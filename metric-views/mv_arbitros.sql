-- Metric View: Arbitros da Copa do Mundo 2026
-- Fonte: fifa_world_cup_2026.gold.dim_arbitros

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_arbitros
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Metricas sobre os arbitros principais do torneio, incluindo rigor historico de arbitragem."
source: fifa_world_cup_2026.gold.dim_arbitros

dimensions:
  - name: Arbitro
    expr: referee_name
    comment: "Nome completo do arbitro principal."
  - name: Pais do Arbitro
    expr: country
    comment: "Pais de origem/federacao do arbitro."
  - name: Media Historica de Cartoes
    expr: avg_cards_per_game
    comment: "Media historica de cartoes (amarelos + vermelhos) mostrados por partida por este arbitro."

measures:
  - name: Total de Arbitros
    expr: COUNT(1)
    comment: "Quantidade de arbitros considerados."
  - name: Media Geral de Cartoes por Jogo
    expr: AVG(avg_cards_per_game)
    comment: "Media geral de cartoes por jogo entre os arbitros considerados."
  - name: Arbitro Mais Rigoroso Media
    expr: MAX(avg_cards_per_game)
    comment: "Maior media historica de cartoes por jogo entre os arbitros considerados."
$$;
