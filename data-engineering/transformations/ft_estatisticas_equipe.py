from pyspark import pipelines as dp

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.ft_estatisticas_equipe",
    comment=(
        "Tabela Fato com as estatisticas de desempenho de cada selecao em cada partida "
        "(posse de bola, finalizacoes, escanteios, faltas, impedimentos e defesas). "
        "Regra de negocio: Granularidade de duas linhas por partida (uma para o time mandante "
        "e uma para o visitante). Complementa o placar bruto de ft_partidas com o 'como' do jogo, "
        "permitindo perguntas como 'qual selecao teve mais posse de bola no torneio?' ou "
        "'quem teve mais finalizacoes por gol marcado (eficiencia)?'."
    ),
    schema="""
        match_id INT REFERENCES fifa_world_cup_2026.gold.ft_partidas(match_id) COMMENT 'Chave estrangeira para a partida.',
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira para a selecao a que as estatisticas pertencem.',
        possession_pct DOUBLE COMMENT 'Percentual de posse de bola da selecao na partida (0 a 100).',
        total_shots INT COMMENT 'Numero total de finalizacoes (chutes a gol ou para fora) realizadas pela selecao.',
        shots_on_target INT COMMENT 'Numero de finalizacoes no alvo (que exigiram defesa do goleiro adversario ou resultaram em gol).',
        corners INT COMMENT 'Numero de escanteios cobrados pela selecao.',
        fouls INT COMMENT 'Numero de faltas cometidas pela selecao.',
        offsides INT COMMENT 'Numero de vezes que a selecao ficou em posicao de impedimento.',
        saves INT COMMENT 'Numero de defesas realizadas pelo goleiro da selecao.',
        player_of_the_match STRING COMMENT 'Nome do jogador eleito o melhor em campo, quando a selecao teve o premiado (pode ser nulo).',
        data_source STRING COMMENT 'Fonte de onde a estatistica foi coletada (ex: fifa.com).',
        last_updated DATE COMMENT 'Data da ultima atualizacao deste registro na fonte original.',
        PRIMARY KEY (match_id, team_id)
    """
)
def ft_estatisticas_equipe():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.match_team_stats")
        .select(
            "match_id",
            "team_id",
            "possession_pct",
            "total_shots",
            "shots_on_target",
            "corners",
            "fouls",
            "offsides",
            "saves",
            "player_of_the_match",
            "data_source",
            "last_updated",
        )
    )