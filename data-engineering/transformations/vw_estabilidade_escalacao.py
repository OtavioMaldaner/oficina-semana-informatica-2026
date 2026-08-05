from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


@dp.materialized_view(
    name="fifa_world_cup_2026.gold.vw_estabilidade_escalacao",
    comment=(
        "View analitica que compara os titulares de cada selecao com os da sua "
        "partida anterior. A estabilidade e calculada como o numero de titulares "
        "repetidos dividido por 11. A primeira partida de cada selecao nao possui "
        "comparacao anterior e, por isso, recebe valores nulos nas metricas de "
        "repeticao e estabilidade."
    ),
    schema="""
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao analisada.',
        team_name STRING COMMENT 'Nome da selecao analisada.',
        match_id INT REFERENCES fifa_world_cup_2026.gold.ft_partidas(match_id) COMMENT 'Partida atual.',
        previous_match_id INT REFERENCES fifa_world_cup_2026.gold.ft_partidas(match_id) COMMENT 'Partida anterior da mesma selecao.',
        match_date DATE COMMENT 'Data da partida atual.',
        kickoff_time_utc TIMESTAMP COMMENT 'Horario de inicio da partida atual em UTC.',
        stage_id INT REFERENCES fifa_world_cup_2026.gold.dim_etapas(stage_id) COMMENT 'Fase da partida atual.',
        opponent_team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao adversaria na partida atual.',
        opponent_name STRING COMMENT 'Nome da selecao adversaria.',
        starting_players ARRAY<INT> COMMENT 'Conjunto ordenado dos identificadores dos titulares da partida atual.',
        previous_starting_players ARRAY<INT> COMMENT 'Conjunto ordenado dos titulares da partida anterior.',
        starting_xi_count INT COMMENT 'Quantidade de titulares distintos registrados na partida atual.',
        repeated_starters INT COMMENT 'Quantidade de titulares repetidos em relacao a partida anterior.',
        lineup_stability_pct DOUBLE COMMENT 'Percentual de estabilidade da escalacao: titulares repetidos dividido por 11 vezes 100.'
    """,
)
def vw_estabilidade_escalacao():
    lineups = (
        spark.read.table("fifa_world_cup_2026.gold.ft_escalacoes")
        .filter(F.col("is_starting_xi") == F.lit(True))
        .select(
            F.col("match_id").cast("int"),
            F.col("team_id").cast("int"),
            F.col("player_id").cast("int"),
        )
    )

    matches = spark.read.table("fifa_world_cup_2026.gold.ft_partidas").select(
        F.col("match_id").cast("int"),
        F.col("date").cast("date").alias("match_date"),
        F.col("kickoff_time_utc").cast("timestamp"),
        F.col("stage_id").cast("int"),
        F.col("home_team_id").cast("int"),
        F.col("away_team_id").cast("int"),
    )

    starting_lineups = (
        lineups.alias("lineups")
        .join(
            matches.alias("matches"),
            F.col("lineups.match_id") == F.col("matches.match_id"),
            "inner",
        )
        .select(
            F.col("lineups.team_id").alias("team_id"),
            F.col("lineups.match_id").alias("match_id"),
            F.col("matches.match_date").alias("match_date"),
            F.col("matches.kickoff_time_utc").alias("kickoff_time_utc"),
            F.col("matches.stage_id").alias("stage_id"),
            F.when(
                F.col("lineups.team_id") == F.col("matches.home_team_id"),
                F.col("matches.away_team_id"),
            )
            .when(
                F.col("lineups.team_id") == F.col("matches.away_team_id"),
                F.col("matches.home_team_id"),
            )
            .cast("int")
            .alias("opponent_team_id"),
            F.col("lineups.player_id").alias("player_id"),
        )
        .groupBy(
            "team_id",
            "match_id",
            "match_date",
            "kickoff_time_utc",
            "stage_id",
            "opponent_team_id",
        )
        .agg(
            F.sort_array(F.collect_set("player_id")).alias("starting_players")
        )
        .withColumn(
            "starting_xi_count",
            F.size("starting_players").cast("int"),
        )
    )

    match_sequence_window = Window.partitionBy("team_id").orderBy(
        F.col("match_date").asc(),
        F.col("kickoff_time_utc").asc_nulls_last(),
        F.col("match_id").asc(),
    )

    compared_lineups = (
        starting_lineups.withColumn(
            "previous_match_id",
            F.lag("match_id").over(match_sequence_window).cast("int"),
        )
        .withColumn(
            "previous_starting_players",
            F.lag("starting_players").over(match_sequence_window),
        )
        .withColumn(
            "repeated_starters",
            F.when(
                F.col("previous_starting_players").isNull(),
                F.lit(None).cast("int"),
            )
            .otherwise(
                F.size(
                    F.array_intersect(
                        F.col("starting_players"),
                        F.col("previous_starting_players"),
                    )
                ).cast("int")
            )
            .cast("int"),
        )
        .withColumn(
            "lineup_stability_pct",
            F.when(
                F.col("previous_starting_players").isNull(),
                F.lit(None).cast("double"),
            )
            .otherwise(
                F.col("repeated_starters").cast("double")
                * F.lit(100.0)
                / F.lit(11.0)
            )
            .cast("double"),
        )
    )

    teams = spark.read.table("fifa_world_cup_2026.gold.dim_selecoes").select(
        F.col("team_id").cast("int"),
        F.col("team_name").cast("string"),
    )

    return (
        compared_lineups.alias("lineups")
        .join(
            teams.alias("team"),
            F.col("lineups.team_id") == F.col("team.team_id"),
            "left",
        )
        .join(
            teams.alias("opponent"),
            F.col("lineups.opponent_team_id") == F.col("opponent.team_id"),
            "left",
        )
        .select(
            F.col("lineups.team_id").cast("int").alias("team_id"),
            F.col("team.team_name").cast("string").alias("team_name"),
            F.col("lineups.match_id").cast("int").alias("match_id"),
            F.col("lineups.previous_match_id")
            .cast("int")
            .alias("previous_match_id"),
            F.col("lineups.match_date").cast("date").alias("match_date"),
            F.col("lineups.kickoff_time_utc")
            .cast("timestamp")
            .alias("kickoff_time_utc"),
            F.col("lineups.stage_id").cast("int").alias("stage_id"),
            F.col("lineups.opponent_team_id")
            .cast("int")
            .alias("opponent_team_id"),
            F.col("opponent.team_name")
            .cast("string")
            .alias("opponent_name"),
            F.col("lineups.starting_players").alias("starting_players"),
            F.col("lineups.previous_starting_players").alias(
                "previous_starting_players"
            ),
            F.col("lineups.starting_xi_count")
            .cast("int")
            .alias("starting_xi_count"),
            F.col("lineups.repeated_starters")
            .cast("int")
            .alias("repeated_starters"),
            F.col("lineups.lineup_stability_pct")
            .cast("double")
            .alias("lineup_stability_pct"),
        )
    )
