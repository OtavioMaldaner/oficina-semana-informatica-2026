"""
Camada BRONZE — ingestao bruta dos CSVs da Copa do Mundo 2026.

Fonte: Volume fifa_world_cup_2026.raw_data.bronze
(ou seja, os arquivos ja foram enviados manualmente para esse Volume
antes de rodar a pipeline — a Free Edition nao libera download direto
de dentro do notebook).

Cada funcao aqui so le o CSV e materializa como tabela Delta, sem
transformar nada. Isso separa "os dados chegaram" de "os dados fazem
sentido", que e o proposito da camada bronze na Arquitetura Medallion.
"""
from pyspark import pipelines as dp

VOLUME_PATH = "/Volumes/fifa_world_cup_2026/raw_data/bronze"

# nome do arquivo (sem .csv) -> descricao usada no COMMENT da tabela
RAW_FILES = {
    "teams": "Selecoes participantes",
    "venues": "Estadios sede",
    "tournament_stages": "Fases do torneio",
    "referees": "Arbitros",
    "matches": "Partidas",
    "squads_and_players": "Elenco e jogadores",
    "match_events": "Eventos das partidas",
    "match_lineups": "Escalacoes das partidas",
    "match_prediction_features": "Atributos para previsao de partidas",
    "match_team_stats": "Estatisticas das equipes por partida",
    "matches_detailed": "Detalhes estendidos das partidas",
    "player_stats": "Estatisticas individuais dos jogadores",
}


def create_bronze_table(file_name: str, description: str) -> None:
    """
    Cria uma materialized view bronze para um arquivo CSV do Volume.

    Usar uma funcao "fabrica" (em vez de decorar direto dentro do for)
    e necessario aqui: se voce aplicar @dp.materialized_view dentro do
    loop sem essa funcao intermediaria, todas as tabelas acabam lendo
    o ULTIMO arquivo da lista (closure tardia do Python). Essa funcao
    resolve isso capturando file_name como argumento local.
    """

    @dp.materialized_view(
        name=f"fifa_world_cup_2026.bronze.{file_name}",
        comment=f"Leitura bruta de {file_name}.csv - {description}.",
    )
    def _read():
        return (
            spark.read.csv(
                f"{VOLUME_PATH}/{file_name}.csv",
                header=True,
                inferSchema=True,
            )
        )


for file_name, description in RAW_FILES.items():
    create_bronze_table(file_name, description)