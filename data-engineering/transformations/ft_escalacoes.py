from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.ft_escalacoes",
    comment=(
        "Tabela Fato de escalacoes (lineups) das partidas. "
        "Regra de negocio: Granularidade de uma linha por jogador convocado para cada partida "
        "(titular ou reserva). Fundamental para responder perguntas sobre quem comecou jogando, "
        "tempo de jogo por atleta e para calcular a formacao tatica de cada selecao em cada partida."
    ),
    schema="""
        lineup_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico do registro de escalacao.',
        match_id INT REFERENCES fifa_world_cup_2026.gold.ft_partidas(match_id) COMMENT 'Chave estrangeira para a partida.',
        player_id INT REFERENCES fifa_world_cup_2026.gold.dim_jogadores(player_id) COMMENT 'Chave estrangeira para o jogador escalado.',
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira para a selecao do jogador nesta partida.',
        is_starting_xi BOOLEAN COMMENT 'Flag indicadora. True = jogador comecou a partida no time titular. False = jogador ficou no banco de reservas (podendo ou nao ter entrado depois).',
        tactical_position STRING COMMENT 'Posicao tatica ocupada pelo jogador nesta partida especifica (GK, DEF, MID, FWD). Pode diferir da posicao padrao do jogador em dim_jogadores.',
        minutes_played INT COMMENT 'Quantidade de minutos que o jogador efetivamente atuou nesta partida.'
    """
)
def ft_escalacoes():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.match_lineups")
        .select(
            "lineup_id",
            "match_id",
            "player_id",
            "team_id",
            F.col("is_starting_xi").cast("boolean").alias("is_starting_xi"),
            "tactical_position",
            "minutes_played",
        )
    )