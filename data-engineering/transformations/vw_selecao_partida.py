"""
Camada GOLD — view analitica com uma linha por selecao e partida.

A view normaliza o modelo mandante/visitante de ft_partidas para facilitar
metricas por selecao no Databricks Genie. Cada partida gera duas linhas:
uma pela perspectiva do mandante e outra pela perspectiva do visitante.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="fifa_world_cup_2026.gold.vw_selecao_partida",
    comment=(
        "View analitica com granularidade de uma linha por selecao e partida. "
        "Normaliza os campos de mandante e visitante em team_id e "
        "opponent_team_id, permitindo calcular gols, xG, pontos e resultados "
        "sem filtrar separadamente home_team_id e away_team_id. Em partidas "
        "decididas nos penaltis, points e result consideram o placar antes da "
        "disputa, conforme os campos home_score e away_score de ft_partidas. "
        "team_role representa somente o papel cadastrado como HOME ou AWAY e "
        "nao implica vantagem de mando em uma competicao disputada em sedes."
    ),
    schema="""
        match_id INT NOT NULL REFERENCES fifa_world_cup_2026.gold.ft_partidas(match_id) COMMENT 'Identificador da partida.',
        match_date DATE COMMENT 'Data da partida.',
        kickoff_time_utc TIMESTAMP COMMENT 'Horario de inicio da partida em UTC.',
        stage_id INT REFERENCES fifa_world_cup_2026.gold.dim_etapas(stage_id) COMMENT 'Fase do torneio.',
        venue_id INT REFERENCES fifa_world_cup_2026.gold.dim_estadios(venue_id) COMMENT 'Estadio da partida.',
        referee_id INT REFERENCES fifa_world_cup_2026.gold.dim_arbitros(referee_id) COMMENT 'Arbitro principal da partida.',
        team_id INT NOT NULL CONSTRAINT fk_vw_selecao_team REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao analisada.',
        team_name STRING COMMENT 'Nome da selecao analisada.',
        fifa_code STRING COMMENT 'Codigo FIFA de tres letras da selecao analisada.',
        team_rank INT COMMENT 'Posicao da selecao no ranking FIFA anterior ao torneio; valores menores indicam equipes mais bem ranqueadas.',
        opponent_team_id INT NOT NULL CONSTRAINT fk_vw_selecao_opponent_team REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Selecao adversaria.',
        opponent_name STRING COMMENT 'Nome da selecao adversaria.',
        opponent_fifa_code STRING COMMENT 'Codigo FIFA de tres letras da selecao adversaria.',
        opponent_rank INT COMMENT 'Posicao do adversario no ranking FIFA anterior ao torneio.',
        goals_for INT COMMENT 'Gols marcados pela selecao, sem incluir a disputa por penaltis.',
        goals_against INT COMMENT 'Gols sofridos pela selecao, sem incluir a disputa por penaltis.',
        xg_for DOUBLE COMMENT 'Expected Goals produzido pela selecao na partida.',
        xg_against DOUBLE COMMENT 'Expected Goals produzido pelo adversario na partida.',
        points INT COMMENT 'Pontos obtidos pelo placar: 3 por vitoria, 1 por empate e 0 por derrota.',
        result STRING COMMENT 'Resultado da selecao pelo placar: WIN, DRAW ou LOSS.',
        team_role STRING COMMENT 'Papel cadastrado na partida: HOME para mandante ou AWAY para visitante.'
    """,
)
@dp.expect_or_drop(
    "selecoes_distintas",
    "team_id IS NOT NULL AND opponent_team_id IS NOT NULL AND team_id <> opponent_team_id",
)
@dp.expect_or_drop(
    "pontuacao_valida",
    "points IN (0, 1, 3)",
)
def vw_selecao_partida():
    matches = dp.read("ft_partidas").select(
        F.col("match_id").cast("int"),
        F.col("date").cast("date").alias("match_date"),
        F.col("kickoff_time_utc").cast("timestamp"),
        F.col("stage_id").cast("int"),
        F.col("venue_id").cast("int"),
        F.col("referee_id").cast("int"),
        F.col("home_team_id").cast("int"),
        F.col("away_team_id").cast("int"),
        F.col("home_score").cast("int"),
        F.col("away_score").cast("int"),
        F.col("home_xg").cast("double"),
        F.col("away_xg").cast("double"),
    )

    home_perspective = matches.select(
        "match_id",
        "match_date",
        "kickoff_time_utc",
        "stage_id",
        "venue_id",
        "referee_id",
        F.col("home_team_id").alias("team_id"),
        F.col("away_team_id").alias("opponent_team_id"),
        F.col("home_score").alias("goals_for"),
        F.col("away_score").alias("goals_against"),
        F.col("home_xg").alias("xg_for"),
        F.col("away_xg").alias("xg_against"),
        F.when(F.col("home_score") > F.col("away_score"), F.lit(3))
        .when(F.col("home_score") == F.col("away_score"), F.lit(1))
        .otherwise(F.lit(0))
        .cast("int")
        .alias("points"),
        F.when(F.col("home_score") > F.col("away_score"), F.lit("WIN"))
        .when(F.col("home_score") == F.col("away_score"), F.lit("DRAW"))
        .otherwise(F.lit("LOSS"))
        .alias("result"),
        F.lit("HOME").alias("team_role"),
    )

    away_perspective = matches.select(
        "match_id",
        "match_date",
        "kickoff_time_utc",
        "stage_id",
        "venue_id",
        "referee_id",
        F.col("away_team_id").alias("team_id"),
        F.col("home_team_id").alias("opponent_team_id"),
        F.col("away_score").alias("goals_for"),
        F.col("home_score").alias("goals_against"),
        F.col("away_xg").alias("xg_for"),
        F.col("home_xg").alias("xg_against"),
        F.when(F.col("away_score") > F.col("home_score"), F.lit(3))
        .when(F.col("away_score") == F.col("home_score"), F.lit(1))
        .otherwise(F.lit(0))
        .cast("int")
        .alias("points"),
        F.when(F.col("away_score") > F.col("home_score"), F.lit("WIN"))
        .when(F.col("away_score") == F.col("home_score"), F.lit("DRAW"))
        .otherwise(F.lit("LOSS"))
        .alias("result"),
        F.lit("AWAY").alias("team_role"),
    )

    team_matches = home_perspective.unionByName(away_perspective)

    teams = dp.read("dim_selecoes").select(
        F.col("team_id").cast("int"),
        F.col("team_name").cast("string"),
        F.col("fifa_code").cast("string"),
        F.col("fifa_ranking_pre_tournament").cast("int"),
    )

    return (
        team_matches.alias("matches")
        .join(
            teams.alias("team"),
            F.col("matches.team_id") == F.col("team.team_id"),
            "inner",
        )
        .join(
            teams.alias("opponent"),
            F.col("matches.opponent_team_id") == F.col("opponent.team_id"),
            "inner",
        )
        .select(
            F.col("matches.match_id").cast("int").alias("match_id"),
            F.col("matches.match_date").cast("date").alias("match_date"),
            F.col("matches.kickoff_time_utc")
            .cast("timestamp")
            .alias("kickoff_time_utc"),
            F.col("matches.stage_id").cast("int").alias("stage_id"),
            F.col("matches.venue_id").cast("int").alias("venue_id"),
            F.col("matches.referee_id").cast("int").alias("referee_id"),
            F.col("matches.team_id").cast("int").alias("team_id"),
            F.col("team.team_name").cast("string").alias("team_name"),
            F.col("team.fifa_code").cast("string").alias("fifa_code"),
            F.col("team.fifa_ranking_pre_tournament")
            .cast("int")
            .alias("team_rank"),
            F.col("matches.opponent_team_id")
            .cast("int")
            .alias("opponent_team_id"),
            F.col("opponent.team_name")
            .cast("string")
            .alias("opponent_name"),
            F.col("opponent.fifa_code")
            .cast("string")
            .alias("opponent_fifa_code"),
            F.col("opponent.fifa_ranking_pre_tournament")
            .cast("int")
            .alias("opponent_rank"),
            F.col("matches.goals_for").cast("int").alias("goals_for"),
            F.col("matches.goals_against")
            .cast("int")
            .alias("goals_against"),
            F.col("matches.xg_for").cast("double").alias("xg_for"),
            F.col("matches.xg_against")
            .cast("double")
            .alias("xg_against"),
            F.col("matches.points").cast("int").alias("points"),
            F.col("matches.result").cast("string").alias("result"),
            F.col("matches.team_role").cast("string").alias("team_role"),
        )
    )
