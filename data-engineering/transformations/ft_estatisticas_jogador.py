from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.ft_estatisticas_jogador",
    comment=(
        "Tabela Fato com as estatisticas individuais acumuladas de cada jogador ao longo de todo o torneio. "
        "Regra de negocio: Granularidade de uma linha por jogador (agregado do campeonato, e nao por partida). "
        "Use esta tabela para rankings do torneio (artilharia, assistencias, media de nota) e junte com "
        "dim_jogadores (mesma chave player_id) para obter nome, selecao, clube e demais atributos do atleta."
    ),
    schema="""
        player_id INT NOT NULL PRIMARY KEY COMMENT 'Chave estrangeira/primaria para o jogador (uma linha por jogador no torneio).',
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira para a selecao do jogador.',
        position STRING COMMENT 'Posicao do jogador (GK, DEF, MID, FWD) conforme reportada nesta fonte de estatisticas.',
        matches_played INT COMMENT 'Numero de partidas em que o jogador entrou em campo no torneio.',
        matches_started INT COMMENT 'Numero de partidas em que o jogador foi titular.',
        minutes_played INT COMMENT 'Total de minutos jogados pelo atleta no torneio.',
        goals INT COMMENT 'Total de gols marcados pelo jogador no torneio (artilharia).',
        assists INT COMMENT 'Total de assistencias para gol dadas pelo jogador no torneio.',
        shots INT COMMENT 'Total de finalizacoes tentadas pelo jogador no torneio.',
        shots_on_target INT COMMENT 'Total de finalizacoes no alvo feitas pelo jogador no torneio.',
        yellow_cards INT COMMENT 'Total de cartoes amarelos recebidos pelo jogador no torneio.',
        red_cards INT COMMENT 'Total de cartoes vermelhos recebidos pelo jogador no torneio.',
        penalty_goals INT COMMENT 'Total de gols marcados de penalti pelo jogador.',
        own_goals INT COMMENT 'Total de gols contra marcados pelo jogador.',
        clean_sheets INT COMMENT 'Numero de jogos em que o jogador (tipicamente goleiro ou defensor) nao sofreu gols. Aplicavel principalmente a goleiros.',
        saves INT COMMENT 'Total de defesas realizadas pelo jogador. Aplicavel principalmente a goleiros.',
        goals_conceded INT COMMENT 'Total de gols sofridos enquanto o jogador estava em campo. Aplicavel principalmente a goleiros.',
        average_rating DOUBLE COMMENT 'Nota media de desempenho do jogador no torneio, atribuida pela fonte de dados (escala tipica 0-10).',
        data_source STRING COMMENT 'Fonte de onde a estatistica foi coletada (ex: sofascore.com).',
        last_verified DATE COMMENT 'Data em que esta estatistica foi verificada/atualizada pela ultima vez pela fonte.'
    """
)
def ft_estatisticas_jogador():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.player_stats")
        .select(
            F.col("player_id").cast("int"),
            F.col("team_id").cast("int"),
            F.col("position").cast("string"),
            F.col("matches_played").cast("int"),
            F.col("matches_started").cast("int"),
            F.col("minutes_played").cast("int"),
            F.col("goals").cast("int"),
            F.col("assists").cast("int"),
            F.col("shots").cast("int"),
            F.col("shots_on_target").cast("int"),
            F.col("yellow_cards").cast("int"),
            F.col("red_cards").cast("int"),
            F.col("penalty_goals").cast("int"),
            F.col("own_goals").cast("int"),
            F.col("clean_sheets").cast("int"),
            F.col("saves").cast("int"),
            F.col("goals_conceded").cast("int"),
            F.col("average_rating").cast("double"),
            F.col("data_source").cast("string"),
            F.col("last_verified").cast("date"),
        )
    )