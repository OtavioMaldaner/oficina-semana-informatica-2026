-- Metric View: Escalacoes (lineups) das partidas
-- Fonte: fifa_world_cup_2026.gold.ft_escalacoes
-- Joins: jogador, selecao e partida

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_escalacoes
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Escalacoes titulares e reservas por partida. Use para perguntas sobre quem jogou, tempo de jogo e formacao tatica."
source: fifa_world_cup_2026.gold.ft_escalacoes

joins:
  - name: jogador
    source: fifa_world_cup_2026.gold.dim_jogadores
    on: source.player_id = jogador.player_id
  - name: selecao
    source: fifa_world_cup_2026.gold.dim_selecoes
    on: source.team_id = selecao.team_id
  - name: partida
    source: fifa_world_cup_2026.gold.ft_partidas
    on: source.match_id = partida.match_id

dimensions:
  - name: Jogador
    expr: jogador.player_name
    comment: "Jogador escalado."
  - name: Selecao
    expr: selecao.team_name
    comment: "Selecao do jogador nesta partida."
  - name: Posicao Tatica
    expr: tactical_position
    comment: "Posicao tatica ocupada pelo jogador nesta partida especifica (GK, DEF, MID, FWD)."
  - name: Foi Titular
    expr: is_starting_xi
    comment: "True = jogador comecou a partida no time titular. False = jogador ficou no banco de reservas."
  - name: Data da Partida
    expr: partida.date
    comment: "Data da partida em que a escalacao ocorreu."

measures:
  - name: Total de Escalacoes
    expr: COUNT(1)
    comment: "Quantidade de registros de escalacao considerados (um por jogador por partida)."
  - name: Total de Titularidades
    expr: COUNT(1) FILTER (WHERE is_starting_xi = true)
    comment: "Quantidade de vezes que jogadores comecaram partidas como titulares."
  - name: Total de Entradas como Reserva
    expr: COUNT(1) FILTER (WHERE is_starting_xi = false AND minutes_played > 0)
    comment: "Quantidade de vezes que jogadores entraram em campo vindo do banco de reservas."
  - name: Minutos Totais Jogados
    expr: SUM(minutes_played)
    comment: "Soma dos minutos jogados por todos os jogadores considerados."
  - name: Media de Minutos por Escalacao
    expr: AVG(minutes_played)
    comment: "Media de minutos jogados por escalacao (titular ou reserva)."
$$;
