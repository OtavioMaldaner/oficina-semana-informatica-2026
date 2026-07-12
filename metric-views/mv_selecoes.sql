-- Metric View: Selecoes participantes da Copa do Mundo 2026
-- Fonte: fifa_world_cup_2026.gold.dim_selecoes

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_selecoes
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Metricas e atributos das selecoes classificadas para a Copa de 2026. Use para responder perguntas sobre ranking, grupos e confederacoes."
source: fifa_world_cup_2026.gold.dim_selecoes

dimensions:
  - name: Selecao
    expr: team_name
    comment: "Nome oficial da selecao (ex: Brazil, Argentina)."
  - name: Codigo FIFA
    expr: fifa_code
    comment: "Codigo de 3 letras da FIFA (ex: BRA, ARG)."
  - name: Grupo
    expr: group_letter
    comment: "Letra do grupo da selecao na fase de grupos (A a L)."
  - name: Confederacao
    expr: confederation
    comment: "Confederacao continental a que a selecao pertence (ex: CONMEBOL, UEFA, CONCACAF)."
  - name: Ranking FIFA Pre-Torneio
    expr: fifa_ranking_pre_tournament
    comment: "Posicao no ranking FIFA antes da Copa. Quanto menor o numero, mais forte a selecao (1 = melhor do mundo)."
  - name: Favorita
    expr: CASE WHEN fifa_ranking_pre_tournament <= 10 THEN 'Top 10' WHEN fifa_ranking_pre_tournament <= 30 THEN 'Top 30' ELSE 'Outras' END
    comment: "Faixa de favoritismo derivada do ranking FIFA pre-torneio."

measures:
  - name: Total de Selecoes
    expr: COUNT(1)
    comment: "Quantidade de selecoes classificadas para a Copa."
  - name: Ranking FIFA Medio
    expr: AVG(fifa_ranking_pre_tournament)
    comment: "Media do ranking FIFA pre-torneio das selecoes consideradas."
  - name: Melhor Ranking
    expr: MIN(fifa_ranking_pre_tournament)
    comment: "Menor (melhor) posicao no ranking FIFA entre as selecoes consideradas."
  - name: Pior Ranking
    expr: MAX(fifa_ranking_pre_tournament)
    comment: "Maior (pior) posicao no ranking FIFA entre as selecoes consideradas."
$$;
