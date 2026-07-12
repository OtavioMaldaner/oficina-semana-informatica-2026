from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.ft_eventos",
    comment=(
        "Tabela Fato de eventos ocorridos dentro das partidas (gols, assistencias, cartoes e revisoes de VAR). "
        "Regra de negocio: Granularidade de uma linha por evento. Permite reconstruir a linha do tempo de "
        "qualquer partida (ex: 'em que minuto o Brasil tomou cartao amarelo?') e calcular metricas de disciplina "
        "e de ritmo de jogo (gols por faixa de minuto, cartoes por selecao, etc)."
    ),
    schema="""
        event_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico do evento.',
        match_id INT REFERENCES fifa_world_cup_2026.gold.ft_partidas(match_id) COMMENT 'Chave estrangeira para a partida em que o evento ocorreu.',
        minute INT COMMENT 'Minuto de jogo em que o evento aconteceu (pode ultrapassar 90 em caso de acrescimos/prorrogacao).',
        event_type STRING COMMENT 'Tipo do evento. Valores possiveis: Goal, Assist, Yellow Card, Red Card, VAR Review, Penalty Shootout Goal, Penalty Shootout Miss.',
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira para a selecao envolvida no evento.',
        player_id INT REFERENCES fifa_world_cup_2026.gold.dim_jogadores(player_id) COMMENT 'Chave estrangeira para o jogador envolvido no evento.'
    """
)
def ft_eventos():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.match_events")
        .select(
            F.col("event_id").cast("int"),
            F.col("match_id").cast("int"),
            F.col("minute").cast("int"),
            F.col("event_type").cast("string"),
            F.col("team_id").cast("int"),
            F.col("player_id").cast("int"),
        )
    )