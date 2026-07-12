"""
Camada GOLD — fatos do star schema da Copa do Mundo 2026.

Contem a tabela fato principal com as metricas dos jogos e uma view 
achatada (desnormalizada) enriquecida com metadados para otimizar as
respostas de IA no Databricks Genie e facilitar a criacao de dashboards.
"""
from pyspark import pipelines as dp
from pyspark.sql import functions as F


@dp.materialized_view(
    name="fifa_world_cup_2026.gold.ft_partidas",
    comment=(
        "Tabela Fato de partidas da Copa do Mundo 2026. "
        "Regra de negocio: Granularidade de uma linha por jogo. Contem os placares oficiais "
        "e metricas avancadas de desempenho, como o xG (Expected Goals). Utiliza um modelo de "
        "dimensao de papel duplo (role-playing dimension) onde a dimensao de selecoes e "
        "referenciada duas vezes: uma para o time mandante e outra para o visitante."
    ),
    schema="""
        match_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico da partida.',
        date DATE COMMENT 'Data em que o jogo foi realizado.',
        kickoff_time_utc TIMESTAMP COMMENT 'Horario exato do apito inicial, padronizado em fuso UTC.',
        stage_id INT REFERENCES fifa_world_cup_2026.gold.dim_etapas(stage_id) COMMENT 'Chave estrangeira para a fase do torneio.',
        venue_id INT REFERENCES fifa_world_cup_2026.gold.dim_estadios(venue_id) COMMENT 'Chave estrangeira para o estadio onde ocorreu o jogo.',
        home_team_id INT CONSTRAINT fk_home_team REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira para a selecao mandante (time da casa).',
        away_team_id INT CONSTRAINT fk_away_team REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira para a selecao visitante (time de fora).',
        home_score INT COMMENT 'Quantidade de gols marcados pela selecao mandante durante o tempo regulamentar/prorrogacao.',
        away_score INT COMMENT 'Quantidade de gols marcados pela selecao visitante.',
        home_xg DOUBLE COMMENT 'Expected Goals (Gols Esperados) do mandante. Metrica avancada que mede a qualidade e probabilidade das chances de gol criadas.',
        away_xg DOUBLE COMMENT 'Expected Goals (Gols Esperados) do visitante.',
        referee_id INT COMMENT 'Identificador do arbitro principal da partida.',
        status STRING COMMENT 'Status atual do jogo (ex: Completed, In Play, Scheduled).'
    """
)
@dp.expect_or_drop(
    "placar_registrado", "home_score IS NOT NULL AND away_score IS NOT NULL"
)
def ft_partidas():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.matches")
        .select(
            "match_id",
            "date",
            "kickoff_time_utc",
            "stage_id",
            "venue_id",
            "home_team_id",
            "away_team_id",
            "home_score",
            "away_score",
            "home_xg",
            "away_xg",
            "referee_id",
            "status",
        )
    )