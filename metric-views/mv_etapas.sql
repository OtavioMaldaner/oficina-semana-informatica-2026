-- Metric View: Fases do torneio da Copa do Mundo 2026
-- Fonte: fifa_world_cup_2026.gold.dim_etapas

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_etapas
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Fases/etapas do torneio (fase de grupos e mata-mata). Use para filtrar ou agrupar outras metricas por fase."
source: fifa_world_cup_2026.gold.dim_etapas

dimensions:
  - name: Fase
    expr: stage_name
    comment: "Nome da fase do torneio (ex: Group Stage, Round of 32, Round of 16, Quarter-finals, Semi-finals, Final)."
  - name: E Mata-Mata
    expr: is_knockout
    comment: "True = fase eliminatoria (mata-mata, quem perde e eliminado). False = fase de grupos."

measures:
  - name: Total de Fases
    expr: COUNT(1)
    comment: "Quantidade de fases do torneio."
$$;
