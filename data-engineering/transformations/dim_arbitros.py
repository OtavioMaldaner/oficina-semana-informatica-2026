from pyspark import pipelines as dp
from pyspark.sql import functions as F

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
        country STRING COMMENT 'Pais de origem/federacao do arbitro.'
    """
)
def dim_arbitros():
    return spark.read.table("fifa_world_cup_2026.bronze.referees").select(
        "referee_id",
        F.col("name").alias("referee_name"),
        "country",
    )