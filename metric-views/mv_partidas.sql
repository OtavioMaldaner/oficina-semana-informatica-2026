-- Metric View: Partidas da Copa do Mundo 2026 (tabela fato principal)
-- Fonte: fifa_world_cup_2026.gold.ft_partidas
-- Joins: selecao mandante, selecao visitante, estadio, fase e arbitro

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_partidas
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Metrica principal de partidas: placares, xG, resultado e contexto (selecoes, estadio, fase, arbitro). Ponto de partida para perguntas gerais sobre jogos."
source: >
  SELECT 
    ft.match_id,
    ft.date,
    ft.status,
    ft.home_score,
    ft.away_score,
    ft.home_xg,
    ft.away_xg,
    mandante.team_name AS selecao_mandante,
    mandante.confederation AS confederacao_mandante,
    visitante.team_name AS selecao_visitante,
    visitante.confederation AS confederacao_visitante,
    estadio.stadium_name AS estadio_nome,
    estadio.city AS cidade,
    estadio.country AS pais_sede,
    etapa.stage_name AS fase_nome,
    etapa.is_knockout AS e_mata_mata,
    arbitro.referee_name AS arbitro_nome
  FROM fifa_world_cup_2026.gold.ft_partidas ft
  LEFT JOIN fifa_world_cup_2026.gold.dim_selecoes mandante ON ft.home_team_id = mandante.team_id
  LEFT JOIN fifa_world_cup_2026.gold.dim_selecoes visitante ON ft.away_team_id = visitante.team_id
  LEFT JOIN fifa_world_cup_2026.gold.dim_estadios estadio ON ft.venue_id = estadio.venue_id
  LEFT JOIN fifa_world_cup_2026.gold.dim_etapas etapa ON ft.stage_id = etapa.stage_id
  LEFT JOIN fifa_world_cup_2026.gold.dim_arbitros arbitro ON ft.referee_id = arbitro.referee_id

dimensions:
  - name: Data da Partida
    expr: date
    comment: "Data em que a partida foi realizada."
  - name: Status
    expr: status
    comment: "Status atual da partida (ex: Completed, In Play, Scheduled)."
  - name: Selecao Mandante
    expr: selecao_mandante
    comment: "Nome da selecao mandante (time da casa)."
  - name: Selecao Visitante
    expr: selecao_visitante
    comment: "Nome da selecao visitante (time de fora)."
  - name: Confederacao Mandante
    expr: confederacao_mandante
    comment: "Confederacao continental da selecao mandante."
  - name: Confederacao Visitante
    expr: confederacao_visitante
    comment: "Confederacao continental da selecao visitante."
  - name: Estadio
    expr: estadio_nome
    comment: "Nome do estadio onde a partida foi realizada."
  - name: Cidade
    expr: cidade
    comment: "Cidade onde a partida foi realizada."
  - name: Pais Sede
    expr: pais_sede
    comment: "Pais sede da partida (USA, Mexico ou Canada)."
  - name: Fase
    expr: fase_nome
    comment: "Fase do torneio em que a partida ocorreu (ex: Group Stage, Round of 16, Final)."
  - name: E Mata-Mata
    expr: e_mata_mata
    comment: "True = partida de fase eliminatoria. False = partida de fase de grupos."
  - name: Arbitro
    expr: arbitro_nome
    comment: "Nome do arbitro principal da partida."
  - name: Resultado
    expr: |-
      CASE
        WHEN home_score > away_score THEN 'Vitoria do Mandante'
        WHEN home_score < away_score THEN 'Vitoria do Visitante'
        ELSE 'Empate'
      END
    comment: "Resultado do jogo do ponto de vista do mandante, calculado a partir do placar."

measures:
  - name: Total de Partidas
    expr: COUNT(1)
    comment: "Quantidade de partidas consideradas."
  - name: Total de Gols Mandante
    expr: SUM(home_score)
    comment: "Soma dos gols marcados pelas selecoes mandantes."
  - name: Total de Gols Visitante
    expr: SUM(away_score)
    comment: "Soma dos gols marcados pelas selecoes visitantes."
  - name: Total de Gols
    expr: SUM(home_score) + SUM(away_score)
    comment: "Soma de todos os gols marcados (mandantes e visitantes) nas partidas consideradas."
  - name: Media de Gols por Partida
    expr: AVG(home_score + away_score)
    comment: "Media de gols marcados (soma dos dois times) por partida."
  - name: xG Medio Mandante
    expr: AVG(home_xg)
    comment: "Media do Expected Goals (xG) das selecoes mandantes."
  - name: xG Medio Visitante
    expr: AVG(away_xg)
    comment: "Media do Expected Goals (xG) das selecoes visitantes."
  - name: Total de Vitorias do Mandante
    expr: COUNT(1) FILTER (WHERE home_score > away_score)
    comment: "Quantidade de partidas vencidas pela selecao mandante."
  - name: Total de Empates
    expr: COUNT(1) FILTER (WHERE home_score = away_score)
    comment: "Quantidade de partidas que terminaram empatadas."
  - name: Total de Vitorias do Visitante
    expr: COUNT(1) FILTER (WHERE home_score < away_score)
    comment: "Quantidade de partidas vencidas pela selecao visitante."
$$;