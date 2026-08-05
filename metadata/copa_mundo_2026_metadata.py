import textwrap
import uuid


def get_copa_mundo_2026_metadata():
    return {
        "title": "FIFA World Cup 2026 Analysis",
        "description": textwrap.dedent(
            """\
                This Agent provides comprehensive analysis of the FIFA World Cup 2026, allowing exploration of teams, players, matches, venues, statistics, and key events for business and performance insights.

                **Capabilities:**
                - Analyze and compare national teams, grouped by FIFA ranking, confederation, group, and pre-tournament metrics.
                - Track player profiles, club affiliations, age, height, positions, and accumulated tournament statistics (gols, assistências, cartões, minutos jogados).
                - Examine match details including dates, scores, expected goals (xG), stadium, altitude, phase of the tournament, and referee.
                - Review detailed in-game events (gols, cartões, assistências, VAR) by minute, team, and player to reconstruct match timelines.
                - Evaluate team performance per match (posse de bola, finalizações, escanteios, faltas, impedimentos, eficiência) and identify MVPs.
                - Investigate tactical formations, starting lineups, substitutions, and playing time per athlete and match.
                - Filter analyses by tournament phase (grupo vs. mata-mata), venue, altitude, and more, following official business rules.
                - Explore historical referee rigor through average cards per game and analyze its impact on matches.

                **Limitations:**
                - Cannot answer questions about details not present in the supplied tables (e.g., ticket prices, TV ratings, individual training sessions).
                - Does not provide real-time updates; data reflects the latest verified or available date in each record.
                - Advanced player tracking (e.g., heat maps, running distance) or financial/marketing data is not included.
                - For event-level minute-by-minute stats, use only for granular needs; for aggregated tournament numbers, always prefer summary tables.
                - Not able to supply information about teams, players, or referees not included in the official tournament dataset.
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
                                    'Média histórica de cartões (amarelos + vermelhos) mostrados por partida por este árbitro — indicador do "rigor" do árbitro.'
                                ],
                                "synonyms": [
                                    "rigor do árbitro",
                                    "cartões por partida",
                                    "severidade",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Média de Cartões por Jogo",
                            },
                            {
                                "column_name": "country",
                                "description": ["País de origem/federação do árbitro."],
                                "synonyms": [
                                    "nacionalidade do árbitro",
                                    "federação de origem",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "País do Árbitro",
                            },
                            {
                                "column_name": "referee_id",
                                "description": ["Identificador único do árbitro."],
                                "synonyms": ["código do árbitro"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Árbitro",
                            },
                            {
                                "column_name": "referee_name",
                                "description": ["Nome completo do árbitro principal."],
                                "synonyms": ["juiz", "árbitro principal"],
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
                                    "Capacidade máxima oficial de público."
                                ],
                                "synonyms": [
                                    "lotação",
                                    "número de lugares",
                                    "tamanho do estádio",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Capacidade",
                            },
                            {
                                "column_name": "city",
                                "description": [
                                    "Cidade onde o estádio está localizado."
                                ],
                                "synonyms": ["município", "localidade"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Cidade",
                            },
                            {
                                "column_name": "country",
                                "description": ["Pais sede. "],
                                "synonyms": ["nação sede", "país anfitrião"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "País Sede",
                            },
                            {
                                "column_name": "elevation_meters",
                                "description": [
                                    "Altitude do estádio em relação ao nível do mar, em metros."
                                ],
                                "synonyms": ["elevação", "altura em relação ao mar"],
                                "enable_format_assistance": True,
                                "display_name": "Altitude",
                            },
                            {
                                "column_name": "stadium_name",
                                "description": ["Nome oficial do estádio sede."],
                                "synonyms": ["arena", "sede", "local do jogo"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Estádio",
                            },
                            {
                                "column_name": "venue_id",
                                "description": ["Identificador único do estádio."],
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
                                    "Indica se é fase eliminatória (verdadeiro) ou fase de grupos (falso)."
                                ],
                                "synonyms": ["eliminatória", "mata-mata"],
                                "enable_format_assistance": True,
                                "display_name": "É Mata-Mata",
                            },
                            {
                                "column_name": "stage_id",
                                "description": [
                                    "Identificador único da fase do torneio."
                                ],
                                "synonyms": ["código da fase"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Fase",
                            },
                            {
                                "column_name": "stage_name",
                                "description": ["Nome da fase"],
                                "synonyms": ["etapa", "rodada", "estágio do torneio"],
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
                                    "Clube onde o jogador atua profissionalmente."
                                ],
                                "synonyms": ["time do jogador", "clube de origem"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Clube",
                            },
                            {
                                "column_name": "date_of_birth",
                                "synonyms": ["nascimento", "idade do jogador"],
                                "enable_format_assistance": True,
                                "display_name": "Data de Nascimento",
                            },
                            {
                                "column_name": "height_cm",
                                "description": ["Altura do jogador em centímetros."],
                                "synonyms": ["estatura", "altura do atleta"],
                                "enable_format_assistance": True,
                                "display_name": "Altura (cm)",
                            },
                            {
                                "column_name": "player_id",
                                "description": ["Identificador único do atleta."],
                                "synonyms": ["código do jogador"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "player_name",
                                "synonyms": ["atleta", "craque", "nome do atleta"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Jogador",
                            },
                            {
                                "column_name": "position",
                                "description": ["Posição tática do jogador em campo"],
                                "synonyms": ["função em campo", "posição tática"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Posição",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Liga o jogador à seleção que ele defende."
                                ],
                                "synonyms": ["time do jogador", "seleção do atleta"],
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
                                "description": ["Confederação continental do país"],
                                "synonyms": ["continente", "federação continental"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Confederação",
                            },
                            {
                                "column_name": "fifa_code",
                                "description": ["Código de 3 letras da FIFA"],
                                "synonyms": [
                                    "sigla",
                                    "abreviação",
                                    "código de 3 letras",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Código FIFA",
                            },
                            {
                                "column_name": "fifa_ranking_pre_tournament",
                                "description": [
                                    "Posição no ranking mundial da FIFA antes da Copa. Menor = mais forte."
                                ],
                                "synonyms": [
                                    "ranking",
                                    "posição no ranking",
                                    "favoritismo",
                                ],
                                "enable_format_assistance": True,
                                "display_name": "Ranking FIFA Pré-Torneio",
                            },
                            {
                                "column_name": "group_letter",
                                "description": ["Letra do grupo na fase de grupos"],
                                "synonyms": ["chave", "letra do grupo"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Grupo",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Identificador único numérico da seleção."
                                ],
                                "synonyms": ["id do time", "código do time"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "team_name",
                                "description": ["Nome oficial do país/seleção"],
                                "synonyms": ["time", "país", "nação", "equipe"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_escalacoes",
                        "column_configs": [
                            {
                                "column_name": "is_starting_xi",
                                "description": [
                                    "Verdadeiro se o jogador começou como titular; falso se ficou no banco."
                                ],
                                "synonyms": ["titular", "começou jogando"],
                                "enable_format_assistance": True,
                                "display_name": "É Titular",
                            },
                            {
                                "column_name": "lineup_id",
                                "description": [
                                    "Identificador único do registro de escalação."
                                ],
                                "synonyms": ["código da escalação"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Escalação",
                            },
                            {
                                "column_name": "match_id",
                                "description": ["Partida a que a escalação se refere."],
                                "synonyms": ["jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "minutes_played",
                                "description": [
                                    "Minutos que o jogador efetivamente atuou nesta partida."
                                ],
                                "synonyms": ["tempo em campo", "minutagem"],
                                "enable_format_assistance": True,
                                "display_name": "Minutos Jogados",
                            },
                            {
                                "column_name": "player_id",
                                "description": ["Jogador escalado."],
                                "synonyms": ["atleta escalado"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "tactical_position",
                                "description": [
                                    "Posição tática ocupada pelo jogador nesta partida específica."
                                ],
                                "synonyms": [
                                    "função tática",
                                    "posição em campo no jogo",
                                ],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Posição na Partida",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção do jogador nesta partida."],
                                "synonyms": ["time do jogador na partida"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_equipe",
                        "column_configs": [
                            {
                                "column_name": "corners",
                                "description": ["Número de escanteios cobrados."],
                                "synonyms": ["cantos", "córners"],
                                "enable_format_assistance": True,
                                "display_name": "Escanteios",
                            },
                            {
                                "column_name": "data_source",
                                "description": [
                                    "Fonte de onde a estatística foi coletada."
                                ],
                                "synonyms": ["origem do dado"],
                                "exclude": True,
                                "display_name": "Fonte dos Dados",
                            },
                            {
                                "column_name": "fouls",
                                "description": ["Número de faltas cometidas."],
                                "synonyms": ["infrações"],
                                "enable_format_assistance": True,
                                "display_name": "Faltas",
                            },
                            {
                                "column_name": "last_updated",
                                "description": [
                                    "Data da última atualização deste registro."
                                ],
                                "synonyms": ["data de atualização"],
                                "exclude": True,
                                "display_name": "Última Atualização",
                            },
                            {
                                "column_name": "match_id",
                                "description": [
                                    "Partida a que a estatística se refere."
                                ],
                                "synonyms": ["jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "offsides",
                                "description": [
                                    "Número de vezes em posição de impedimento."
                                ],
                                "synonyms": ["posições de impedimento"],
                                "enable_format_assistance": True,
                                "display_name": "Impedimentos",
                            },
                            {
                                "column_name": "player_of_the_match",
                                "description": ["Jogador eleito o melhor em campo."],
                                "synonyms": ["craque do jogo", "MVP da partida"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Melhor em Campo",
                            },
                            {
                                "column_name": "possession_pct",
                                "description": [
                                    "Percentual de posse de bola da seleção na partida."
                                ],
                                "synonyms": ["posse", "domínio de bola"],
                                "enable_format_assistance": True,
                                "display_name": "Posse de Bola (%)",
                            },
                            {
                                "column_name": "saves",
                                "description": [
                                    "Número de defesas realizadas pelo goleiro."
                                ],
                                "synonyms": ["defesas do goleiro"],
                                "enable_format_assistance": True,
                                "display_name": "Defesas",
                            },
                            {
                                "column_name": "shots_on_target",
                                "description": ["Número de finalizações no alvo."],
                                "synonyms": ["chutes certos", "chutes a gol"],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações no Alvo",
                            },
                            {
                                "column_name": "team_id",
                                "description": [
                                    "Seleção a que a estatística pertence."
                                ],
                                "synonyms": ["time"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "total_shots",
                                "description": [
                                    "Número total de finalizações realizadas."
                                ],
                                "synonyms": ["chutes", "tentativas de gol"],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_estatisticas_jogador",
                        "column_configs": [
                            {
                                "column_name": "assists",
                                "description": ["Total de assistências para gol."],
                                "synonyms": ["passes para gol"],
                                "enable_format_assistance": True,
                                "display_name": "Assistências",
                            },
                            {
                                "column_name": "average_rating",
                                "description": [
                                    "Nota média de desempenho no torneio (escala 0-10)."
                                ],
                                "synonyms": ["avaliação média", "rating médio"],
                                "enable_format_assistance": True,
                                "display_name": "Nota Média",
                            },
                            {
                                "column_name": "clean_sheets",
                                "description": ["Jogos em que não sofreu gols"],
                                "synonyms": ["clean sheets"],
                                "enable_format_assistance": True,
                                "display_name": "Jogos sem Sofrer Gol",
                            },
                            {"column_name": "data_source", "exclude": True},
                            {
                                "column_name": "goals",
                                "description": ["Total de gols marcados no torneio."],
                                "synonyms": ["artilharia", "gols marcados"],
                                "enable_format_assistance": True,
                                "display_name": "Gols",
                            },
                            {
                                "column_name": "goals_conceded",
                                "description": ["Total de gols sofridos em campo."],
                                "synonyms": ["gols tomados"],
                                "enable_format_assistance": True,
                                "display_name": "Gols Sofridos",
                            },
                            {"column_name": "last_verified", "exclude": True},
                            {
                                "column_name": "matches_played",
                                "description": [
                                    "Partidas em que o jogador entrou em campo no torneio."
                                ],
                                "synonyms": ["jogos disputados"],
                                "enable_format_assistance": True,
                                "display_name": "Partidas Jogadas",
                            },
                            {
                                "column_name": "matches_started",
                                "description": [
                                    "Partidas em que o jogador foi titular."
                                ],
                                "synonyms": ["jogos titular"],
                                "enable_format_assistance": True,
                                "display_name": "Partidas como Titular",
                            },
                            {
                                "column_name": "minutes_played",
                                "description": ["Total de minutos jogados no torneio."],
                                "synonyms": ["tempo total em campo"],
                                "enable_format_assistance": True,
                                "display_name": "Minutos Jogados",
                            },
                            {
                                "column_name": "own_goals",
                                "enable_format_assistance": True,
                            },
                            {
                                "column_name": "penalty_goals",
                                "description": ["Total de gols marcados de pênalti."],
                                "synonyms": ["pênaltis convertidos"],
                                "enable_format_assistance": True,
                                "display_name": "Gols de Pênalti",
                            },
                            {
                                "column_name": "player_id",
                                "description": [
                                    "Jogador a que as estatísticas se referem."
                                ],
                                "synonyms": ["atleta"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "position",
                                "description": [
                                    "Posição do jogador conforme esta fonte de estatísticas."
                                ],
                                "synonyms": ["função em campo"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Posição",
                            },
                            {
                                "column_name": "red_cards",
                                "description": [
                                    "Total de cartões vermelhos recebidos."
                                ],
                                "synonyms": ["vermelhos", "expulsões"],
                                "enable_format_assistance": True,
                                "display_name": "Cartões Vermelhos",
                            },
                            {
                                "column_name": "saves",
                                "description": [
                                    "Total de defesas realizadas (goleiros)."
                                ],
                                "synonyms": ["defesas do goleiro"],
                                "enable_format_assistance": True,
                                "display_name": "Defesas",
                            },
                            {
                                "column_name": "shots",
                                "description": ["Total de finalizações tentadas."],
                                "synonyms": ["chutes tentados"],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações",
                            },
                            {
                                "column_name": "shots_on_target",
                                "description": ["Total de finalizações no alvo."],
                                "synonyms": ["chutes certos"],
                                "enable_format_assistance": True,
                                "display_name": "Finalizações no Alvo",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção do jogador."],
                                "synonyms": ["time do jogador"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                            {
                                "column_name": "yellow_cards",
                                "description": ["Total de cartões amarelos recebidos."],
                                "synonyms": ["amarelos"],
                                "enable_format_assistance": True,
                                "display_name": "Cartões Amarelos",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_eventos",
                        "column_configs": [
                            {
                                "column_name": "event_id",
                                "description": ["Identificador único do evento."],
                                "synonyms": ["código do evento"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Evento",
                            },
                            {
                                "column_name": "event_type",
                                "synonyms": ["categoria do evento", "o que aconteceu"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Tipo de Evento",
                            },
                            {
                                "column_name": "match_id",
                                "description": ["Partida em que o evento ocorreu."],
                                "synonyms": ["jogo do evento"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "minute",
                                "description": [
                                    "Minuto de jogo em que o evento aconteceu."
                                ],
                                "synonyms": ["tempo do evento", "minutagem"],
                                "enable_format_assistance": True,
                                "display_name": "Minuto",
                            },
                            {
                                "column_name": "player_id",
                                "description": ["Jogador envolvido no evento."],
                                "synonyms": ["atleta envolvido"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Jogador",
                            },
                            {
                                "column_name": "team_id",
                                "description": ["Seleção envolvida no evento."],
                                "synonyms": ["time envolvido"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Seleção",
                            },
                        ],
                    },
                    {
                        "identifier": "fifa_world_cup_2026.gold.ft_partidas",
                        "column_configs": [
                            {
                                "column_name": "away_score",
                                "description": [
                                    "Gols marcados pela seleção visitante."
                                ],
                                "synonyms": ["placar visitante", "gols fora"],
                                "enable_format_assistance": True,
                                "display_name": "Gols do Visitante",
                            },
                            {
                                "column_name": "away_team_id",
                                "description": ["Seleção visitante."],
                                "synonyms": ["time visitante", "time de fora"],
                                "enable_format_assistance": True,
                                "display_name": "ID Seleção Visitante",
                            },
                            {
                                "column_name": "away_xg",
                                "description": [
                                    "Expected Goals (gols esperados) do visitante."
                                ],
                                "synonyms": ["gols esperados do visitante"],
                                "enable_format_assistance": True,
                                "display_name": "xG do Visitante",
                            },
                            {
                                "column_name": "date",
                                "synonyms": ["dia do jogo"],
                                "enable_format_assistance": True,
                                "display_name": "Data da Partida",
                            },
                            {
                                "column_name": "home_score",
                                "description": ["Gols marcados pela seleção mandante."],
                                "synonyms": ["placar da casa", "gols em casa"],
                                "enable_format_assistance": True,
                                "display_name": "Gols do Mandante",
                            },
                            {
                                "column_name": "home_team_id",
                                "description": ["Seleção mandante (time da casa)."],
                                "synonyms": ["time da casa", "mandante"],
                                "enable_format_assistance": True,
                                "display_name": "ID Seleção Mandante",
                            },
                            {
                                "column_name": "home_xg",
                                "description": [
                                    "Expected Goals (gols esperados) do mandante."
                                ],
                                "synonyms": ["gols esperados da casa"],
                                "enable_format_assistance": True,
                                "display_name": "xG do Mandante",
                            },
                            {
                                "column_name": "kickoff_time_utc",
                                "description": [
                                    "Horário exato do apito inicial, em UTC."
                                ],
                                "synonyms": ["hora do jogo", "horário de início"],
                                "enable_format_assistance": True,
                                "display_name": "Horário (UTC)",
                            },
                            {
                                "column_name": "match_id",
                                "description": ["Identificador único da partida."],
                                "synonyms": ["código do jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Partida",
                            },
                            {
                                "column_name": "referee_id",
                                "description": ["Árbitro principal da partida."],
                                "synonyms": ["juiz da partida"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Árbitro",
                            },
                            {
                                "column_name": "stage_id",
                                "description": [
                                    "Fase do torneio em que a partida ocorreu."
                                ],
                                "synonyms": ["etapa do jogo"],
                                "enable_format_assistance": True,
                                "display_name": "ID da Fase",
                            },
                            {
                                "column_name": "status",
                                "description": ["Status atual do jogo"],
                                "synonyms": ["situação do jogo", "andamento"],
                                "enable_format_assistance": True,
                                "enable_entity_matching": True,
                                "display_name": "Status",
                            },
                            {
                                "column_name": "venue_id",
                                "description": ["Estádio onde ocorreu o jogo."],
                                "synonyms": ["local do jogo", "sede da partida"],
                                "enable_format_assistance": True,
                                "display_name": "ID do Estádio",
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
                                ## Contexto geral
                                * Os dados são da Copa do Mundo 2026 (48 seleções, sediada por EUA, México e Canadá, 11/jun a 19/jul de 2026).
                                * Responda sempre em português, mesmo que a pergunta use termos em inglês (ex: "top scorer" = artilheiro).
                                * "Seleção", "time", "equipe" e "país" são sinônimos e se referem sempre a `dim_selecoes`.
                                
                                ## Qual tabela usar
                                * Para ranking de gols/assistências/cartões de um jogador **no torneio inteiro**, use `ft_estatisticas_jogador` (já é agregado). Só use `ft_eventos` quando a pergunta pedir detalhe minuto a minuto ou de uma partida específica (ex: "em que minuto o Brasil tomou o cartão amarelo contra a Argentina").
                                * Para saber quem jogou uma partida específica (titular ou reserva), use `ft_escalacoes`, não `ft_estatisticas_jogador`.
                                * Para estatísticas de "como" um time jogou uma partida (posse, escanteios, chutes), use `ft_estatisticas_equipe` — nunca tente somar isso a partir de `ft_eventos`.
                                
                                ## Regras de negócio importantes
                                * Em `dim_selecoes.fifa_ranking_pre_tournament`, **menor número = seleção mais forte** (1 é o melhor ranking do mundo). Nunca trate esse número como se "maior fosse melhor".
                                * `ft_partidas` usa `dim_selecoes` duas vezes (dimensão de papel duplo): `home_team_id` é a seleção mandante, `away_team_id` é a visitante. Ao perguntar sobre "todos os jogos de um time", considere as duas colunas — não filtre só por `home_team_id`.
                                * `ft_estatisticas_equipe` tem **duas linhas por partida** (uma por seleção). Para saber se a linha é do mandante ou do visitante, cruze com `ft_partidas.home_team_id`/`away_team_id`.
                                * `dim_etapas.is_knockout = true` identifica fases eliminatórias (mata-mata); `false` é fase de grupos. Use esse campo para perguntas como "só fases eliminatórias" em vez de tentar adivinhar pelo nome da fase.
                                * `dim_arbitros.avg_cards_per_game` é uma média histórica do árbitro, não da partida específica — não confunda com os cartões realmente mostrados em uma partida (que estão em `ft_eventos`, `event_type = 'Yellow Card'`/`'Red Card'`).
                                * Estatísticas de goleiro (`saves`, `clean_sheets`, `goals_conceded` em `ft_estatisticas_jogador`) só fazem sentido para jogadores com `position = 'GK'`; para outras posições esses campos tendem a ser nulos ou zero.
                                * Se um valor estiver nulo (ex: `player_of_the_match`, campos de goleiro para um jogador de linha), explique que o dado não estava disponível na fonte em vez de tratar como zero.
                                
                                ## Formatação das respostas
                                * `possession_pct` é percentual (0 a 100) — exiba com o símbolo %, não como fração.
                                * Datas devem ser exibidas no formato dia/mês/ano (ex: 14/07/2026).
                                * `home_xg`/`away_xg` (Expected Goals) são números decimais — arredonde para 2 casas ao exibir, mas não arredonde antes de somar ou comparar.
                                * Ao mostrar rankings (artilheiros, seleções, etc.), inclua o nome legível (via join com a dimensão) e nunca só o `_id`.
                                
                                ## Desambiguação
                                * "Gols" sem mais contexto = `ft_estatisticas_jogador.goals` (total do jogador no torneio) ou `ft_partidas.home_score`/`away_score` (gols de uma partida) — escolha conforme o sujeito da pergunta ser jogador ou partida.
                                * "Melhor em campo" ou "MVP" = `ft_estatisticas_equipe.player_of_the_match`.
                                * "Rigor do árbitro" = `dim_arbitros.avg_cards_per_game`, não uma contagem feita a partir de `ft_eventos`.
                                """
                            )
                        ],
                    }
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
                            "dim_jogadores.team_id = dim_selecoes.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga cada jogador convocado à seleção que defende. Use para perguntas sobre elenco de um país, nacionalidade de um jogador, ou médias por seleção (altura, idade). Relação N:1 — 26 jogadores por seleção."
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
                            "ft_partidas.home_team_id = dim_selecoes.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Resolve a seleção mandante. Como dim_selecoes é usada duas vezes (dimensão de papel duplo), este join cobre só o lado mandante."
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
                            "ft_partidas.away_team_id = dim_selecoes_2.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve a seleção visitante. Use sempre junto do anterior quando a pergunta precisar mostrar os dois lados de um confronto (ex: "quem jogou contra quem").'
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
                            "ft_partidas.venue_id = dim_estadios.venue_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a partida ao estádio. Use para perguntas de público, cidade-sede ou altitude (ex: "jogos em estádios acima de 2000m").'
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
                            "ft_partidas.stage_id = dim_etapas.stage_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga a partida à fase do torneio. Use para separar fase de grupos de mata-mata, ou filtrar por fase específica; combine com is_knockout para agrupamentos rápidos."
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
                            "ft_escalacoes.match_id = ft_partidas.match_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a escalação à partida. Necessário pra "quem começou titular em tal jogo" ou pra cruzar escalação com data/fase/estádio.'
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
                            "ft_escalacoes.player_id = dim_jogadores.player_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve nome e atributos do jogador escalado. Use pra "quantas vezes um jogador foi titular" ou pra comparar posição cadastrada com a posição tática usada na partida (tactical_position).'
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
                            "ft_escalacoes.team_id = dim_selecoes.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga a escalação à seleção. Use pra formação tática por seleção (ex: "quantos titulares o Brasil escalou no torneio").'
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
                            "ft_estatisticas_equipe.match_id = ft_partidas.match_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga as estatísticas (posse, finalizações, escanteios) de uma seleção à partida em que ocorreram. Necessário pra relacionar "como" o time jogou com o contexto do jogo.'
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
                            "ft_estatisticas_equipe.team_id = dim_selecoes.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Resolve o nome da seleção. Atenção: essa tabela tem duas linhas por partida (uma por seleção) — o join sozinho não diz quem foi mandante ou visitante; pra isso, cruze também com ft_partidas.home_team_id/away_team_id."
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
                            "ft_estatisticas_jogador.team_id = dim_selecoes.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Liga as estatísticas acumuladas do jogador à seleção que ele defende. Use para rankings agregados por seleção (ex: "seleção com mais gols no total do elenco").'
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
                            "ft_eventos.match_id = ft_partidas.match_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            "Liga cada evento (gol, cartão, assistência, VAR) à partida. Essencial pra reconstruir a linha do tempo de um jogo ou filtrar eventos por fase/data."
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
                            "ft_eventos.team_id = dim_selecoes.team_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve a seleção envolvida no evento. Use pra disciplina por seleção (ex: "cartões vermelhos que o time X recebeu no torneio").'
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
                            "ft_eventos.player_id = dim_jogadores.player_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve o jogador envolvido no evento. Dá pra montar rankings individuais a partir de eventos brutos, mas é redundante com ft_estatisticas_jogador pra perguntas simples de total — prefira ft_estatisticas_jogador para "quem marcou mais gols no total" e reserve ft_eventos para detalhe minuto a minuto.'
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
                            "ft_partidas.referee_id = dim_arbitros.referee_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve o árbitro principal da partida. Necessário para cruzar resultado/cartões com o histórico de rigor do árbitro (ex: "partidas apitadas por árbitros com média de cartões acima de 4").'
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
                            "ft_estatisticas_jogador.player_id = dim_jogadores.player_id",
                            "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--",
                        ],
                        "instruction": [
                            'Resolve nome, posição, clube e demais atributos do jogador a partir das estatísticas do torneio. É o join que traduz "quem tem o player_id com mais gols" em um nome de verdade.'
                        ],
                    },
                ],
                "sql_snippets": {
                    "filters": [
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "dim_etapas.is_knockout = true",
                            ],
                            "display_name": "Fase Eliminatória",
                            "instruction": [
                                'Use quando a pergunta mencionar "mata-mata", "eliminatórias" ou fases específicas de knockout.'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "ft_escalacoes.is_starting_xi = true",
                            ],
                            "display_name": "Titulares",
                            "instruction": [
                                'Use quando a pergunta for sobre quem "jogou desde o início", em oposição a quem só entrou como reserva.'
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "dim_jogadores.position = 'GK'",
                            ],
                            "display_name": "Goleiros",
                            "instruction": [
                                "Use para perguntas sobre defesas, gols sofridos ou clean sheets — esses campos só têm sentido para goleiros."
                            ],
                        },
                    ],
                    "expressions": [
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "CASE",
                                "WHEN ft_partidas.home_score > ft_partidas.away_score THEN 'Vitória do Mandante'",
                                "WHEN ft_partidas.home_score < ft_partidas.away_score THEN 'Vitória do Visitante'",
                                "ELSE 'Empate' END",
                            ],
                            "display_name": "Resultado da Partida",
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "DATEDIFF(YEAR, dim_jogadores.date_of_birth, DATE('2026-06-11'))",
                            ],
                            "display_name": "Faixa Etária",
                            "instruction": [
                                "Calcula a idade do jogador na data de abertura do torneio, não a idade atual"
                            ],
                        },
                    ],
                    "measures": [
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "SUM(ft_partidas.home_score) + SUM(ft_partidas.away_score)",
                            ],
                            "display_name": "Total de Gols do Torneio",
                            "instruction": [
                                "Soma de todos os gols marcados em todas as partidas consideradas."
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "SUM(ft_partidas.home_score) - SUM(ft_partidas.away_score)",
                            ],
                            "display_name": "Saldo de Gols",
                            "instruction": [
                                "Use para saldo de gols de uma seleção específica — filtre por home_team_id/away_team_id antes de agregar."
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "AVG(ft_partidas.home_score + ft_partidas.away_score)",
                            ],
                            "display_name": "Média de Gols por Partida",
                            "instruction": [
                                "Média de gols (dos dois times somados) por jogo."
                            ],
                        },
                        {
                            "id": uuid.uuid4().hex,
                            "sql": [
                                "SUM(ft_partidas.home_score) / NULLIF(SUM(ft_partidas.home_xg), 0)",
                            ],
                            "display_name": "Eficiência Ofensiva (Gols/xG)",
                            "instruction": [
                                "Compara gols reais com gols esperados (xG). Valores acima de 1 indicam finalização acima do esperado."
                            ],
                        },
                    ],
                },
            },
        },
    }
