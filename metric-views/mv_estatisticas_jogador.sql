-- Metric View: Estatisticas individuais de jogadores no torneio
-- Fonte: fifa_world_cup_2026.gold.ft_estatisticas_jogador
-- Joins: jogador e selecao

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_estatisticas_jogador
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Estatisticas individuais acumuladas de cada jogador no torneio inteiro. Use para rankings de artilharia, assistencias e nota media."
source: >
  SELECT 
    ft.*,
    jogador.player_name AS jogador_nome,
    jogador.club_team AS jogador_clube,
    selecao.team_name AS selecao_nome
  FROM fifa_world_cup_2026.gold.ft_estatisticas_jogador ft
  LEFT JOIN fifa_world_cup_2026.gold.dim_jogadores jogador ON ft.player_id = jogador.player_id
  LEFT JOIN fifa_world_cup_2026.gold.dim_selecoes selecao ON ft.team_id = selecao.team_id

dimensions:
  - name: Jogador
    expr: jogador_nome
    comment: "Nome do jogador."
  - name: Selecao
    expr: selecao_nome
    comment: "Selecao do jogador."
  - name: Posicao
    expr: position
    comment: "Posicao do jogador (GK, DEF, MID, FWD) conforme reportada nesta fonte de estatisticas."
  - name: Clube
    expr: jogador_clube
    comment: "Clube onde o jogador atua profissionalmente."

measures:
  - name: Total de Gols
    expr: SUM(goals)
    comment: "Soma de gols marcados no torneio (artilharia)."
  - name: Total de Assistencias
    expr: SUM(assists)
    comment: "Soma de assistencias para gol dadas no torneio."
  - name: Total de Finalizacoes
    expr: SUM(shots)
    comment: "Soma de finalizacoes tentadas no torneio."
  - name: Total de Finalizacoes no Alvo
    expr: SUM(shots_on_target)
    comment: "Soma de finalizacoes no alvo feitas no torneio."
  - name: Total de Cartoes Amarelos
    expr: SUM(yellow_cards)
    comment: "Soma de cartoes amarelos recebidos no torneio."
  - name: Total de Cartoes Vermelhos
    expr: SUM(red_cards)
    comment: "Soma de cartoes vermelhos recebidos no torneio."
  - name: Total de Penaltis Convertidos
    expr: SUM(penalty_goals)
    comment: "Soma de gols marcados de penalti."
  - name: Total de Gols Contra
    expr: SUM(own_goals)
    comment: "Soma de gols contra marcados."
  - name: Total de Jogos Sem Sofrer Gol
    expr: SUM(clean_sheets)
    comment: "Soma de jogos sem sofrer gols (clean sheets), aplicavel principalmente a goleiros e defensores."
  - name: Total de Defesas
    expr: SUM(saves)
    comment: "Soma de defesas realizadas, aplicavel principalmente a goleiros."
  - name: Media de Nota
    expr: AVG(average_rating)
    comment: "Media da nota de desempenho no torneio (escala tipica 0-10)."
  - name: Total de Minutos Jogados
    expr: SUM(minutes_played)
    comment: "Soma de minutos jogados no torneio."
$$;
