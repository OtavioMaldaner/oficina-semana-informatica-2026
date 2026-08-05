from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


@dp.materialized_view(
    name="fifa_world_cup_2026.gold.vw_pontos_recuperados",
    comment=(
        "View analitica com uma linha por selecao e partida para medir pontos "
        "recuperados depois de a equipe ficar em desvantagem. O placar e "
        "reconstruido somente com eventos do tipo Goal; eventos de disputa de "
        "penaltis nao participam do calculo. Como a fonte nao possui segundo nem "
        "periodo do evento, event_id e usado como desempate deterministico para "
        "eventos registrados no mesmo minuto."
    ),
    schema="""
        match_id INT NOT NULL COMMENT 'Identificador da partida.',
        match_date DATE COMMENT 'Data da partida.',
        kickoff_time_utc TIMESTAMP COMMENT 'Horario de inicio da partida em UTC.',
        stage_id INT REFERENCES fifa_world_cup_2026.gold.dim_etapas(stage_id) COMMENT 'Fase do torneio.',
        team_id INT CONSTRAINT fk_vw_pontos_team REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao analisada.',
        team_name STRING COMMENT 'Nome da selecao analisada.',
        opponent_team_id INT CONSTRAINT fk_vw_pontos_opponent_team REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao adversaria.',
        opponent_name STRING COMMENT 'Nome da selecao adversaria.',
        goals_for INT COMMENT 'Gols marcados pela selecao no placar final.',
        goals_against INT COMMENT 'Gols sofridos pela selecao no placar final.',
        actual_points INT COMMENT 'Pontos conquistados no resultado final: 3 por vitoria, 1 por empate e 0 por derrota.',
        was_behind BOOLEAN COMMENT 'True quando a selecao esteve perdendo em algum momento da partida.',
        recovered_points INT COMMENT 'Pontos conquistados em partida na qual a selecao esteve perdendo: 3 na virada, 1 no empate e 0 nos demais casos.'
    """,
)
def vw_pontos_recuperados():
    matches = spark.read.table("fifa_world_cup_2026.gold.ft_partidas").select(
        F.col("match_id").cast("int"),
        F.col("date").cast("date").alias("match_date"),
        F.col("kickoff_time_utc").cast("timestamp"),
        F.col("stage_id").cast("int"),
        F.col("home_team_id").cast("int"),
        F.col("away_team_id").cast("int"),
        F.col("home_score").cast("int"),
        F.col("away_score").cast("int"),
    )

    home_perspective = matches.select(
        "match_id",
        "match_date",
        "kickoff_time_utc",
        "stage_id",
        F.col("home_team_id").alias("team_id"),
        F.col("away_team_id").alias("opponent_team_id"),
        F.col("home_score").alias("goals_for"),
        F.col("away_score").alias("goals_against"),
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
        F.col("away_score").alias("goals_for"),
        F.col("home_score").alias("goals_against"),
        F.when(F.col("away_score") > F.col("home_score"), F.lit(3))
        .when(F.col("away_score") == F.col("home_score"), F.lit(1))
        .otherwise(F.lit(0))
        .cast("int")
        .alias("actual_points"),
    )

    team_matches = home_perspective.unionByName(away_perspective)

    goals = (
        spark.read.table("fifa_world_cup_2026.gold.ft_eventos")
        .filter(F.col("event_type") == F.lit("Goal"))
        .select(
            F.col("event_id").cast("int"),
            F.col("match_id").cast("int"),
            F.col("minute").cast("int"),
            F.col("team_id").cast("int").alias("scoring_team_id"),
        )
    )

    goal_states = (
        team_matches.alias("matches")
        .join(
            goals.alias("goals"),
            F.col("matches.match_id") == F.col("goals.match_id"),
            "inner",
        )
        .select(
            F.col("matches.match_id").alias("match_id"),
            F.col("matches.team_id").alias("team_id"),
            F.col("matches.opponent_team_id").alias("opponent_team_id"),
            F.col("goals.event_id").alias("event_id"),
            F.col("goals.minute").alias("minute"),
            F.when(
                F.col("goals.scoring_team_id") == F.col("matches.team_id"),
                F.lit(1),
            )
            .otherwise(F.lit(0))
            .alias("goal_for_increment"),
            F.when(
                F.col("goals.scoring_team_id")
                == F.col("matches.opponent_team_id"),
                F.lit(1),
            )
            .otherwise(F.lit(0))
            .alias("goal_against_increment"),
        )
    )

    score_window = (
        Window.partitionBy("match_id", "team_id")
        .orderBy(F.col("minute").asc(), F.col("event_id").asc())
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    disadvantages = (
        goal_states.withColumn(
            "running_goals_for",
            F.sum("goal_for_increment").over(score_window),
        )
        .withColumn(
            "running_goals_against",
            F.sum("goal_against_increment").over(score_window),
        )
        .groupBy("match_id", "team_id")
        .agg(
            F.max(
                F.when(
                    F.col("running_goals_for")
                    < F.col("running_goals_against"),
                    F.lit(1),
                ).otherwise(F.lit(0))
            )
            .cast("int")
            .alias("was_behind")
        )
    )

    teams = spark.read.table("fifa_world_cup_2026.gold.dim_selecoes").select(
        F.col("team_id").cast("int"),
        F.col("team_name").cast("string"),
    )

    return (
        team_matches.alias("matches")
        .join(
            disadvantages.alias("disadvantages"),
            (F.col("matches.match_id") == F.col("disadvantages.match_id"))
            & (F.col("matches.team_id") == F.col("disadvantages.team_id")),
            "left",
        )
        .join(
            teams.alias("team"),
            F.col("matches.team_id") == F.col("team.team_id"),
            "left",
        )
        .join(
            teams.alias("opponent"),
            F.col("matches.opponent_team_id") == F.col("opponent.team_id"),
            "left",
        )
        .withColumn(
            "was_behind",
            F.coalesce(F.col("disadvantages.was_behind"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recovered_points",
            F.when(
                F.col("was_behind") == F.lit(1),
                F.col("matches.actual_points"),
            )
            .otherwise(F.lit(0))
            .cast("int"),
        )
        .select(
            F.col("matches.match_id").cast("int").alias("match_id"),
            F.col("matches.match_date").cast("date").alias("match_date"),
            F.col("matches.kickoff_time_utc")
            .cast("timestamp")
            .alias("kickoff_time_utc"),
            F.col("matches.stage_id").cast("int").alias("stage_id"),
            F.col("matches.team_id").cast("int").alias("team_id"),
            F.col("team.team_name").cast("string").alias("team_name"),
            F.col("matches.opponent_team_id")
            .cast("int")
            .alias("opponent_team_id"),
            F.col("opponent.team_name")
            .cast("string")
            .alias("opponent_name"),
            F.col("matches.goals_for").cast("int").alias("goals_for"),
            F.col("matches.goals_against").cast("int").alias("goals_against"),
            F.col("matches.actual_points")
            .cast("int")
            .alias("actual_points"),
            (F.col("was_behind") == F.lit(1)).alias("was_behind"),
            F.col("recovered_points").cast("int").alias("recovered_points"),
        )
    )
