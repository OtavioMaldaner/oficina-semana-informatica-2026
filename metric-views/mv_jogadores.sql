-- Metric View: Elenco e jogadores convocados para a Copa do Mundo 2026
-- Fonte: fifa_world_cup_2026.gold.dim_jogadores (+ join com dim_selecoes)

CREATE OR REPLACE VIEW fifa_world_cup_2026.gold.mv_jogadores
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Perfil dos jogadores convocados: idade, altura, posicao, clube e selecao. Use para perguntas sobre biotipo e origem dos elencos."
source: fifa_world_cup_2026.gold.dim_jogadores

joins:
  - name: selecao
    source: fifa_world_cup_2026.gold.dim_selecoes
    on: source.team_id = selecao.team_id

dimensions:
  - name: Jogador
    expr: player_name
    comment: "Nome do jogador conforme registro oficial."
  - name: Selecao
    expr: selecao.team_name
    comment: "Selecao que o jogador defende."
  - name: Posicao
    expr: position
    comment: "Posicao tatica do jogador. GK = goleiro, DF = defensor, MF = meio-campo, FW = atacante."
  - name: Clube
    expr: club_team
    comment: "Clube onde o jogador atua profissionalmente no momento da convocacao."
  - name: Altura Cm
    expr: height_cm
    comment: "Altura do jogador em centimetros."
  - name: Data de Nascimento
    expr: date_of_birth
    comment: "Data de nascimento do atleta."
  - name: Idade Atual
    expr: FLOOR(DATEDIFF(CURRENT_DATE(), date_of_birth) / 365.25)
    comment: "Idade calculada a partir da data de nascimento ate a data de hoje."

measures:
  - name: Total de Jogadores
    expr: COUNT(1)
    comment: "Quantidade de jogadores convocados considerados."
  - name: Altura Media Cm
    expr: AVG(height_cm)
    comment: "Media de altura, em centimetros, dos jogadores considerados."
  - name: Idade Media
    expr: AVG(FLOOR(DATEDIFF(CURRENT_DATE(), date_of_birth) / 365.25))
    comment: "Media de idade atual dos jogadores considerados."
  - name: Jogador Mais Alto Cm
    expr: MAX(height_cm)
    comment: "Maior altura, em centimetros, entre os jogadores considerados."
  - name: Total de Clubes Distintos
    expr: COUNT(DISTINCT club_team)
    comment: "Quantidade de clubes distintos representados entre os jogadores considerados."
$$;
