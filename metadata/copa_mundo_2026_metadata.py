import textwrap
import uuid


def _sort_id_lists(data):
    """A API do Genie exige que listas de join_specs, text_instructions,
    filters, expressions e measures venham ordenadas pelo campo `id`.
    Como os ids são gerados com uuid4() a cada chamada, a ordenação
    precisa ser feita em tempo de execução, logo antes do retorno."""
    instructions = data["serialized_space"]["instructions"]
    instructions["text_instructions"].sort(key=lambda item: item["id"])
    instructions["join_specs"].sort(key=lambda item: item["id"])
    snippets = instructions["sql_snippets"]
    snippets["filters"].sort(key=lambda item: item["id"])
    snippets["expressions"].sort(key=lambda item: item["id"])
    snippets["measures"].sort(key=lambda item: item["id"])
    return data


def get_copa_mundo_2026_metadata():
    data = {
        "title": "Copa do Mundo FIFA 2026 — Análise de Dados",
        "description": textwrap.dedent(
            """\
                Este agente responde perguntas sobre a Copa do Mundo FIFA 2026 em linguagem natural, permitindo explorar seleções, jogadores, partidas, estádios, árbitros, estatísticas e eventos de jogo.

                **O que consegue responder:**
                - Comparar seleções por ranking FIFA, confederação, grupo e desempenho no torneio.
                - Consultar o perfil dos jogadores (clube, idade, altura, posição) e suas estatísticas acumuladas: gols, assistências, cartões, minutos jogados e nota média.
                - Detalhar partidas: data, placar, gols esperados (xG), estádio, altitude, fase do torneio e árbitro.
                - Reconstruir a linha do tempo de um jogo a partir dos eventos (gols, cartões, assistências, VAR) por minuto, seleção e jogador.
                - Avaliar o desempenho de uma seleção por partida (posse de bola, finalizações, escanteios, faltas, impedimentos, eficiência) e identificar o melhor em campo.
                - Analisar escalações, formações, titulares, substituições e tempo em campo por atleta.
                - Filtrar qualquer análise por fase (grupos ou mata-mata), estádio, cidade-sede e altitude.
                - Calcular métricas avançadas: xG diferencial, gols acima do esperado, pontos esperados (xPts), pontos recuperados, estabilidade de escalação e índice de zebra.
                - Avaliar o rigor histórico dos árbitros pela média de cartões por jogo e cruzá-lo com o que aconteceu em campo.

                **Limitações:**
                - Só responde com base nas tabelas disponíveis. Assuntos como preço de ingressos, audiência de TV, treinos, contratos ou dados financeiros não estão no conjunto de dados.
                - Não há atualização em tempo real: os dados refletem a última data verificada em cada registro.
                - Não há dados de rastreamento avançado (mapas de calor, distância percorrida, velocidade).
                - Seleções, jogadores e árbitros fora da lista oficial do torneio não existem na base.
                - Métricas como xPts, índice de zebra, pontos recuperados e estabilidade de escalação são cálculos próprios deste projeto, e não estatísticas oficiais da FIFA.
            """
        ),
        "serialized_space": {
            "version": 2,
            "data_sources": {
                "tables": [
                    {
                        "identifier": "fifa_world_cup_2026.gold.dim_arbitros",
                        "column_configs": [
                            {
                                "column_name": "avg_cards_per_game",
                                "description": [
                                    'Média histórica de cartões (amarelos + vermelhos) mostrados por partida por este árbitro. É o indicador de "rigor" do árbitro e vem da carreira dele, não das partidas desta Copa.'
                                ],
                                "synonyms": [
                                    "rigor do árbitro",
                                    "cartões por partida",
                                    "severidade",
                                    "média de cartões",
                                    "árbitro rigoroso",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Média de Cartões por Jogo",
                            },
                            {
                                "column_name": "country",
                                "description": [
                                    "País da federação de origem do árbitro."
                                ],
                                "synonyms": [
                                    "nacionalidade do árbitro",
                                    "federação de origem",
                                    "país do juiz",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "País do Árbitro",
                            },
                            {
                                "column_name": "referee_id",
                                "description": [
                                    "Identificador único do árbitro. Chave usada no relacionamento com ft_partidas."
                                ],
                                "synonyms": ["código do árbitro", "id do juiz"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Árbitro",
                            },
                            {
                                "column_name": "referee_name",
                                "description": [
                                    "Nome completo do árbitro principal da partida."
                                ],
                                "synonyms": [
                                    "juiz",
                                    "árbitro principal",
                                    "nome do árbitro",
                                    "apitador",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Árbitro",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.dim_estadios",
                        "column_configs": [
                            {
                                "column_name": "capacity",
                                "description": [
                                    "Capacidade máxima oficial de público do estádio. Não é o público presente na partida."
                                ],
                                "synonyms": [
                                    "lotação",
                                    "número de lugares",
                                    "tamanho do estádio",
                                    "capacidade de público",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Capacidade",
                            },
                            {
                                "column_name": "city",
                                "description": [
                                    "Cidade-sede onde o estádio está localizado."
                                ],
                                "synonyms": [
                                    "município",
                                    "localidade",
                                    "cidade-sede",
                                    "sede",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Cidade",
                            },
                            {
                                "column_name": "country",
                                "description": [
                                    "País-sede do estádio. Nesta Copa, sempre Estados Unidos, México ou Canadá."
                                ],
                                "synonyms": [
                                    "nação sede",
                                    "país anfitrião",
                                    "país da sede",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "País-Sede",
                            },
                            {
                                "column_name": "elevation_meters",
                                "description": [
                                    "Altitude do estádio em relação ao nível do mar, em metros. Útil para analisar o efeito da altitude no desempenho das seleções (as sedes mexicanas são as mais altas)."
                                ],
                                "synonyms": [
                                    "elevação",
                                    "altura em relação ao mar",
                                    "altitude do estádio",
                                    "metros acima do nível do mar",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Altitude (m)",
                            },
                            {
                                "column_name": "stadium_name",
                                "description": ["Nome oficial do estádio-sede."],
                                "synonyms": [
                                    "arena",
                                    "sede",
                                    "local do jogo",
                                    "nome do estádio",
                                    "praça esportiva",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Estádio",
                            },
                            {
                                "column_name": "venue_id",
                                "description": [
                                    "Identificador único do estádio. Chave usada no relacionamento com ft_partidas."
                                ],
                                "synonyms": ["código do estádio", "id da sede"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Estádio",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.dim_etapas",
                        "column_configs": [
                            {
                                "column_name": "is_knockout",
                                "description": [
                                    "Indica se a fase é eliminatória (verdadeiro = mata-mata) ou fase de grupos (falso). Use sempre este campo para separar mata-mata de fase de grupos, em vez de tentar interpretar o nome da fase."
                                ],
                                "synonyms": [
                                    "eliminatória",
                                    "mata-mata",
                                    "é eliminatória",
                                    "fase final",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "É Mata-Mata",
                            },
                            {
                                "column_name": "stage_id",
                                "description": [
                                    "Identificador único da fase do torneio. Chave usada no relacionamento com ft_partidas."
                                ],
                                "synonyms": ["código da fase", "id da etapa"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Fase",
                            },
                            {
                                "column_name": "stage_name",
                                "description": [
                                    "Nome da fase do torneio (fase de grupos, oitavas, quartas, semifinal, decisão de terceiro lugar e final)."
                                ],
                                "synonyms": [
                                    "etapa",
                                    "rodada",
                                    "estágio do torneio",
                                    "nome da fase",
                                    "fase",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Fase",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.dim_jogadores",
                        "column_configs": [
                            {
                                "column_name": "club_team",
                                "description": [
                                    "Clube em que o jogador atua profissionalmente. Não confundir com a seleção que ele defende no torneio (team_id)."
                                ],
                                "synonyms": [
                                    "clube do jogador",
                                    "clube de origem",
                                    "time do clube",
                                    "onde joga",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Clube",
                            },
                            {
                                "column_name": "date_of_birth",
                                "description": [
                                    "Data de nascimento do jogador. Para responder perguntas sobre idade, calcule a diferença até a data de abertura do torneio (11/06/2026), não até a data de hoje."
                                ],
                                "synonyms": [
                                    "nascimento",
                                    "idade do jogador",
                                    "data de nascimento",
                                    "aniversário",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Data de Nascimento",
                            },
                            {
                                "column_name": "height_cm",
                                "description": ["Altura do jogador em centímetros."],
                                "synonyms": [
                                    "estatura",
                                    "altura do atleta",
                                    "quantos centímetros",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Altura (cm)",
                            },
                            {
                                "column_name": "player_id",
                                "description": [
                                    "Identificador único do atleta. Chave usada nos relacionamentos com escalações, eventos e estatísticas."
                                ],
                                "synonyms": ["código do jogador", "id do atleta"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "player_name",
                                "description": [
                                    "Nome do jogador convocado. Sempre exiba este nome nos resultados em vez do player_id."
                                ],
                                "synonyms": [
                                    "atleta",
                                    "craque",
                                    "nome do atleta",
                                    "nome do jogador",
                                    "jogador",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Jogador",
                            },
                            {
                                "column_name": "position",
                                "description": [
                                    "Posição tática de cadastro do jogador (goleiro, defensor, meio-campista, atacante). É a posição principal do atleta no torneio; a posição usada em uma partida específica está em ft_escalacoes.tactical_position."
                                ],
                                "synonyms": [
                                    "função em campo",
                                    "posição tática",
                                    "posição do jogador",
                                    "goleiro",
                                    "zagueiro",
                                    "meia",
                                    "atacante",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Posição",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Seleção que o jogador defende no torneio. Faz a ligação com dim_selecoes."
                                ],
                                "synonyms": [
                                    "seleção do atleta",
                                    "país do jogador",
                                    "id da seleção do jogador",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                        "column_configs": [
                            {
                                "column_name": "confederation",
                                "description": [
                                    "Confederação continental à qual a seleção pertence (CONMEBOL, UEFA, CAF, AFC, CONCACAF, OFC)."
                                ],
                                "synonyms": [
                                    "continente",
                                    "federação continental",
                                    "confederação",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Confederação",
                            },
                            {
                                "column_name": "fifa_code",
                                "description": [
                                    "Código de 3 letras da FIFA que identifica a seleção (por exemplo, BRA, ARG, FRA)."
                                ],
                                "synonyms": [
                                    "sigla",
                                    "abreviação",
                                    "código de 3 letras",
                                    "sigla da seleção",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Código FIFA",
                            },
                            {
                                "column_name": "fifa_ranking_pre_tournament",
                                "description": [
                                    "Posição da seleção no ranking mundial da FIFA antes do início da Copa. Atenção: quanto MENOR o número, mais forte a seleção (1 é a melhor do mundo). Ordene de forma crescente para listar as favoritas."
                                ],
                                "synonyms": [
                                    "ranking",
                                    "posição no ranking",
                                    "favoritismo",
                                    "ranking FIFA",
                                    "colocação no ranking",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Ranking FIFA Pré-Torneio",
                            },
                            {
                                "column_name": "group_letter",
                                "description": [
                                    "Letra do grupo da seleção na fase de grupos (A a L, já que são 12 grupos de 4 seleções)."
                                ],
                                "synonyms": [
                                    "chave",
                                    "letra do grupo",
                                    "grupo da seleção",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Grupo",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Identificador único da seleção. É a chave usada por todas as tabelas de fatos."
                                ],
                                "synonyms": [
                                    "id do time",
                                    "código do time",
                                    "id da seleção",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "team_name",
                                "description": [
                                    "Nome do país/seleção participante. Sempre exiba este nome nos resultados em vez do team_id."
                                ],
                                "synonyms": [
                                    "time",
                                    "país",
                                    "nação",
                                    "equipe",
                                    "seleção",
                                    "nome da seleção",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                        "column_configs": [
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Identificador único da partida. Grão desta tabela: uma linha por jogo."
                                ],
                                "synonyms": ["código do jogo", "id da partida"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "date",
                                "description": [
                                    "Data em que a partida foi disputada. Exiba no formato dia/mês/ano."
                                ],
                                "synonyms": [
                                    "dia do jogo",
                                    "data da partida",
                                    "quando foi o jogo",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Data da Partida",
                            },
                            {
                                "column_name": "kickoff_time_utc",
                                "description": [
                                    "Horário exato do apito inicial, em UTC. Lembre que o horário local das sedes é diferente do UTC."
                                ],
                                "synonyms": [
                                    "hora do jogo",
                                    "horário de início",
                                    "apito inicial",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Horário (UTC)",
                            },
                            {
                                "column_name": "home_team_id",
                                "description": [
                                    "Seleção mandante (time da casa) da partida. Ligue com dim_selecoes usando o alias dim_selecoes."
                                ],
                                "synonyms": [
                                    "time da casa",
                                    "mandante",
                                    "seleção mandante",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "ID Seleção Mandante",
                            },
                            {
                                "column_name": "away_team_id",
                                "description": [
                                    "Seleção visitante da partida. Ligue com dim_selecoes usando um segundo alias (dim_selecoes_2), nunca o mesmo alias do mandante."
                                ],
                                "synonyms": [
                                    "time visitante",
                                    "time de fora",
                                    "seleção visitante",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "ID Seleção Visitante",
                            },
                            {
                                "column_name": "home_score",
                                "description": [
                                    "Gols marcados pela seleção mandante no tempo normal e na prorrogação."
                                ],
                                "synonyms": [
                                    "placar da casa",
                                    "gols em casa",
                                    "gols do mandante",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols do Mandante",
                            },
                            {
                                "column_name": "away_score",
                                "description": [
                                    "Gols marcados pela seleção visitante no tempo normal e na prorrogação."
                                ],
                                "synonyms": [
                                    "placar visitante",
                                    "gols fora",
                                    "gols do visitante",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols do Visitante",
                            },
                            {
                                "column_name": "home_xg",
                                "description": [
                                    "Gols esperados (Expected Goals, xG) da seleção mandante: soma da probabilidade de gol de cada finalização criada."
                                ],
                                "synonyms": [
                                    "gols esperados da casa",
                                    "xG do mandante",
                                    "expected goals mandante",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "xG do Mandante",
                            },
                            {
                                "column_name": "away_xg",
                                "description": [
                                    "Gols esperados (Expected Goals, xG) da seleção visitante: soma da probabilidade de gol de cada finalização criada."
                                ],
                                "synonyms": [
                                    "gols esperados do visitante",
                                    "xG do visitante",
                                    "expected goals visitante",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "xG do Visitante",
                            },
                            {
                                "column_name": "stage_id",
                                "description": [
                                    "Fase do torneio em que a partida ocorreu. Ligue com dim_etapas para obter o nome da fase e o indicador de mata-mata."
                                ],
                                "synonyms": ["etapa do jogo", "fase da partida"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Fase",
                            },
                            {
                                "column_name": "venue_id",
                                "description": [
                                    "Estádio em que a partida foi disputada. Ligue com dim_estadios para obter nome, cidade, capacidade e altitude."
                                ],
                                "synonyms": ["local do jogo", "sede da partida"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Estádio",
                            },
                            {
                                "column_name": "referee_id",
                                "description": [
                                    "Árbitro principal designado para a partida. Ligue com dim_arbitros."
                                ],
                                "synonyms": ["juiz da partida", "árbitro do jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Árbitro",
                            },
                            {
                                "column_name": "status",
                                "description": [
                                    "Situação da partida (por exemplo, encerrada, em andamento ou agendada). Confira os valores existentes com um SELECT DISTINCT antes de filtrar por texto."
                                ],
                                "synonyms": [
                                    "situação do jogo",
                                    "andamento",
                                    "status da partida",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Status da Partida",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_eventos",
                        "column_configs": [
                            {
                                "column_name": "event_id",
                                "description": [
                                    "Identificador único do evento. Grão desta tabela: uma linha por lance registrado dentro de uma partida."
                                ],
                                "synonyms": ["código do evento", "id do lance"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Evento",
                            },
                            {
                                "column_name": "event_type",
                                "description": [
                                    "Tipo do lance registrado: gol, assistência, cartão amarelo, cartão vermelho, substituição, revisão de VAR e similares. Os valores estão gravados em inglês (por exemplo, 'Goal', 'Yellow Card', 'Red Card'); confirme com um SELECT DISTINCT antes de filtrar."
                                ],
                                "synonyms": [
                                    "categoria do evento",
                                    "o que aconteceu",
                                    "tipo de lance",
                                    "gol",
                                    "cartão",
                                    "substituição",
                                    "VAR",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Tipo de Evento",
                            },
                            {
                                "column_name": "match_id",
                                "description": ["Partida em que o evento ocorreu."],
                                "synonyms": ["jogo do evento", "partida do lance"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "minute",
                                "description": [
                                    "Minuto de jogo em que o evento aconteceu. Use para montar a linha do tempo da partida ou para analisar em que trecho do jogo cada seleção é mais decisiva."
                                ],
                                "synonyms": [
                                    "tempo do evento",
                                    "minutagem",
                                    "minuto do gol",
                                    "quando aconteceu",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Minuto",
                            },
                            {
                                "column_name": "player_id",
                                "description": [
                                    "Jogador envolvido no evento (quem marcou, quem recebeu o cartão, quem deu a assistência)."
                                ],
                                "synonyms": ["atleta envolvido", "jogador do lance"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Seleção envolvida no evento. Ligue com dim_selecoes para exibir o nome do país."
                                ],
                                "synonyms": ["time envolvido", "seleção do lance"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_escalacoes",
                        "column_configs": [
                            {
                                "column_name": "lineup_id",
                                "description": [
                                    "Identificador único do registro de escalação. Grão desta tabela: uma linha por jogador relacionado em cada partida."
                                ],
                                "synonyms": ["código da escalação", "id da escalação"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Escalação",
                            },
                            {
                                "column_name": "is_starting_xi",
                                "description": [
                                    "Verdadeiro se o jogador começou a partida como titular; falso se ficou no banco de reservas."
                                ],
                                "synonyms": [
                                    "titular",
                                    "começou jogando",
                                    "onze inicial",
                                    "banco de reservas",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "É Titular",
                            },
                            {
                                "column_name": "match_id",
                                "description": ["Partida a que a escalação se refere."],
                                "synonyms": ["jogo", "partida da escalação"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "minutes_played",
                                "description": [
                                    "Minutos que o jogador efetivamente atuou nesta partida. Zero indica que ficou no banco sem entrar."
                                ],
                                "synonyms": [
                                    "tempo em campo",
                                    "minutagem",
                                    "minutos na partida",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Minutos Jogados na Partida",
                            },
                            {
                                "column_name": "player_id",
                                "description": ["Jogador relacionado para a partida."],
                                "synonyms": ["atleta escalado", "jogador escalado"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "tactical_position",
                                "description": [
                                    "Posição tática efetivamente ocupada pelo jogador nesta partida. Pode ser diferente da posição de cadastro em dim_jogadores.position."
                                ],
                                "synonyms": [
                                    "função tática",
                                    "posição em campo no jogo",
                                    "posição na partida",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Posição na Partida",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção do jogador nesta partida."],
                                "synonyms": [
                                    "time do jogador na partida",
                                    "seleção escalada",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_equipe",
                        "column_configs": [
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Partida a que a estatística se refere. Atenção ao grão: esta tabela tem duas linhas por partida, uma para cada seleção."
                                ],
                                "synonyms": ["jogo", "partida da estatística"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Seleção a que a estatística pertence. Para saber se é a mandante ou a visitante, compare com ft_partidas.home_team_id e away_team_id, ou use a view vw_selecao_partida."
                                ],
                                "synonyms": ["time", "seleção da estatística"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "possession_pct",
                                "description": [
                                    "Percentual de posse de bola da seleção na partida, de 0 a 100. As duas linhas de uma mesma partida somam aproximadamente 100."
                                ],
                                "synonyms": [
                                    "posse",
                                    "domínio de bola",
                                    "posse de bola",
                                    "percentual de posse",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Posse de Bola (%)",
                            },
                            {
                                "column_name": "total_shots",
                                "description": [
                                    "Número total de finalizações realizadas pela seleção na partida, incluindo as que foram para fora."
                                ],
                                "synonyms": [
                                    "chutes",
                                    "tentativas de gol",
                                    "finalizações",
                                    "arremates",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações",
                            },
                            {
                                "column_name": "shots_on_target",
                                "description": [
                                    "Número de finalizações no alvo, ou seja, que exigiram defesa do goleiro ou resultaram em gol. É sempre menor ou igual a total_shots."
                                ],
                                "synonyms": [
                                    "chutes certos",
                                    "chutes a gol",
                                    "finalizações no gol",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações no Alvo",
                            },
                            {
                                "column_name": "corners",
                                "description": [
                                    "Número de escanteios cobrados pela seleção na partida."
                                ],
                                "synonyms": ["cantos", "córners", "escanteios"],
                                "enable_format_assistance": True,
                                "display_name": "Escanteios",
                            },
                            {
                                "column_name": "fouls",
                                "description": [
                                    "Número de faltas cometidas pela seleção na partida."
                                ],
                                "synonyms": ["infrações", "faltas cometidas"],
                                "enable_format_assistance": True,
                                "display_name": "Faltas",
                            },
                            {
                                "column_name": "offsides",
                                "description": [
                                    "Número de vezes em que a seleção foi flagrada em posição de impedimento."
                                ],
                                "synonyms": [
                                    "posições de impedimento",
                                    "impedimentos",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Impedimentos",
                            },
                            {
                                "column_name": "saves",
                                "description": [
                                    "Número de defesas realizadas pelo goleiro da seleção nesta partida."
                                ],
                                "synonyms": ["defesas do goleiro", "defesas"],
                                "enable_format_assistance": True,
                                "display_name": "Defesas",
                            },
                            {
                                "column_name": "player_of_the_match",
                                "description": [
                                    "Jogador eleito o melhor em campo pela seleção nesta partida. Pode ser nulo quando a fonte não registrou a escolha."
                                ],
                                "synonyms": [
                                    "craque do jogo",
                                    "MVP da partida",
                                    "melhor em campo",
                                    "man of the match",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Melhor em Campo",
                            },
                            {
                                "column_name": "data_source",
                                "description": [
                                    "Fonte de onde a estatística foi coletada. Campo de controle, não usado em análises."
                                ],
                                "synonyms": ["origem do dado"],
                                "exclude": True,
                                "display_name": "Fonte dos Dados",
                            },
                            {
                                "column_name": "last_updated",
                                "description": [
                                    "Data da última atualização deste registro. Campo de controle, não usado em análises."
                                ],
                                "synonyms": ["data de atualização"],
                                "exclude": True,
                                "display_name": "Última Atualização",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_jogador",
                        "column_configs": [
                            {
                                "column_name": "player_id",
                                "description": [
                                    "Jogador a que as estatísticas se referem. Grão desta tabela: uma linha por jogador, já com os totais acumulados do torneio."
                                ],
                                "synonyms": ["atleta", "id do jogador"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Seleção que o jogador defende no torneio."
                                ],
                                "synonyms": ["time do jogador", "seleção do atleta"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "position",
                                "description": [
                                    "Posição do jogador conforme esta fonte de estatísticas. Em caso de divergência, dim_jogadores.position é a referência oficial."
                                ],
                                "synonyms": ["função em campo", "posição"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Posição",
                            },
                            {
                                "column_name": "goals",
                                "description": [
                                    "Total de gols marcados pelo jogador no torneio. É a coluna correta para rankings de artilharia."
                                ],
                                "synonyms": [
                                    "artilharia",
                                    "gols marcados",
                                    "artilheiro",
                                    "goleador",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols",
                            },
                            {
                                "column_name": "assists",
                                "description": [
                                    "Total de assistências para gol dadas pelo jogador no torneio."
                                ],
                                "synonyms": [
                                    "passes para gol",
                                    "assistências",
                                    "garçom",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Assistências",
                            },
                            {
                                "column_name": "penalty_goals",
                                "description": [
                                    "Total de gols marcados de pênalti. Este total já está incluído na coluna goals — não some as duas."
                                ],
                                "synonyms": [
                                    "pênaltis convertidos",
                                    "gols de pênalti",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols de Pênalti",
                            },
                            {
                                "column_name": "own_goals",
                                "description": [
                                    "Total de gols contra marcados pelo jogador. Não entram na contagem de artilharia (goals)."
                                ],
                                "synonyms": [
                                    "gols contra",
                                    "contra",
                                    "gol contra",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols Contra",
                            },
                            {
                                "column_name": "yellow_cards",
                                "description": [
                                    "Total de cartões amarelos recebidos pelo jogador no torneio."
                                ],
                                "synonyms": ["amarelos", "cartões amarelos"],
                                "enable_format_assistance": True,
                                "display_name": "Cartões Amarelos",
                            },
                            {
                                "column_name": "red_cards",
                                "description": [
                                    "Total de cartões vermelhos recebidos pelo jogador no torneio."
                                ],
                                "synonyms": [
                                    "vermelhos",
                                    "expulsões",
                                    "cartões vermelhos",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Cartões Vermelhos",
                            },
                            {
                                "column_name": "shots",
                                "description": [
                                    "Total de finalizações tentadas pelo jogador no torneio."
                                ],
                                "synonyms": ["chutes tentados", "finalizações"],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações",
                            },
                            {
                                "column_name": "shots_on_target",
                                "description": [
                                    "Total de finalizações do jogador que foram no alvo."
                                ],
                                "synonyms": ["chutes certos", "finalizações no gol"],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações no Alvo",
                            },
                            {
                                "column_name": "saves",
                                "description": [
                                    "Total de defesas realizadas. Só faz sentido para goleiros."
                                ],
                                "synonyms": ["defesas do goleiro", "defesas"],
                                "enable_format_assistance": True,
                                "display_name": "Defesas",
                            },
                            {
                                "column_name": "clean_sheets",
                                "description": [
                                    "Número de partidas em que o jogador terminou sem sofrer gols. Só faz sentido para goleiros."
                                ],
                                "synonyms": [
                                    "clean sheets",
                                    "jogos sem sofrer gol",
                                    "jogos sem levar gol",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Jogos sem Sofrer Gol",
                            },
                            {
                                "column_name": "goals_conceded",
                                "description": [
                                    "Total de gols sofridos enquanto o jogador estava em campo. Só faz sentido para goleiros."
                                ],
                                "synonyms": ["gols tomados", "gols sofridos"],
                                "enable_format_assistance": True,
                                "display_name": "Gols Sofridos",
                            },
                            {
                                "column_name": "matches_played",
                                "description": [
                                    "Número de partidas em que o jogador entrou em campo no torneio."
                                ],
                                "synonyms": ["jogos disputados", "partidas jogadas"],
                                "enable_format_assistance": True,
                                "display_name": "Partidas Jogadas",
                            },
                            {
                                "column_name": "matches_started",
                                "description": [
                                    "Número de partidas em que o jogador foi titular. É sempre menor ou igual a matches_played."
                                ],
                                "synonyms": ["jogos como titular", "vezes titular"],
                                "enable_format_assistance": True,
                                "display_name": "Partidas como Titular",
                            },
                            {
                                "column_name": "minutes_played",
                                "description": [
                                    "Total de minutos que o jogador atuou no torneio. Use como filtro de corte em rankings por 90 minutos."
                                ],
                                "synonyms": [
                                    "tempo total em campo",
                                    "minutagem total",
                                    "minutos jogados",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Minutos Jogados",
                            },
                            {
                                "column_name": "average_rating",
                                "description": [
                                    "Nota média de desempenho do jogador no torneio, em escala de 0 a 10."
                                ],
                                "synonyms": [
                                    "avaliação média",
                                    "rating médio",
                                    "nota média",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Nota Média",
                            },
                            {
                                "column_name": "data_source",
                                "description": [
                                    "Fonte de onde a estatística foi coletada. Campo de controle, não usado em análises."
                                ],
                                "exclude": True,
                                "display_name": "Fonte dos Dados",
                            },
                            {
                                "column_name": "last_verified",
                                "description": [
                                    "Data da última verificação do registro. Campo de controle, não usado em análises."
                                ],
                                "exclude": True,
                                "display_name": "Última Verificação",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                        "column_configs": [
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Partida a que a linha se refere. Grão desta view: uma linha por seleção por partida (duas linhas por jogo)."
                                ],
                                "synonyms": ["id da partida", "jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "match_date",
                                "description": [
                                    "Data da partida. Exiba no formato dia/mês/ano."
                                ],
                                "synonyms": ["data do jogo", "dia da partida"],
                                "enable_format_assistance": True,
                                "display_name": "Data da Partida",
                            },
                            {
                                "column_name": "kickoff_time_utc",
                                "description": ["Horário do apito inicial, em UTC."],
                                "synonyms": ["hora do jogo", "horário de início"],
                                "enable_format_assistance": True,
                                "display_name": "Horário (UTC)",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Seleção da linha, ou seja, a seleção sob cuja ótica a partida está descrita."
                                ],
                                "synonyms": ["id da seleção", "time"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "team_name",
                                "description": [
                                    "Nome da seleção da linha. É a coluna correta para responder 'os jogos da seleção X'."
                                ],
                                "synonyms": [
                                    "seleção",
                                    "time",
                                    "país",
                                    "nome da seleção",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Seleção",
                            },
                            {
                                "column_name": "fifa_code",
                                "description": [
                                    "Código de 3 letras da FIFA da seleção da linha."
                                ],
                                "synonyms": ["sigla", "código FIFA"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Código FIFA",
                            },
                            {
                                "column_name": "team_role",
                                "description": [
                                    "Papel da seleção na partida: mandante ou visitante. Use este campo em vez de comparar manualmente home_team_id e away_team_id."
                                ],
                                "synonyms": [
                                    "mandante ou visitante",
                                    "papel na partida",
                                    "casa ou fora",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Mando de Campo",
                            },
                            {
                                "column_name": "opponent_team_id",
                                "description": [
                                    "Seleção adversária nesta partida. Nunca é igual a team_id."
                                ],
                                "synonyms": ["id do adversário", "id do oponente"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Adversário",
                            },
                            {
                                "column_name": "opponent_name",
                                "description": [
                                    "Nome da seleção adversária, já resolvido. Use esta coluna para montar o confronto ('Seleção x Adversário') em vez de fazer dois joins manuais com dim_selecoes."
                                ],
                                "synonyms": [
                                    "adversário",
                                    "oponente",
                                    "contra quem jogou",
                                    "rival",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Adversário",
                            },
                            {
                                "column_name": "opponent_fifa_code",
                                "description": [
                                    "Código de 3 letras da FIFA da seleção adversária."
                                ],
                                "synonyms": ["sigla do adversário"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Código FIFA do Adversário",
                            },
                            {
                                "column_name": "goals_for",
                                "description": [
                                    "Gols marcados pela seleção da linha nesta partida."
                                ],
                                "synonyms": [
                                    "gols marcados",
                                    "gols a favor",
                                    "gols pró",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols a Favor",
                            },
                            {
                                "column_name": "goals_against",
                                "description": [
                                    "Gols sofridos pela seleção da linha nesta partida."
                                ],
                                "synonyms": [
                                    "gols sofridos",
                                    "gols contra",
                                    "gols tomados",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Gols Sofridos",
                            },
                            {
                                "column_name": "xg_for",
                                "description": [
                                    "Gols esperados (xG) produzidos pela seleção da linha nesta partida."
                                ],
                                "synonyms": [
                                    "xG a favor",
                                    "gols esperados produzidos",
                                    "xG produzido",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "xG a Favor",
                            },
                            {
                                "column_name": "xg_against",
                                "description": [
                                    "Gols esperados (xG) concedidos ao adversário nesta partida. Quanto menor, melhor foi a defesa."
                                ],
                                "synonyms": [
                                    "xG contra",
                                    "gols esperados concedidos",
                                    "xG cedido",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "xG Contra",
                            },
                            {
                                "column_name": "result",
                                "description": [
                                    "Resultado da partida sob a ótica da seleção da linha: vitória, empate ou derrota. Confira os valores gravados com um SELECT DISTINCT antes de filtrar por texto."
                                ],
                                "synonyms": [
                                    "vitória",
                                    "empate",
                                    "derrota",
                                    "resultado",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Resultado",
                            },
                            {
                                "column_name": "points",
                                "description": [
                                    "Pontos conquistados pela seleção nesta partida: 3 na vitória, 1 no empate e 0 na derrota."
                                ],
                                "synonyms": [
                                    "pontos ganhos",
                                    "pontuação",
                                    "pontos na partida",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Pontos",
                            },
                            {
                                "column_name": "team_rank",
                                "description": [
                                    "Ranking FIFA pré-torneio da seleção da linha. Menor número significa seleção mais forte."
                                ],
                                "synonyms": ["ranking da seleção", "posição no ranking"],
                                "enable_format_assistance": True,
                                "display_name": "Ranking da Seleção",
                            },
                            {
                                "column_name": "opponent_rank",
                                "description": [
                                    "Ranking FIFA pré-torneio do adversário. Comparado com team_rank, indica quem era o favorito no confronto."
                                ],
                                "synonyms": [
                                    "ranking do adversário",
                                    "ranking do oponente",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Ranking do Adversário",
                            },
                            {
                                "column_name": "stage_id",
                                "description": [
                                    "Fase do torneio da partida. Ligue com dim_etapas para obter o nome e o indicador de mata-mata."
                                ],
                                "synonyms": ["fase", "etapa"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Fase",
                            },
                            {
                                "column_name": "venue_id",
                                "description": [
                                    "Estádio da partida. Ligue com dim_estadios para obter nome, cidade e altitude."
                                ],
                                "synonyms": ["estádio", "local do jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Estádio",
                            },
                            {
                                "column_name": "referee_id",
                                "description": [
                                    "Árbitro principal da partida. Ligue com dim_arbitros."
                                ],
                                "synonyms": ["árbitro", "juiz"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Árbitro",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.vw_xpts_selecao_partida",
                        "column_configs": [
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Partida a que o cálculo se refere. Grão desta view: uma linha por seleção por partida."
                                ],
                                "synonyms": ["id da partida", "jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção a que o cálculo se refere."],
                                "synonyms": ["id da seleção", "time"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "team_name",
                                "description": [
                                    "Nome da seleção a que o cálculo se refere."
                                ],
                                "synonyms": ["seleção", "time", "país"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Seleção",
                            },
                            {
                                "column_name": "actual_points",
                                "description": [
                                    "Pontos realmente conquistados na partida: 3, 1 ou 0."
                                ],
                                "synonyms": [
                                    "pontos reais",
                                    "pontos conquistados",
                                    "pontos obtidos",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Pontos Reais",
                            },
                            {
                                "column_name": "expected_points",
                                "description": [
                                    "Pontos esperados (xPts) estimados por um modelo de Poisson a partir do xG das duas seleções. É uma métrica calculada neste projeto, não um dado oficial da FIFA."
                                ],
                                "synonyms": [
                                    "xPts",
                                    "pontos esperados",
                                    "expected points",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Pontos Esperados (xPts)",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.vw_pontos_recuperados",
                        "column_configs": [
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Partida a que o cálculo se refere. Grão desta view: uma linha por seleção por partida."
                                ],
                                "synonyms": ["id da partida", "jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção a que o cálculo se refere."],
                                "synonyms": ["id da seleção", "time"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "team_name",
                                "description": [
                                    "Nome da seleção a que o cálculo se refere."
                                ],
                                "synonyms": ["seleção", "time", "país"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Seleção",
                            },
                            {
                                "column_name": "opponent_team_id",
                                "description": ["Seleção adversária na partida."],
                                "synonyms": ["id do adversário"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Adversário",
                            },
                            {
                                "column_name": "opponent_name",
                                "description": ["Nome da seleção adversária."],
                                "synonyms": ["adversário", "oponente"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Adversário",
                            },
                            {
                                "column_name": "points",
                                "description": [
                                    "Pontos efetivamente conquistados na partida: 3, 1 ou 0."
                                ],
                                "synonyms": ["pontos", "pontuação"],
                                "enable_format_assistance": True,
                                "display_name": "Pontos",
                            },
                            {
                                "column_name": "recovered_points",
                                "description": [
                                    "Pontos recuperados após estar em desvantagem no placar: 3 quando a seleção esteve perdendo e venceu, 1 quando esteve perdendo e empatou, e 0 quando nunca esteve atrás. Mede poder de reação."
                                ],
                                "synonyms": [
                                    "pontos recuperados",
                                    "poder de reação",
                                    "virada",
                                    "reação",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Pontos Recuperados",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.vw_estabilidade_escalacao",
                        "column_configs": [
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Partida a que o cálculo se refere. Grão desta view: uma linha por seleção por partida."
                                ],
                                "synonyms": ["id da partida", "jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "match_date",
                                "description": [
                                    "Data da partida, usada para ordenar a sequência de jogos de cada seleção."
                                ],
                                "synonyms": ["data do jogo"],
                                "enable_format_assistance": True,
                                "display_name": "Data da Partida",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção a que o cálculo se refere."],
                                "synonyms": ["id da seleção", "time"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "starting_players",
                                "description": [
                                    "Lista dos jogadores titulares nesta partida. Campo auxiliar do cálculo de estabilidade; use apenas para conferência, não para agregações."
                                ],
                                "synonyms": ["titulares", "onze inicial"],
                                "display_name": "Titulares da Partida",
                            },
                            {
                                "column_name": "previous_starting_players",
                                "description": [
                                    "Lista dos jogadores titulares na partida anterior da mesma seleção. Campo auxiliar do cálculo de estabilidade."
                                ],
                                "synonyms": ["titulares anteriores", "onze anterior"],
                                "display_name": "Titulares da Partida Anterior",
                            },
                            {
                                "column_name": "lineup_stability_pct",
                                "description": [
                                    "Percentual de titulares mantidos em relação à partida anterior da mesma seleção, de 0 a 100. É nulo na primeira partida de cada seleção, pois não existe jogo anterior para comparar."
                                ],
                                "synonyms": [
                                    "estabilidade da escalação",
                                    "titulares repetidos",
                                    "manutenção do time",
                                    "rodízio",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Estabilidade da Escalação (%)",
                            },
                        ],
                    },
                ]
            },
            "instructions": {
                "text_instructions": [
                    {
                        "id": uuid.uuid4().hex,
                        "content": [
                            textwrap.dedent(
                                """\
                                ## Idioma
                                Responda sempre em português do Brasil, com vocabulário de futebol, mesmo que a pergunta use termos em inglês (ex.: "top scorer" = artilheiro, "clean sheet" = jogo sem sofrer gol, "xG" = gols esperados).

                                ## Regras de negócio que não estão em nenhuma coluna ou join
                                * Ranking FIFA (`fifa_ranking_pre_tournament`, `team_rank`, `opponent_rank`): menor número = seleção mais forte (1 é a melhor do mundo). Para listar favoritas, ordene de forma crescente.
                                * `ft_estatisticas_equipe` tem duas linhas por partida (uma por seleção). Somar sem filtrar a seleção dobra os valores. Para saber se a linha é da mandante ou visitante, compare com `ft_partidas.home_team_id`/`away_team_id` ou use `vw_selecao_partida.team_role`.
                                * Em `ft_estatisticas_equipe`, `possession_pct` representa a posse controlada oficial da FIFA. A soma das duas seleções pode ser menor que 100%; a diferença corresponde ao período "In Contest", no qual nenhuma equipe possuía controle claro da bola. Não normalize os valores, exceto quando o usuário pedir explicitamente uma posse tradicional fechando em 100%.
                                * `dim_arbitros.avg_cards_per_game` é a média histórica de carreira do árbitro, não os cartões da partida em si. Cartões reais estão em `ft_eventos` e `ft_estatisticas_jogador.yellow_cards`/`red_cards`.
                                * `saves`, `clean_sheets` e `goals_conceded` em `ft_estatisticas_jogador` só fazem sentido para goleiros. Filtre a posição antes de montar rankings de goleiro.
                                * `penalty_goals` já está incluído em `goals`; `own_goals` não entra em `goals`. Não some essas colunas.
                                * xPts, índice de zebra, pontos recuperados e estabilidade de escalação são métricas calculadas neste projeto, não estatísticas oficiais da FIFA. Ao apresentá-las, explique em uma frase curta o que significam.
                                * Quando um campo estiver nulo (`player_of_the_match`, estabilidade na primeira partida de uma seleção, campos de goleiro para jogador de linha), diga que o dado não estava disponível na fonte — nunca trate como zero.
                                * Antes de filtrar por texto em `event_type`, `status`, `result` ou `team_role`, confira os valores realmente gravados com um `SELECT DISTINCT` — alguns estão em inglês na origem.
                                * Tradução de `dim_etapas.stage_name` (os valores na fonte estão em inglês): "Group Stage" = fase de grupos; "Round of 32" = dezesseis-avos-de-final; "Round of 16" = oitavas-de-final; "Quarterfinal" = quartas de final; "Semifinal" = semifinal; "Final" = final. Nunca chame o Round of 32 de "oitavas" — oitavas de final é exclusivamente o Round of 16.

                                ## Formatação das respostas
                                * Datas no formato dia/mês/ano (ex.: 14/07/2026).
                                * `possession_pct` e `lineup_stability_pct`: exiba com "%" e uma casa decimal, nunca como fração.
                                * xG, xPts e demais métricas decimais: arredonde para 2 casas ao exibir, mas nunca antes de somar ou comparar.
                                * Placares no formato "Seleção 2 x 1 Adversário", com a seleção da pergunta à esquerda.
                                * Em rankings ou listagens, mostre sempre o nome legível (`team_name`, `player_name`, `stadium_name`, `referee_name`) via join com a dimensão — nunca apenas colunas `_id`.
                                * Em rankings por 90 minutos ou por partida, informe o corte mínimo de minutagem usado.
                                * Ao listar mais de 10 linhas, mostre o Top 10 e diga quantas linhas existem no total.
                                """
                            ),
                            textwrap.dedent(
                                """\
                                ## Regras de negócio importantes
                                * **Ranking FIFA invertido:** em `dim_selecoes.fifa_ranking_pre_tournament` e nas colunas `team_rank`/`opponent_rank`, **menor número = seleção mais forte** (1 é a melhor do mundo). Para listar as favoritas, ordene de forma crescente. Nunca trate esse número como se "maior fosse melhor".
                                * **Dimensão de papel duplo:** `ft_partidas` referencia `dim_selecoes` duas vezes — `home_team_id` é a mandante e `away_team_id` é a visitante. Ao perguntar "todos os jogos de um time", considere as duas colunas; filtrar só por `home_team_id` esconde metade dos jogos.
                                * **Nunca reutilize o mesmo alias de `dim_selecoes` para mandante e visitante.** Isso faz o adversário aparecer como a própria seleção (por exemplo, "Brasil x Brasil"). Se precisar mesmo partir de `ft_partidas`, use dois joins com aliases distintos (`dim_selecoes` para o mandante e `dim_selecoes_2` para o visitante). Na dúvida, prefira `vw_selecao_partida`, que já entrega `team_name` e `opponent_name` corretos.
                                * **Grão duplo:** `ft_estatisticas_equipe` tem duas linhas por partida, uma por seleção. Para saber se a linha é da mandante ou da visitante, compare com `ft_partidas.home_team_id`/`away_team_id` ou use `vw_selecao_partida.team_role`. Ao somar estatísticas por partida sem filtrar a seleção, os valores dobram.
                                * **Fases:** `dim_etapas.is_knockout = true` identifica mata-mata; `false` é fase de grupos. Use esse campo em vez de tentar interpretar o nome da fase.
                                * **Árbitros:** `dim_arbitros.avg_cards_per_game` é uma média histórica da carreira do árbitro, não os cartões da partida. Os cartões realmente mostrados estão em `ft_eventos` (`event_type` de cartão amarelo ou vermelho) e em `ft_estatisticas_jogador.yellow_cards`/`red_cards`.
                                * **Goleiros:** `saves`, `clean_sheets` e `goals_conceded` em `ft_estatisticas_jogador` só fazem sentido para jogadores com posição de goleiro; para as demais posições esses campos tendem a ser nulos ou zero. Filtre a posição antes de fazer rankings de goleiro.
                                * **Pênaltis e gols contra:** `penalty_goals` já está incluído em `goals`; `own_goals` não entra em `goals`. Não some as colunas.
                                * **Métricas próprias:** xPts, índice de zebra, pontos recuperados, estabilidade de escalação e as métricas derivadas de xG são cálculos deste projeto, e não estatísticas oficiais da FIFA. Sempre que apresentá-las, diga em uma frase curta o que elas significam.
                                * **Valores nulos:** quando um campo estiver nulo (por exemplo, `player_of_the_match`, estabilidade na primeira partida de uma seleção ou campos de goleiro para um jogador de linha), explique que o dado não estava disponível na fonte em vez de tratar como zero.
                                * **Valores textuais:** antes de filtrar por texto em `event_type`, `status`, `result` ou `team_role`, verifique os valores realmente gravados com um `SELECT DISTINCT`. Alguns estão em inglês na origem.

                                ## Formatação das respostas
                                * Datas: sempre no formato dia/mês/ano, por exemplo 14/07/2026.
                                * `possession_pct` e `lineup_stability_pct` são percentuais de 0 a 100 — exiba com o símbolo % e uma casa decimal, nunca como fração.
                                * xG, xPts e demais métricas decimais: arredonde para 2 casas ao exibir, mas nunca arredonde antes de somar ou comparar.
                                * Placares: exiba no formato "Seleção 2 x 1 Adversário", com a seleção da pergunta à esquerda.
                                * Em qualquer ranking ou listagem, mostre sempre o nome legível (`team_name`, `player_name`, `stadium_name`, `referee_name`) obtido pelo join com a dimensão. **Nunca exiba apenas colunas terminadas em `_id`.**
                                * Em rankings por 90 minutos ou por partida, informe o corte mínimo de minutagem usado e, quando fizer sentido, exiba também o total absoluto ao lado da média.
                                * Ao listar mais de 10 linhas, mostre o Top 10 e diga quantas linhas existem no total.

                                ## Desambiguação
                                * "Gols" sem mais contexto: se o sujeito for um jogador, use `ft_estatisticas_jogador.goals`; se for uma seleção, use `vw_selecao_partida.goals_for`; se for uma partida, use `ft_partidas.home_score`/`away_score`.
                                * "Melhor em campo", "craque do jogo" ou "MVP" = `ft_estatisticas_equipe.player_of_the_match`.
                                * "Rigor do árbitro" = `dim_arbitros.avg_cards_per_game`, e não uma contagem feita a partir de `ft_eventos`.
                                * "Artilheiro" = maior `ft_estatisticas_jogador.goals`. Em caso de empate, desempate por menos minutos jogados e por mais assistências, sempre explicando o critério usado.
                                * "Aproveitamento" = pontos conquistados dividido pelo total de pontos disputados (3 por partida), exibido em percentual.
                                * "Zebra" = vitória ou empate da seleção com ranking FIFA pior (número maior) contra uma seleção melhor ranqueada.
                                * "Altitude" se refere ao estádio (`dim_estadios.elevation_meters`), nunca à altura dos jogadores (`dim_jogadores.height_cm`).
                                * "Posição" pode ser a posição de cadastro (`dim_jogadores.position`), a posição usada em um jogo (`ft_escalacoes.tactical_position`) ou a colocação em um ranking — confirme pelo contexto da pergunta.
                                """
                            ),
                        ],
                    },
                ],
                "join_specs": [
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.dim_jogadores",
                            "alias": "dim_jogadores",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`dim_jogadores`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga cada jogador convocado à seleção que ele defende. Use para perguntas sobre o elenco de um país, a nacionalidade de um jogador ou médias por seleção (altura, idade). Relação N:1, com 26 jogadores por seleção."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`ft_partidas`.`home_team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Resolve o nome da seleção mandante. Como dim_selecoes é uma dimensão de papel duplo, este join cobre apenas o lado mandante — o alias dim_selecoes representa exclusivamente o time da casa e nunca deve ser usado para o visitante."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes_2",
                        },
                        "sql": [
                            "`ft_partidas`.`away_team_id` = `dim_selecoes_2`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve o nome da seleção visitante, sempre com o alias dim_selecoes_2. Use junto com o join do mandante quando a pergunta precisar mostrar os dois lados do confronto. Se apenas um dos dois joins for usado para montar "quem jogou contra quem", o adversário aparece como a própria seleção — nesse tipo de pergunta, prefira vw_selecao_partida.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_estadios",
                            "alias": "dim_estadios",
                        },
                        "sql": [
                            "`ft_partidas`.`venue_id` = `dim_estadios`.`venue_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a partida ao estádio. Use para perguntas sobre capacidade, cidade-sede, país-sede ou altitude (por exemplo, "jogos disputados em estádios acima de 2000 metros").'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_etapas",
                            "alias": "dim_etapas",
                        },
                        "sql": [
                            "`ft_partidas`.`stage_id` = `dim_etapas`.`stage_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga a partida à fase do torneio. Use para separar fase de grupos de mata-mata ou filtrar uma fase específica; combine com is_knockout para agrupamentos rápidos."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_arbitros",
                            "alias": "dim_arbitros",
                        },
                        "sql": [
                            "`ft_partidas`.`referee_id` = `dim_arbitros`.`referee_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve o árbitro principal da partida. Necessário para cruzar resultado ou cartões com o histórico de rigor do árbitro (por exemplo, "partidas apitadas por árbitros com média de cartões acima de 4").'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_escalacoes",
                            "alias": "ft_escalacoes",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "sql": [
                            "`ft_escalacoes`.`match_id` = `ft_partidas`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a escalação à partida. Necessário para "quem começou como titular em tal jogo" ou para cruzar escalação com data, fase e estádio. Atenção: cada partida traz muitas linhas de escalação, então não some colunas de ft_partidas depois deste join sem usar COUNT(DISTINCT) ou uma subconsulta.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_escalacoes",
                            "alias": "ft_escalacoes",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_jogadores",
                            "alias": "dim_jogadores",
                        },
                        "sql": [
                            "`ft_escalacoes`.`player_id` = `dim_jogadores`.`player_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve o nome e os atributos do jogador escalado. Use para "quantas vezes um jogador foi titular" ou para comparar a posição de cadastro (dim_jogadores.position) com a posição tática usada na partida (ft_escalacoes.tactical_position).'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_escalacoes",
                            "alias": "ft_escalacoes",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`ft_escalacoes`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a escalação à seleção. Use para análises de formação e rodízio por seleção (por exemplo, "quantos jogadores diferentes o Brasil escalou como titular no torneio").'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_equipe",
                            "alias": "ft_estatisticas_equipe",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "sql": [
                            "`ft_estatisticas_equipe`.`match_id` = `ft_partidas`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga as estatísticas de uma seleção (posse, finalizações, escanteios) à partida em que ocorreram. Necessário para relacionar "como" o time jogou com o contexto do jogo. Atenção: são duas linhas por partida, então somar colunas de ft_partidas após este join dobra os valores.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_equipe",
                            "alias": "ft_estatisticas_equipe",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`ft_estatisticas_equipe`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Resolve o nome da seleção dona da estatística. Atenção: esta tabela tem duas linhas por partida, uma por seleção, e o join sozinho não diz quem foi mandante ou visitante — para isso, cruze também com ft_partidas.home_team_id/away_team_id ou use vw_selecao_partida.team_role."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_jogador",
                            "alias": "ft_estatisticas_jogador",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_jogadores",
                            "alias": "dim_jogadores",
                        },
                        "sql": [
                            "`ft_estatisticas_jogador`.`player_id` = `dim_jogadores`.`player_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve nome, posição, clube e demais atributos do jogador a partir das estatísticas do torneio. É o join que traduz "quem tem o player_id com mais gols" em um nome de verdade, e deve estar presente em todo ranking individual.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_jogador",
                            "alias": "ft_estatisticas_jogador",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`ft_estatisticas_jogador`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga as estatísticas acumuladas do jogador à seleção que ele defende. Use para rankings agregados por seleção (por exemplo, "seleção cujo elenco somou mais gols no torneio").'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_eventos",
                            "alias": "ft_eventos",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                            "alias": "ft_partidas",
                        },
                        "sql": [
                            "`ft_eventos`.`match_id` = `ft_partidas`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga cada evento (gol, cartão, assistência, VAR) à partida. Essencial para reconstruir a linha do tempo de um jogo ou filtrar eventos por fase, data ou estádio. Como há muitos eventos por partida, use COUNT(DISTINCT match_id) ao contar jogos depois deste join."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_eventos",
                            "alias": "ft_eventos",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`ft_eventos`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve a seleção envolvida no evento. Use para disciplina por seleção (por exemplo, "quantos cartões vermelhos a seleção X recebeu no torneio") ou para distribuição de gols por minuto de jogo.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.ft_eventos",
                            "alias": "ft_eventos",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_jogadores",
                            "alias": "dim_jogadores",
                        },
                        "sql": [
                            "`ft_eventos`.`player_id` = `dim_jogadores`.`player_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve o jogador envolvido no evento. Dá para montar rankings individuais a partir dos eventos brutos, mas isso é redundante com ft_estatisticas_jogador — prefira ft_estatisticas_jogador para "quem marcou mais gols no total" e reserve ft_eventos para detalhe minuto a minuto.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga a linha de desempenho à seleção dona dela. Só é necessário quando a pergunta pedir atributos que não estão na view, como grupo, confederação ou ranking pré-torneio — o nome da seleção já vem pronto em vw_selecao_partida.team_name."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes_2",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`opponent_team_id` = `dim_selecoes_2`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a linha de desempenho à seleção adversária, sempre com o alias dim_selecoes_2. Use apenas para trazer atributos do adversário que não estão na view (grupo, confederação, ranking) — o nome do adversário já vem pronto em vw_selecao_partida.opponent_name.'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_etapas",
                            "alias": "dim_etapas",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`stage_id` = `dim_etapas`.`stage_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Traz a fase do torneio para as análises por seleção. Use para separar desempenho na fase de grupos do desempenho no mata-mata."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_estadios",
                            "alias": "dim_estadios",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`venue_id` = `dim_estadios`.`venue_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Traz o estádio para as análises por seleção. Use para perguntas como "as seleções vão melhor ou pior em estádios de altitude".'
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_arbitros",
                            "alias": "dim_arbitros",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`referee_id` = `dim_arbitros`.`referee_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Traz o árbitro para as análises por seleção. Use para cruzar o rigor histórico do árbitro com o desempenho das seleções nas partidas que ele apitou."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_equipe",
                            "alias": "ft_estatisticas_equipe",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`match_id` = `ft_estatisticas_equipe`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Junta o resultado da partida com as estatísticas de jogo pela partida. Use sempre em conjunto com o join por team_id entre as mesmas duas tabelas — as duas chaves juntas (match_id e team_id) é que garantem não misturar as linhas das duas seleções. Caminho para perguntas como 'quem teve mais posse de bola nas vitórias'."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_equipe",
                            "alias": "ft_estatisticas_equipe",
                        },
                        "sql": [
                            "`vw_selecao_partida`.`team_id` = `ft_estatisticas_equipe`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Complementa o join por match_id entre vw_selecao_partida e ft_estatisticas_equipe. Use sempre as duas chaves (match_id e team_id) juntas; usar só esta trocaria a seleção pela do adversário na mesma partida."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_xpts_selecao_partida",
                            "alias": "vw_xpts_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "sql": [
                            "`vw_xpts_selecao_partida`.`match_id` = `vw_selecao_partida`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Junta pontos esperados (xPts) com o desempenho real da mesma partida. Use sempre em conjunto com o join por team_id entre as mesmas duas tabelas, para não misturar as duas seleções da partida."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_xpts_selecao_partida",
                            "alias": "vw_xpts_selecao_partida",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "sql": [
                            "`vw_xpts_selecao_partida`.`team_id` = `vw_selecao_partida`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Complementa o join por match_id entre vw_xpts_selecao_partida e vw_selecao_partida. Use as duas chaves juntas (match_id e team_id). Use para perguntas sobre sorte e azar: pontos reais acima do xPts indicam aproveitamento acima do que o xG previa."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_pontos_recuperados",
                            "alias": "vw_pontos_recuperados",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "sql": [
                            "`vw_pontos_recuperados`.`match_id` = `vw_selecao_partida`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Junta os pontos recuperados com o contexto completo da partida (fase, adversário, estádio). Use sempre em conjunto com o join por team_id entre as mesmas duas tabelas."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_pontos_recuperados",
                            "alias": "vw_pontos_recuperados",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "sql": [
                            "`vw_pontos_recuperados`.`team_id` = `vw_selecao_partida`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Complementa o join por match_id entre vw_pontos_recuperados e vw_selecao_partida. Use as duas chaves juntas (match_id e team_id). Use para perguntas sobre poder de reação e viradas."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_estabilidade_escalacao",
                            "alias": "vw_estabilidade_escalacao",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "sql": [
                            "`vw_estabilidade_escalacao`.`match_id` = `vw_selecao_partida`.`match_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Junta a estabilidade da escalação com o resultado da partida. Use sempre em conjunto com o join por team_id entre as mesmas duas tabelas."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_estabilidade_escalacao",
                            "alias": "vw_estabilidade_escalacao",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.vw_selecao_partida",
                            "alias": "vw_selecao_partida",
                        },
                        "sql": [
                            "`vw_estabilidade_escalacao`.`team_id` = `vw_selecao_partida`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Complementa o join por match_id entre vw_estabilidade_escalacao e vw_selecao_partida. Use as duas chaves juntas (match_id e team_id). Lembre que a primeira partida de cada seleção tem estabilidade nula e deve ficar de fora das médias."
                        ],
                    },
                    {
                        "id": uuid.uuid4().hex,
                        "left": {
                            "identifier": "fifa_world_cup_2026.gold.vw_estabilidade_escalacao",
                            "alias": "vw_estabilidade_escalacao",
                        },
                        "right": {
                            "identifier": "fifa_world_cup_2026.gold.dim_selecoes",
                            "alias": "dim_selecoes",
                        },
                        "sql": [
                            "`vw_estabilidade_escalacao`.`team_id` = `dim_selecoes`.`team_id`",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Resolve o nome da seleção na análise de estabilidade da escalação, já que esta view não traz team_name."
                        ],
                    },
                ],
                "sql_snippets": {
                    "filters": [
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    dim_etapas.is_knockout = true
                                    """
                                )
                            ],
                            "display_name": "Somente Mata-Mata",
                            "instruction": [
                                'Use quando a pergunta mencionar "mata-mata", "eliminatórias", "fases finais" ou uma fase específica de knockout (oitavas, quartas, semifinal, final).'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    dim_etapas.is_knockout = false
                                    """
                                )
                            ],
                            "display_name": "Somente Fase de Grupos",
                            "instruction": [
                                'Use quando a pergunta mencionar "fase de grupos", "primeira fase" ou "classificação dos grupos".'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    ft_escalacoes.is_starting_xi = true
                                    """
                                )
                            ],
                            "display_name": "Somente Titulares",
                            "instruction": [
                                'Use quando a pergunta for sobre quem "jogou desde o início", "foi titular" ou "esteve no onze inicial", em oposição a quem entrou como reserva.'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    dim_jogadores.position = 'GK'
                                    """
                                )
                            ],
                            "display_name": "Somente Goleiros",
                            "instruction": [
                                "Use para perguntas sobre defesas, gols sofridos ou jogos sem sofrer gol — esses campos só fazem sentido para goleiros. Se o valor 'GK' não retornar linhas, confira os códigos de posição realmente gravados na tabela."
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    dim_jogadores.position <> 'GK'
                                    """
                                )
                            ],
                            "display_name": "Somente Jogadores de Linha",
                            "instruction": [
                                "Use em rankings ofensivos (gols, assistências, finalizações) quando a pergunta for sobre jogadores de linha e os goleiros distorcerem o resultado."
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    vw_selecao_partida.points = 3
                                    """
                                )
                            ],
                            "display_name": "Somente Vitórias",
                            "instruction": [
                                'Use quando a pergunta for sobre vitórias de uma seleção. Filtrar por pontos é mais seguro do que filtrar pelo texto da coluna result. Para empates use points = 1 e para derrotas points = 0.'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    dim_estadios.elevation_meters >= 1500
                                    """
                                )
                            ],
                            "display_name": "Estádios de Altitude",
                            "instruction": [
                                'Use quando a pergunta mencionar "altitude", "estádios altos" ou o efeito das sedes mexicanas. O corte de 1500 metros é uma convenção deste projeto — ajuste se a pergunta trouxer outro valor.'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    ft_estatisticas_jogador.minutes_played >= 270
                                    """
                                )
                            ],
                            "display_name": "Minutagem Mínima (3 jogos)",
                            "instruction": [
                                "Use como corte em rankings de médias por 90 minutos ou de nota média, para evitar que jogadores com pouquíssimos minutos apareçam no topo. Sempre informe na resposta que o corte foi aplicado."
                            ],
                        },
                    ],
                    "expressions": [
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    CASE
                                        WHEN ft_partidas.home_score > ft_partidas.away_score THEN 'Vitória do Mandante'
                                        WHEN ft_partidas.home_score < ft_partidas.away_score THEN 'Vitória do Visitante'
                                        ELSE 'Empate'
                                    END
                                    """
                                )
                            ],
                            "display_name": "Resultado da Partida",
                            "instruction": [
                                "Classifica a partida do ponto de vista do mando de campo. Para o resultado sob a ótica de uma seleção específica, use vw_selecao_partida.result ou vw_selecao_partida.points."
                            ],
                            "synonyms": [
                                "quem venceu",
                                "vitória ou empate",
                                "desfecho do jogo",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    DATEDIFF(YEAR, dim_jogadores.date_of_birth, DATE('2026-06-11'))
                                    """
                                )
                            ],
                            "display_name": "Idade na Abertura do Torneio",
                            "instruction": [
                                "Calcula a idade do jogador em 11/06/2026, data de abertura da Copa, e não a idade na data de hoje. Use sempre esta expressão quando a pergunta falar em idade."
                            ],
                            "synonyms": [
                                "idade",
                                "quantos anos",
                                "idade do jogador",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    CASE
                                        WHEN DATEDIFF(YEAR, dim_jogadores.date_of_birth, DATE('2026-06-11')) < 21 THEN 'Até 20 anos'
                                        WHEN DATEDIFF(YEAR, dim_jogadores.date_of_birth, DATE('2026-06-11')) < 26 THEN '21 a 25 anos'
                                        WHEN DATEDIFF(YEAR, dim_jogadores.date_of_birth, DATE('2026-06-11')) < 31 THEN '26 a 30 anos'
                                        WHEN DATEDIFF(YEAR, dim_jogadores.date_of_birth, DATE('2026-06-11')) < 36 THEN '31 a 35 anos'
                                        ELSE '36 anos ou mais'
                                    END
                                    """
                                )
                            ],
                            "display_name": "Faixa Etária",
                            "instruction": [
                                "Agrupa os jogadores em faixas de idade calculadas na data de abertura do torneio. Use para distribuições e comparações entre seleções jovens e experientes."
                            ],
                            "synonyms": [
                                "grupo de idade",
                                "faixa de idade",
                                "jovens e veteranos",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    CASE
                                        WHEN ft_eventos.minute <= 15 THEN '01-15'
                                        WHEN ft_eventos.minute <= 30 THEN '16-30'
                                        WHEN ft_eventos.minute <= 45 THEN '31-45'
                                        WHEN ft_eventos.minute <= 60 THEN '46-60'
                                        WHEN ft_eventos.minute <= 75 THEN '61-75'
                                        ELSE '76-90+'
                                    END
                                    """
                                )
                            ],
                            "display_name": "Faixa de Minutos do Jogo",
                            "instruction": [
                                "Agrupa os eventos em blocos de 15 minutos. Use para perguntas sobre em que trecho do jogo cada seleção mais marca ou mais sofre gols. Os acréscimos ficam na última faixa."
                            ],
                            "synonyms": [
                                "período do jogo",
                                "bloco de 15 minutos",
                                "momento do gol",
                            ],
                        },
                    ],
                    "measures": [
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    COUNT(DISTINCT ft_partidas.match_id)
                                    """
                                )
                            ],
                            "display_name": "Total de Partidas",
                            "instruction": [
                                "Conta partidas distintas. Use sempre COUNT(DISTINCT match_id) em vez de COUNT(*) quando houver join com escalações, eventos ou estatísticas de equipe, que multiplicam as linhas."
                            ],
                            "synonyms": [
                                "número de jogos",
                                "quantidade de partidas",
                                "quantos jogos",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(ft_partidas.home_score) + SUM(ft_partidas.away_score)
                                    """
                                )
                            ],
                            "display_name": "Total de Gols do Torneio",
                            "instruction": [
                                "Soma todos os gols marcados nas partidas consideradas, somando os dois lados do placar. Use apenas partindo de ft_partidas, sem joins que dupliquem linhas."
                            ],
                            "synonyms": [
                                "gols no total",
                                "total de gols",
                                "quantos gols",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    AVG(ft_partidas.home_score + ft_partidas.away_score)
                                    """
                                )
                            ],
                            "display_name": "Média de Gols por Partida",
                            "instruction": [
                                "Média de gols dos dois times somados por jogo. Bom indicador para comparar fase de grupos com mata-mata ou estádios de altitude com estádios ao nível do mar."
                            ],
                            "synonyms": [
                                "média de gols",
                                "gols por jogo",
                                "média por partida",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_selecao_partida.goals_for)
                                    -
                                    SUM(vw_selecao_partida.goals_against)
                                    """
                                )
                            ],
                            "display_name": "Saldo de Gols",
                            "instruction": [
                                "Gols marcados menos gols sofridos pela seleção, considerando corretamente jogos como mandante e como visitante. Agrupe por team_id ou team_name. Não calcule saldo a partir de ft_partidas.home_score menos away_score, porque isso só enxerga o lado mandante."
                            ],
                            "synonyms": [
                                "saldo",
                                "diferença de gols",
                                "gols pró menos gols contra",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_selecao_partida.points)
                                    """
                                )
                            ],
                            "display_name": "Pontos Conquistados",
                            "instruction": [
                                "Soma os pontos da seleção nas partidas consideradas (3 por vitória, 1 por empate). Base para montar a classificação dos grupos; agrupe por team_name e ordene de forma decrescente, usando saldo de gols como critério de desempate."
                            ],
                            "synonyms": [
                                "pontos",
                                "pontuação",
                                "pontos no grupo",
                                "classificação",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    100.0 * SUM(vw_selecao_partida.points)
                                    /
                                    NULLIF(3 * COUNT(DISTINCT vw_selecao_partida.match_id), 0)
                                    """
                                )
                            ],
                            "display_name": "Aproveitamento (%)",
                            "instruction": [
                                "Percentual de pontos conquistados sobre o total de pontos disputados, considerando 3 pontos por partida. Exiba com o símbolo % e uma casa decimal. Permite comparar seleções que disputaram números diferentes de jogos."
                            ],
                            "synonyms": [
                                "aproveitamento",
                                "percentual de pontos",
                                "rendimento",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    AVG(vw_selecao_partida.goals_against)
                                    """
                                )
                            ],
                            "display_name": "Média de Gols Sofridos por Jogo",
                            "instruction": [
                                "Média de gols que a seleção sofreu por partida. Quanto menor, melhor o desempenho defensivo. Agrupe por team_name."
                            ],
                            "synonyms": [
                                "gols sofridos por jogo",
                                "defesa",
                                "média defensiva",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_selecao_partida.goals_for)
                                    /
                                    NULLIF(SUM(vw_selecao_partida.xg_for), 0)
                                    """
                                )
                            ],
                            "display_name": "Eficiência Ofensiva (Gols/xG)",
                            "instruction": [
                                "Compara gols reais com gols esperados da seleção. Valores acima de 1 indicam finalização acima do esperado; abaixo de 1, desperdício de chances. Calcule sempre a partir de vw_selecao_partida para considerar jogos como mandante e visitante."
                            ],
                            "synonyms": [
                                "eficiência",
                                "gols por xG",
                                "aproveitamento das chances",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_selecao_partida.xg_for)
                                    -
                                    SUM(vw_selecao_partida.xg_against)
                                    """
                                )
                            ],
                            "display_name": "xG Diferencial",
                            "instruction": [
                                "xG produzido menos xG concedido. Valores positivos indicam que a seleção criou chances de melhor qualidade do que permitiu ao adversário. Agrupe por team_id ou team_name ao comparar seleções."
                            ],
                            "synonyms": [
                                "saldo de xG",
                                "xG diff",
                                "diferença de xG",
                                "domínio por xG",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_selecao_partida.goals_for)
                                    -
                                    SUM(vw_selecao_partida.xg_for)
                                    """
                                )
                            ],
                            "display_name": "Gols Acima do Esperado",
                            "instruction": [
                                "Gols marcados menos xG produzido. Resultado positivo indica que a seleção marcou mais do que a qualidade das chances indicava. Não confundir com xG diferencial, que compara ataque e defesa."
                            ],
                            "synonyms": [
                                "gols menos xG",
                                "sobreperformance ofensiva",
                                "finalização acima do esperado",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    100.0 * SUM(vw_selecao_partida.xg_for)
                                    /
                                    NULLIF(
                                        SUM(vw_selecao_partida.xg_for)
                                        + SUM(vw_selecao_partida.xg_against),
                                        0
                                    )
                                    """
                                )
                            ],
                            "display_name": "Participação no xG da Partida",
                            "instruction": [
                                "Percentual do xG total das partidas que foi produzido pela seleção. Exiba como percentual. Acima de 50% indica que a seleção produziu mais xG do que seus adversários no conjunto analisado."
                            ],
                            "synonyms": [
                                "xG share",
                                "domínio de chances",
                                "percentual do xG",
                                "participação no xG",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_xpts_selecao_partida.expected_points)
                                    """
                                )
                            ],
                            "display_name": "Pontos Esperados (xPts)",
                            "instruction": [
                                "Soma dos pontos esperados, estimados por um modelo de Poisson independente a partir do xG das duas seleções. Não é uma métrica oficial da FIFA — explique isso ao apresentá-la."
                            ],
                            "synonyms": [
                                "xPts",
                                "pontos esperados",
                                "expected points",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_xpts_selecao_partida.actual_points)
                                    -
                                    SUM(vw_xpts_selecao_partida.expected_points)
                                    """
                                )
                            ],
                            "display_name": "Pontos Acima do Esperado",
                            "instruction": [
                                "Pontos reais menos pontos esperados (xPts). Valores positivos sugerem que a seleção pontuou mais do que o xG previa, o que costuma ser lido como eficiência ou sorte; valores negativos, o contrário."
                            ],
                            "synonyms": [
                                "pontos acima do xPts",
                                "sorte",
                                "sobreperformance",
                                "pontos além do esperado",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(vw_pontos_recuperados.recovered_points)
                                    """
                                )
                            ],
                            "display_name": "Pontos Recuperados",
                            "instruction": [
                                "Mede o poder de reação da seleção: 3 pontos quando esteve perdendo e venceu, 1 quando esteve perdendo e empatou, e 0 quando nunca esteve atrás no placar. Métrica própria deste projeto."
                            ],
                            "synonyms": [
                                "poder de reação",
                                "viradas",
                                "pontos de virada",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    AVG(vw_estabilidade_escalacao.lineup_stability_pct)
                                    """
                                )
                            ],
                            "display_name": "Estabilidade da Escalação (%)",
                            "instruction": [
                                "Percentual médio de titulares mantidos em relação à partida anterior. A primeira partida de cada seleção tem valor nulo e não entra na média. Valores altos indicam time-base fixo; valores baixos indicam rodízio."
                            ],
                            "synonyms": [
                                "estabilidade da escalação",
                                "rodízio de titulares",
                                "manutenção do time-base",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(
                                        CASE
                                            WHEN vw_selecao_partida.points = 3
                                                 AND vw_selecao_partida.team_rank
                                                     > vw_selecao_partida.opponent_rank
                                            THEN
                                                vw_selecao_partida.team_rank
                                                - vw_selecao_partida.opponent_rank

                                            WHEN vw_selecao_partida.points = 1
                                                 AND vw_selecao_partida.team_rank
                                                     > vw_selecao_partida.opponent_rank
                                            THEN
                                                0.5 * (
                                                    vw_selecao_partida.team_rank
                                                    - vw_selecao_partida.opponent_rank
                                                )

                                            ELSE 0
                                        END
                                    )
                                    """
                                )
                            ],
                            "display_name": "Índice de Zebra",
                            "instruction": [
                                "Métrica própria deste projeto, não oficial. A vitória de uma seleção pior ranqueada vale a diferença entre os rankings; o empate do azarão vale metade dessa diferença; o favorito não pontua. Quanto maior o índice, mais a seleção surpreendeu."
                            ],
                            "synonyms": [
                                "zebrômetro",
                                "índice de zebra",
                                "surpresas",
                                "azarão",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    AVG(ft_estatisticas_equipe.possession_pct)
                                    """
                                )
                            ],
                            "display_name": "Posse de Bola Média (%)",
                            "instruction": [
                                "Média do percentual de posse de bola da seleção nas partidas consideradas. Exiba com o símbolo % e uma casa decimal. Agrupe por seleção, nunca por partida sem filtrar o time, já que a tabela tem duas linhas por jogo."
                            ],
                            "synonyms": [
                                "posse média",
                                "média de posse",
                                "domínio de bola",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    100.0 * SUM(ft_estatisticas_equipe.shots_on_target)
                                    /
                                    NULLIF(SUM(ft_estatisticas_equipe.total_shots), 0)
                                    """
                                )
                            ],
                            "display_name": "Precisão de Finalização (%)",
                            "instruction": [
                                "Percentual de finalizações que foram no alvo. Exiba com o símbolo % e uma casa decimal. Use para comparar a qualidade das finalizações entre seleções."
                            ],
                            "synonyms": [
                                "precisão de chute",
                                "chutes certos",
                                "pontaria",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    90.0
                                    * SUM(ft_estatisticas_jogador.goals + ft_estatisticas_jogador.assists)
                                    /
                                    NULLIF(SUM(ft_estatisticas_jogador.minutes_played), 0)
                                    """
                                )
                            ],
                            "display_name": "Participações em Gols por 90",
                            "instruction": [
                                "Gols mais assistências a cada 90 minutos em campo. Em rankings individuais, agrupe por player_id e exiba player_name via dim_jogadores. Aplique sempre um corte de minutagem mínima para evitar distorções, e informe o corte usado na resposta."
                            ],
                            "synonyms": [
                                "G+A por 90",
                                "gols e assistências por 90",
                                "participações por 90",
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                textwrap.dedent(
                                    """\
                                    SUM(ft_estatisticas_jogador.goals + ft_estatisticas_jogador.assists)
                                    """
                                )
                            ],
                            "display_name": "Participações em Gols",
                            "instruction": [
                                "Soma de gols e assistências do jogador no torneio. Use para rankings de participação ofensiva em números absolutos, complementando o ranking por 90 minutos."
                            ],
                            "synonyms": [
                                "gols mais assistências",
                                "G+A",
                                "participação em gols",
                            ],
                        },
                    ],
                },
            },
        },
    }
    return _sort_id_lists(data)