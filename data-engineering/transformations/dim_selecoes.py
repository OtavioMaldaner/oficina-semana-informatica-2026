from pyspark import pipelines as dp

@dp.materialized_view(
    name="fifa_world_cup_2026.gold.dim_selecoes",
    comment=(
        "Dimensao contendo as selecoes nacionais de futebol classificadas para a Copa do Mundo 2026. "
        "Regra de negocio: Esta tabela e o eixo principal para qualquer metrica agregada por pais. "
        "Contem o ranking pre-torneio (indicador de favoritismo) e a distribuicao das equipes "
        "em seus respectivos grupos e confederacoes continentais."
    ),
    schema="""
        team_id INT NOT NULL PRIMARY KEY COMMENT 'Identificador unico numerico da selecao.',
        team_name STRING COMMENT 'Nome oficial do pais/selecao em ingles (ex: Brazil, Argentina).',
        fifa_code STRING COMMENT 'Codigo de 3 letras da FIFA (ex: BRA, ARG). Util para unioes com fontes externas.',
        group_letter STRING COMMENT 'Letra do grupo na primeira fase (A ao L, contemplando os 48 times de 2026).',
        confederation STRING COMMENT 'Confederacao continental a qual o pais pertence (ex: CONMEBOL, UEFA, CONCACAF).',
        fifa_ranking_pre_tournament INT COMMENT 'Posicao da selecao no ranking mundial da FIFA antes do inicio da Copa. Valores menores indicam times mais fortes (1 = melhor do mundo).'
    """
)
def dim_selecoes():
    return (
        spark.read.table("fifa_world_cup_2026.bronze.teams")
        .select(
            "team_id",
            "team_name",
            "fifa_code",
            "group_letter",
            "confederation",
            "fifa_ranking_pre_tournament",
        )
    )
