-- Metric View: Eventos das partidas (gols, cartoes, VAR, assistencias)
-- Fonte: fifa_world_cup_2026.gold.ft_eventos
-- Joins: partida, selecao e jogador

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_eventos
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Eventos ocorridos dentro das partidas, minuto a minuto. Use para perguntas de disciplina (cartoes), artilharia por minuto e uso de VAR."
source: fifa_world_cup_2026.gold.ft_eventos

joins:
  - name: partida
    source: fifa_world_cup_2026.gold.ft_partidas
    on: source.match_id = partida.match_id
  - name: selecao
    source: fifa_world_cup_2026.gold.dim_selecoes
    on: source.team_id = selecao.team_id
  - name: jogador
    source: fifa_world_cup_2026.gold.dim_jogadores
    on: source.player_id = jogador.player_id

dimensions:
  - name: Tipo de Evento
    expr: event_type
    comment: "Tipo do evento: Goal, Assist, Yellow Card, Red Card, VAR Review, Penalty Shootout Goal ou Penalty Shootout Miss."
  - name: Minuto
    expr: minute
    comment: "Minuto de jogo em que o evento aconteceu (pode ultrapassar 90 em acrescimos/prorrogacao)."
  - name: Faixa de Minuto
    expr: |-
      CASE
        WHEN minute <= 15 THEN '0-15'
        WHEN minute <= 30 THEN '16-30'
        WHEN minute <= 45 THEN '31-45'
        WHEN minute <= 60 THEN '46-60'
        WHEN minute <= 75 THEN '61-75'
        WHEN minute <= 90 THEN '76-90'
        ELSE '90+ (acrescimos/prorrogacao)'
      END
    comment: "Agrupamento do minuto em blocos de 15 minutos, util para analisar ritmo de jogo."
  - name: Selecao
    expr: selecao.team_name
    comment: "Selecao envolvida no evento."
  - name: Jogador
    expr: jogador.player_name
    comment: "Jogador envolvido no evento."
  - name: Data da Partida
    expr: partida.date
    comment: "Data da partida em que o evento ocorreu."

measures:
  - name: Total de Eventos
    expr: COUNT(1)
    comment: "Quantidade total de eventos considerados."
  - name: Total de Gols
    expr: COUNT(1) FILTER (WHERE event_type = 'Goal')
    comment: "Quantidade de gols marcados."
  - name: Total de Assistencias
    expr: COUNT(1) FILTER (WHERE event_type = 'Assist')
    comment: "Quantidade de assistencias para gol."
  - name: Total de Cartoes Amarelos
    expr: COUNT(1) FILTER (WHERE event_type = 'Yellow Card')
    comment: "Quantidade de cartoes amarelos mostrados."
  - name: Total de Cartoes Vermelhos
    expr: COUNT(1) FILTER (WHERE event_type = 'Red Card')
    comment: "Quantidade de cartoes vermelhos mostrados."
  - name: Total de Revisoes VAR
    expr: COUNT(1) FILTER (WHERE event_type = 'VAR Review')
    comment: "Quantidade de revisoes de VAR realizadas."
$$;
