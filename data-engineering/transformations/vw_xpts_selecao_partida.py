from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.view(
    name="vw_xpts_selecao_partida",
    comment=(
        "View analitica com pontos esperados por selecao e partida. O modelo "
        "considera os gols de cada equipe como variaveis de Poisson independentes, "
        "usando xG a favor e xG contra como medias. Sao avaliados placares de 0 a "
        "10 gols para cada lado e as probabilidades sao renormalizadas pela massa "
        "retida nesse intervalo. xPts nao e uma metrica oficial da FIFA."
    ),
    schema="""
        match_id INT NOT NULL COMMENT 'Identificador da partida.',
        match_date DATE COMMENT 'Data da partida.',
        kickoff_time_utc TIMESTAMP COMMENT 'Horario de inicio da partida em UTC.',
        stage_id INT REFERENCES fifa_world_cup_2026.gold.dim_etapas(stage_id) COMMENT 'Fase do torneio.',
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao analisada.',
        team_name STRING COMMENT 'Nome da selecao analisada.',
        opponent_team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao adversaria.',
        opponent_name STRING COMMENT 'Nome da selecao adversaria.',
        xg_for DOUBLE COMMENT 'Expected Goals produzido pela selecao na partida.',
        xg_against DOUBLE COMMENT 'Expected Goals produzido pelo adversario na partida.',
        actual_points INT COMMENT 'Pontos reais conquistados: 3 por vitoria, 1 por empate e 0 por derrota.',
        win_probability DOUBLE COMMENT 'Probabilidade estimada de vitoria pelo modelo de Poisson, entre 0 e 1.',
        draw_probability DOUBLE COMMENT 'Probabilidade estimada de empate pelo modelo de Poisson, entre 0 e 1.',
        loss_probability DOUBLE COMMENT 'Probabilidade estimada de derrota pelo modelo de Poisson, entre 0 e 1.',
        expected_points DOUBLE COMMENT 'Pontos esperados: 3 vezes a probabilidade de vitoria mais a probabilidade de empate.',
        points_above_expected DOUBLE COMMENT 'Pontos reais menos pontos esperados.',
        probability_mass_0_to_10 DOUBLE COMMENT 'Massa de probabilidade capturada pelos placares de 0 a 10 antes da renormalizacao.'
    """,
)
def vw_xpts_selecao_partida():
    matches = (
        spark.read.table("fifa_world_cup_2026.gold.ft_partidas")
        .select(
            F.col("match_id").cast("int"),
            F.col("date").cast("date").alias("match_date"),
            F.col("kickoff_time_utc").cast("timestamp"),
            F.col("stage_id").cast("int"),
            F.col("home_team_id").cast("int"),
            F.col("away_team_id").cast("int"),
            F.col("home_score").cast("int"),
            F.col("away_score").cast("int"),
            F.col("home_xg").cast("double"),
            F.col("away_xg").cast("double"),
        )
        .filter(F.col("home_xg").isNotNull() & F.col("away_xg").isNotNull())
    )

    home_perspective = matches.select(
        "match_id",
        "match_date",
        "kickoff_time_utc",
        "stage_id",
        F.col("home_team_id").alias("team_id"),
        F.col("away_team_id").alias("opponent_team_id"),
        F.col("home_xg").alias("xg_for"),
        F.col("away_xg").alias("xg_against"),
        F.when(F.col("home_score") > F.col("away_score"), F.lit(3))
        .when(F.col("home_score") == F.col("away_score"), F.lit(1))
        .otherwise(F.lit(0))
        .cast("int")
        .alias("actual_points"),
    )

    away_perspective = matches.select(
        "match_id",
        "match_date",
        "kickoff_time_utc",
        "stage_id",
        F.col("away_team_id").alias("team_id"),
        F.col("home_team_id").alias("opponent_team_id"),
        F.col("away_xg").alias("xg_for"),
        F.col("home_xg").alias("xg_against"),
        F.when(F.col("away_score") > F.col("home_score"), F.lit(3))
        .when(F.col("away_score") == F.col("home_score"), F.lit(1))
        .otherwise(F.lit(0))
        .cast("int")
        .alias("actual_points"),
    )

    team_matches = home_perspective.unionByName(away_perspective)

    modeled_goals_for = spark.range(0, 11).select(
        F.col("id").cast("int").alias("modeled_goals_for")
    )
    modeled_goals_against = spark.range(0, 11).select(
        F.col("id").cast("int").alias("modeled_goals_against")
    )

    scorelines = team_matches.crossJoin(modeled_goals_for).crossJoin(
        modeled_goals_against
    )

    poisson_for = (
        F.exp(-F.col("xg_for"))
        * F.pow(F.col("xg_for"), F.col("modeled_goals_for"))
        / F.factorial(F.col("modeled_goals_for")).cast("double")
    )
    poisson_against = (
        F.exp(-F.col("xg_against"))
        * F.pow(F.col("xg_against"), F.col("modeled_goals_against"))
        / F.factorial(F.col("modeled_goals_against")).cast("double")
    )

    outcome_probabilities = scorelines.withColumn(
        "joint_probability",
        (poisson_for * poisson_against).cast("double"),
    )

    grouped_probabilities = outcome_probabilities.groupBy(
        "match_id",
        "match_date",
        "kickoff_time_utc",
        "stage_id",
        "team_id",
        "opponent_team_id",
        "xg_for",
        "xg_against",
        "actual_points",
    ).agg(
        F.sum("joint_probability")
        .cast("double")
        .alias("probability_mass_0_to_10"),
        F.sum(
            F.when(
                F.col("modeled_goals_for") > F.col("modeled_goals_against"),
                F.col("joint_probability"),
            ).otherwise(F.lit(0.0))
        )
        .cast("double")
        .alias("raw_win_probability"),
        F.sum(
            F.when(
                F.col("modeled_goals_for") == F.col("modeled_goals_against"),
                F.col("joint_probability"),
            ).otherwise(F.lit(0.0))
        )
        .cast("double")
        .alias("raw_draw_probability"),
        F.sum(
            F.when(
                F.col("modeled_goals_for") < F.col("modeled_goals_against"),
                F.col("joint_probability"),
            ).otherwise(F.lit(0.0))
        )
        .cast("double")
        .alias("raw_loss_probability"),
    )

    metrics = (
        grouped_probabilities.withColumn(
            "win_probability",
            F.col("raw_win_probability")
            / F.col("probability_mass_0_to_10"),
        )
        .withColumn(
            "draw_probability",
            F.col("raw_draw_probability")
            / F.col("probability_mass_0_to_10"),
        )
        .withColumn(
            "loss_probability",
            F.col("raw_loss_probability")
            / F.col("probability_mass_0_to_10"),
        )
        .withColumn(
            "expected_points",
            (
                F.lit(3.0) * F.col("raw_win_probability")
                + F.col("raw_draw_probability")
            )
            / F.col("probability_mass_0_to_10"),
        )
        .withColumn(
            "points_above_expected",
            F.col("actual_points").cast("double") - F.col("expected_points"),
        )
    )

    teams = spark.read.table("fifa_world_cup_2026.gold.dim_selecoes").select(
        F.col("team_id").cast("int"),
        F.col("team_name").cast("string"),
    )

    return (
        metrics.alias("metrics")
        .join(
            teams.alias("team"),
            F.col("metrics.team_id") == F.col("team.team_id"),
            "left",
        )
        .join(
            teams.alias("opponent"),
            F.col("metrics.opponent_team_id") == F.col("opponent.team_id"),
            "left",
        )
        .select(
            F.col("metrics.match_id").cast("int").alias("match_id"),
            F.col("metrics.match_date").cast("date").alias("match_date"),
            F.col("metrics.kickoff_time_utc")
            .cast("timestamp")
            .alias("kickoff_time_utc"),
            F.col("metrics.stage_id").cast("int").alias("stage_id"),
            F.col("metrics.team_id").cast("int").alias("team_id"),
            F.col("team.team_name").cast("string").alias("team_name"),
            F.col("metrics.opponent_team_id")
            .cast("int")
            .alias("opponent_team_id"),
            F.col("opponent.team_name")
            .cast("string")
            .alias("opponent_name"),
            F.col("metrics.xg_for").cast("double").alias("xg_for"),
            F.col("metrics.xg_against").cast("double").alias("xg_against"),
            F.col("metrics.actual_points")
            .cast("int")
            .alias("actual_points"),
            F.col("metrics.win_probability")
            .cast("double")
            .alias("win_probability"),
            F.col("metrics.draw_probability")
            .cast("double")
            .alias("draw_probability"),
            F.col("metrics.loss_probability")
            .cast("double")
            .alias("loss_probability"),
            F.col("metrics.expected_points")
            .cast("double")
            .alias("expected_points"),
            F.col("metrics.points_above_expected")
            .cast("double")
            .alias("points_above_expected"),
            F.col("metrics.probability_mass_0_to_10")
            .cast("double")
            .alias("probability_mass_0_to_10"),
        )
    )
