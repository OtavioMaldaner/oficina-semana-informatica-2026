-- Metric View: Estatisticas de equipe por partida
-- Fonte: fifa_world_cup_2026.gold.ft_estatisticas_equipe
-- Joins: selecao e partida

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_estatisticas_equipe
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Estatisticas de desempenho de cada selecao em cada partida (posse, finalizacoes, escanteios, faltas, defesas). Complementa o placar bruto com o 'como' do jogo."
source: fifa_world_cup_2026.gold.ft_estatisticas_equipe

joins:
  - name: selecao
    source: fifa_world_cup_2026.gold.dim_selecoes
    on: source.team_id = selecao.team_id
  - name: partida
    source: fifa_world_cup_2026.gold.ft_partidas
    on: source.match_id = partida.match_id

dimensions:
  - name: Selecao
    expr: selecao.team_name
    comment: "Selecao a que as estatisticas pertencem."
  - name: Data da Partida
    expr: partida.date
    comment: "Data da partida a que as estatisticas se referem."
  - name: Craque da Partida
    expr: player_of_the_match
    comment: "Nome do jogador eleito o melhor em campo, quando a selecao teve o premiado (pode ser nulo)."

measures:
  - name: Posse de Bola Media
    expr: AVG(possession_pct)
    comment: "Media do percentual de posse de bola (0 a 100)."
  - name: Total de Finalizacoes
    expr: SUM(total_shots)
    comment: "Soma de finalizacoes (a gol ou para fora) realizadas."
  - name: Total de Finalizacoes no Alvo
    expr: SUM(shots_on_target)
    comment: "Soma de finalizacoes que foram no alvo (exigiram defesa ou resultaram em gol)."
  - name: Precisao de Finalizacao
    expr: SUM(shots_on_target) / NULLIF(SUM(total_shots), 0)
    comment: "Percentual de finalizacoes que foram no alvo, em relacao ao total de finalizacoes."
  - name: Total de Escanteios
    expr: SUM(corners)
    comment: "Soma de escanteios cobrados."
  - name: Total de Faltas
    expr: SUM(fouls)
    comment: "Soma de faltas cometidas."
  - name: Total de Impedimentos
    expr: SUM(offsides)
    comment: "Soma de vezes em posicao de impedimento."
  - name: Total de Defesas
    expr: SUM(saves)
    comment: "Soma de defesas realizadas pelos goleiros."
$$;
