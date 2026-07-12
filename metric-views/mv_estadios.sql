-- Metric View: Estadios sede da Copa do Mundo 2026
-- Fonte: fifa_world_cup_2026.gold.dim_estadios

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_estadios
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Metricas e atributos dos estadios sede da Copa de 2026 (EUA, Mexico e Canada). Use para perguntas sobre capacidade e altitude."
source: fifa_world_cup_2026.gold.dim_estadios

dimensions:
  - name: Estadio
    expr: stadium_name
    comment: "Nome oficial do estadio sede."
  - name: Cidade
    expr: city
    comment: "Cidade onde o estadio esta localizado."
  - name: Pais Sede
    expr: country
    comment: "Pais sede do estadio. Valores esperados: USA, Mexico ou Canada."
  - name: Capacidade
    expr: capacity
    comment: "Capacidade maxima oficial de publico (numero de assentos) do estadio."
  - name: Altitude Metros
    expr: elevation_meters
    comment: "Altitude do estadio em relacao ao nivel do mar, em metros."
  - name: Faixa de Altitude
    expr: CASE WHEN elevation_meters >= 2000 THEN 'Alta altitude (>= 2000m)' WHEN elevation_meters >= 1000 THEN 'Media altitude (1000-2000m)' ELSE 'Baixa altitude (< 1000m)' END
    comment: "Categoria de altitude, relevante para o impacto no desempenho fisico dos jogadores."

measures:
  - name: Total de Estadios
    expr: COUNT(1)
    comment: "Quantidade de estadios sede considerados."
  - name: Capacidade Total
    expr: SUM(capacity)
    comment: "Soma da capacidade de publico de todos os estadios considerados."
  - name: Capacidade Media
    expr: AVG(capacity)
    comment: "Media de capacidade de publico dos estadios considerados."
  - name: Altitude Media
    expr: AVG(elevation_meters)
    comment: "Media de altitude, em metros, dos estadios considerados."
  - name: Maior Capacidade
    expr: MAX(capacity)
    comment: "Maior capacidade de publico entre os estadios considerados."
$$;
