from pyspark import pipelines as dp

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.dim_arbitros",
    comment=(
        "Dimensao com os arbitros principais que apitam partidas da Copa de 2026. "
        "Regra de negocio: Permite analisar o rigor de arbitragem (media de cartoes por jogo) "
        "e cruzar com o resultado das partidas para identificar possiveis correlacoes entre "
        "arbitro e numero de cartoes/faltas em uma partida."
    ),
    schema="""
        referee_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico do arbitro.',
        referee_name STRING COMMENT 'Nome completo do arbitro principal.',
        country STRING COMMENT 'Pais de origem/federacao do arbitro.',
        avg_cards_per_game DOUBLE COMMENT 'Media historica de cartoes (amarelos + vermelhos) mostrados por partida por este arbitro. Indicador do "rigor" do arbitro.'
    """
)
def dim_arbitros():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.referees")
        .selectExpr(
            "referee_id",
            "name AS referee_name",
            "country",
            "avg_cards_per_game",
        )
    )