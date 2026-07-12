from pyspark import pipelines as dp

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.dim_estadios",
    comment=(
        "Dimensao geografica e estrutural das sedes da Copa de 2026 (realizada nos EUA, Mexico e Canada). "
        "Regra de negocio: Fundamental para analises de impacto de publico e condicoes fisicas de jogo. "
        "A altitude e um fator critico para o desempenho atletico, enquanto a capacidade dita o potencial de renda e publico."
    ),
    schema="""
        venue_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico do estadio.',
        stadium_name STRING COMMENT 'Nome oficial do estadio sede.',
        city STRING COMMENT 'Cidade onde o estadio esta localizado.',
        country STRING COMMENT 'Pais sede. Valores esperados: USA, Mexico ou Canada.',
        capacity INT COMMENT 'Capacidade maxima oficial de publico (numero de assentos) do estadio.',
        elevation_meters INT COMMENT 'Altitude do estadio em relacao ao nivel do mar (em metros). Fundamental para analisar possivel desgaste fisico dos jogadores.'
    """
)
def dim_estadios():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.venues")
        .select(
            "venue_id",
            "stadium_name",
            "city",
            "country",
            "capacity",
            "elevation_meters",
        )
    )