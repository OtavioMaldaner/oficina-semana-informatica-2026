from pyspark import pipelines as dp

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.dim_etapas",
    comment=(
        "Dimensao que mapeia a estrutura temporal e as fases do torneio. "
        "Regra de negocio: A Copa de 2026 introduz a fase de 16-avos de final (Round of 32) devido "
        "ao aumento para 48 times. Esta tabela permite filtrar partidas entre fase de grupos (pontos corridos) "
        "e fases eliminatorias (mata-mata)."
    ),
    schema="""
        stage_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico da fase do torneio.',
        stage_name STRING COMMENT 'Nome da fase (ex: Group Stage, Round of 32, Round of 16, Quarter-finals, Semi-finals, Final).',
        is_knockout BOOLEAN COMMENT 'Flag indicadora. True = fase eliminatoria (mata-mata onde quem perde e eliminado). False = fase de grupos.'
    """
)
def dim_etapas():
    return spark.read.table("fifa_world_cup_2026.bronze.tournament_stages")