from pyspark import pipelines as dp

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.dim_jogadores",
    comment=(
        "Dimensao granular com o elenco oficial (jogadores convocados) de todas as selecoes. "
        "Regra de negocio: Crucial para responder perguntas sobre o perfil dos atletas (medias de idade, "
        "jogadores mais altos, biotipo) ou para mapear quais clubes mundiais cederam mais jogadores para a Copa."
    ),
    schema="""
        player_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico do atleta.',
        team_id INT REFERENCES fifa_world_cup_2026.gold.dim_selecoes(team_id) COMMENT 'Chave estrangeira que liga o jogador a selecao que ele defende.',
        player_name STRING COMMENT 'Nome do jogador conforme registro oficial.',
        position STRING COMMENT 'Posicao tatica do jogador no campo (ex: GK para goleiro, DF para defensor, MF para meio-campo, FW para atacante).',
        club_team STRING COMMENT 'Clube onde o jogador atua profissionalmente no momento da convocacao (ex: Real Madrid, Manchester City, Grêmio, etc).',
        height_cm INT COMMENT 'Altura do jogador em centimetros. Util para calcular medias de estatura dos times.',
        date_of_birth DATE COMMENT 'Data de nascimento do atleta. Deve ser usada para calcular a idade do jogador na epoca do torneio.'
    """
)
@dp.expect_or_drop("jogador_com_selecao", "team_id IS NOT NULL")
def dim_jogadores():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.squads_and_players")
        .select(
            "player_id",
            "team_id",
            "player_name",
            "position",
            "club_team",
            "height_cm",
            "date_of_birth",
        )
    )