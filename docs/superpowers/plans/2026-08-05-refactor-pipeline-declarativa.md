# Refactor das pipelines declarativas — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adotar `dp.read` em todas as leituras intra-pipeline da camada gold e remover ruído de código das transformações, sem alterar nenhuma lógica de negócio.

**Architecture:** ~~Uma única pipeline no Lakeflow Pipelines Editor reúne `data-ingestion/transformations/` e `data-engineering/transformations/`.~~ **CORRIGIDO em 2026-08-05, pós Task 3:** são duas pipelines separadas no Lakeflow — `data-ingestion` (bronze, 12 materialized views geradas em laço a partir de CSVs de um Volume) e `data-engineering` (gold, 13 arquivos: 5 dimensões, 5 fatos, 3 views analíticas). `dp.read` só resolve datasets declarados **dentro da mesma pipeline**; confirmado empiricamente que nenhuma variante de argumento alcança `bronze.teams` a partir de `data-engineering` (ver Task 3). Logo: as 10 leituras bronze→gold **continuam em `spark.read.table`**; só as 8 leituras gold→gold dentro de `data-engineering` (Task 5) migram para `dp.read`. `spark.read.csv` na bronze permanece, por ser leitura de arquivo.

**Tech Stack:** Databricks Free Edition, Unity Catalog, Lakeflow Spark Declarative Pipelines, `pyspark.pipelines` (importado como `dp`), PySpark DataFrame API.

## Como este plano é verificado

Não existe ciclo TDD aqui, e o plano não finge que existe. Não há pyspark no ambiente local e as transformações só executam dentro do Databricks. Cada tarefa é verificada por quatro meios, nesta ordem:

1. **Sintaxe** — `python3 -m py_compile <arquivo>`. Funciona sem pyspark instalado (só compila, não importa) e pega erro de digitação real.
2. **Invariantes por `grep`** — contagens exatas e esperadas de `spark.read.table`, `dp.read`, `.cast(`. São asserções de verdade sobre o diff, não aproximações.
3. **Revisão do diff** — `git diff` conferido contra a regra da tarefa.
4. **Execução da pipeline** — feita pelo autor no Lakeflow Pipelines Editor. É o único meio que valida comportamento. As tarefas que dependem disso dizem explicitamente onde parar e o que observar.

Uma tarefa **não** é dada como concluída com base em 1–3 apenas, quando ela declara que exige 4.

## Global Constraints

Copiadas da spec. Valem implicitamente para toda tarefa.

- **Clareza didática vence.** Quando boa prática de produção conflitar com legibilidade para um aluno de 16 anos, a legibilidade vence. Cada transformação deve ser legível de cima a baixo isoladamente.
- **Nenhuma mudança de lógica.** O refactor preserva comportamento. Corrigir bugs analíticos dos `vw_*` está fora de escopo.
- **Casts que leem de bronze permanecem** — 6 em `ft_eventos.py`, 20 em `ft_estatisticas_jogador.py`. A bronze usa `inferSchema=True`, então são load-bearing.
- **Casts que leem de gold saem** — gold declara `schema`, então são redundantes.
- **Catálogo não é parametrizado.** `fifa_world_cup_2026` continua literal. Nada de `spark.conf.get("catalog")`.
- **Sem helper compartilhado.** A lógica mandante/visitante duplicada entre `vw_pontos_recuperados.py` e `vw_xpts_selecao_partida.py` permanece duplicada de propósito.
- **Prefixo `vw_` mantido** nos três datasets analíticos.
- **`spark.read.csv` na bronze não muda.**

### Regra mecânica de limpeza (Tarefas 6–8)

Aplicada literalmente, sem julgamento caso a caso:

- **Remover** `.cast(T)` quando a expressão já é do tipo `T` por vir de coluna gold declarada no `schema` da tabela de origem.
- **Manter** `.cast(T)` aplicado a `F.lit(None)` — ali o cast declara o tipo do ramo nulo, não é redundante. São 2 ocorrências, ambas em `vw_estabilidade_escalacao.py`.
- **Remover** `.alias(X)` quando a coluna resultante já se chama `X`.
- **Manter** `.alias(X)` quando renomeia de fato (ex.: `F.col("opponent.team_name").alias("opponent_name")`, `F.col("date").alias("match_date")`).

---

## Estrutura de arquivos

Nenhum arquivo é criado ou removido. 14 arquivos existentes são modificados.

| Arquivo | Responsabilidade | Tarefas |
|---|---|---|
| `data-ingestion/transformations/main.py` | Bronze: 12 MVs a partir de CSVs | nenhuma (não muda) |
| `data-engineering/transformations/dim_selecoes.py` | Dimensão seleções | 3 (concluída, sem mudança líquida) |
| `data-engineering/transformations/dim_estadios.py` | Dimensão estádios | ~~4~~ cancelada |
| `data-engineering/transformations/dim_etapas.py` | Dimensão fases | ~~4~~ cancelada |
| `data-engineering/transformations/dim_jogadores.py` | Dimensão jogadores | ~~4~~ cancelada |
| `data-engineering/transformations/dim_arbitros.py` | Dimensão árbitros | ~~4~~ cancelada, 10 |
| `data-engineering/transformations/ft_partidas.py` | Fato partidas | ~~4~~ cancelada, 9, 10 |
| `data-engineering/transformations/ft_eventos.py` | Fato eventos | ~~4~~ cancelada |
| `data-engineering/transformations/ft_escalacoes.py` | Fato escalações | ~~4~~ cancelada |
| `data-engineering/transformations/ft_estatisticas_equipe.py` | Fato estatísticas por equipe/partida | ~~4~~ cancelada |
| `data-engineering/transformations/ft_estatisticas_jogador.py` | Fato estatísticas por jogador | ~~4~~ cancelada |
| `data-engineering/transformations/vw_estabilidade_escalacao.py` | View analítica: estabilidade de escalação | 2, 5, 6 |
| `data-engineering/transformations/vw_pontos_recuperados.py` | View analítica: pontos recuperados | 2, 5, 7 |
| `data-engineering/transformations/vw_xpts_selecao_partida.py` | View analítica: pontos esperados (Poisson) | 2, 5, 8 |

---

## Task 1: Remover os objetos `vw_*` pré-existentes do Unity Catalog

Estes objetos são a causa real da falha da pipeline: eles já existem no Unity Catalog, criados fora desta pipeline, e o Lakeflow não assume propriedade de objeto pré-existente — exige remoção antes.

**Esta tarefa é destrutiva e é executada pelo autor, não por um agente.** O `DROP` foi explicitamente autorizado. Ainda assim é um passo isolado, precedido de captura da definição atual, para ser reversível.

**Files:** nenhum arquivo do repositório é alterado.

**Interfaces:**
- Consumes: nada.
- Produces: catálogo `fifa_world_cup_2026.gold` sem os três objetos `vw_*`, liberando a Task 2 para publicá-los pela pipeline.

- [ ] **Step 1: Descobrir o que existe e de que tipo**

No SQL editor do Databricks:

```sql
SHOW TABLES IN fifa_world_cup_2026.gold LIKE 'vw_*';
SHOW VIEWS IN fifa_world_cup_2026.gold LIKE 'vw_*';
```

Anotar quais dos três aparecem e se são TABLE ou VIEW. Pode ser que nem todos existam.

- [ ] **Step 2: Capturar a definição atual antes de destruir**

Para cada objeto encontrado no Step 1:

```sql
DESCRIBE EXTENDED fifa_world_cup_2026.gold.vw_estabilidade_escalacao;
DESCRIBE EXTENDED fifa_world_cup_2026.gold.vw_pontos_recuperados;
DESCRIBE EXTENDED fifa_world_cup_2026.gold.vw_xpts_selecao_partida;
```

Salvar a saída num arquivo local fora do repositório. Se algum objeto tiver definição SQL que divirja do Python de `data-engineering/transformations/`, **parar e reportar** — significa que a versão em produção não é a versão versionada, e isso muda o escopo.

- [ ] **Step 3: Remover**

Usar `VIEW` ou `TABLE` conforme o tipo apurado no Step 1:

```sql
DROP VIEW IF EXISTS fifa_world_cup_2026.gold.vw_estabilidade_escalacao;
DROP VIEW IF EXISTS fifa_world_cup_2026.gold.vw_pontos_recuperados;
DROP VIEW IF EXISTS fifa_world_cup_2026.gold.vw_xpts_selecao_partida;
```

- [ ] **Step 4: Confirmar remoção**

```sql
SHOW TABLES IN fifa_world_cup_2026.gold LIKE 'vw_*';
SHOW VIEWS IN fifa_world_cup_2026.gold LIKE 'vw_*';
```

Esperado: nenhuma linha.

- [ ] **Step 5: Nada a commitar**

Esta tarefa não altera o repositório. Seguir para a Task 2.

---

## Task 2: Converter os três `vw_*` para materialized view publicada em gold

`@dp.view` cria dataset não publicado no Unity Catalog. Genie e Power BI precisam consultá-los, então viram `@dp.materialized_view` com nome qualificado. O bloco `schema` e as constraints `REFERENCES` permanecem — em tabela publicada eles são metadados válidos e alimentam a detecção de relacionamento no Power BI.

**Files:**
- Modify: `data-engineering/transformations/vw_estabilidade_escalacao.py:6-7`
- Modify: `data-engineering/transformations/vw_pontos_recuperados.py:6-7`
- Modify: `data-engineering/transformations/vw_xpts_selecao_partida.py:5-6`

**Interfaces:**
- Consumes: catálogo limpo pela Task 1.
- Produces: três materialized views em `fifa_world_cup_2026.gold.vw_*`, que passam a existir no DAG como nós publicados.

- [ ] **Step 1: Alterar o decorator de `vw_estabilidade_escalacao.py`**

Trocar:

```python
@dp.view(
    name="vw_estabilidade_escalacao",
```

por:

```python
@dp.materialized_view(
    name="fifa_world_cup_2026.gold.vw_estabilidade_escalacao",
```

Nada mais no arquivo muda nesta tarefa.

- [ ] **Step 2: Alterar o decorator de `vw_pontos_recuperados.py`**

Trocar:

```python
@dp.view(
    name="vw_pontos_recuperados",
```

por:

```python
@dp.materialized_view(
    name="fifa_world_cup_2026.gold.vw_pontos_recuperados",
```

- [ ] **Step 3: Alterar o decorator de `vw_xpts_selecao_partida.py`**

Trocar:

```python
@dp.view(
    name="vw_xpts_selecao_partida",
```

por:

```python
@dp.materialized_view(
    name="fifa_world_cup_2026.gold.vw_xpts_selecao_partida",
```

- [ ] **Step 4: Verificar sintaxe e invariantes**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/vw_*.py && echo "sintaxe OK"
grep -c "@dp.view(" data-engineering/transformations/vw_*.py
grep -c "@dp.materialized_view(" data-engineering/transformations/vw_*.py
```

Esperado: `sintaxe OK`; contagem de `@dp.view(` = 0 nos três; contagem de `@dp.materialized_view(` = 1 em cada um dos três.

- [ ] **Step 5: Rodar a pipeline no Lakeflow — GATE**

Esta é a primeira execução que deve ficar verde. Observar:

- A pipeline conclui sem erro.
- O DAG mostra os três nós `vw_*`.

Se falhar, **capturar a mensagem de erro exata e parar**. Não prosseguir para a Task 3 com a pipeline vermelha — todo o faseamento deste plano depende de ter uma base verde antes da sonda de `dp.read`.

- [ ] **Step 6: Commit**

```bash
git add data-engineering/transformations/vw_estabilidade_escalacao.py \
        data-engineering/transformations/vw_pontos_recuperados.py \
        data-engineering/transformations/vw_xpts_selecao_partida.py
git commit -m "fix: publica as views analiticas como materialized view em gold"
```

---

## Task 3: Sonda — descobrir a forma do argumento de `dp.read` — **CONCLUÍDA, PREMISSA DERRUBADA**

**Resultado (2026-08-05):** variantes 1 (`dp.read("teams")`) e 2 (`dp.read("bronze.teams")`) falharam em execução real com `AnalysisException: TABLE_OR_VIEW_NOT_FOUND` sobre `fifa_world_cup_2026.gold.teams` — o argumento é resolvido contra o schema alvo da própria pipeline (`gold`), não contra bronze. O DAG do pipeline `data-engineering` não mostra nenhum nó bronze, confirmando que bronze e gold são pipelines Lakeflow separadas neste workspace, não uma única pipeline. Variante 3 (nome totalmente qualificado) não foi testada — descartada por inspeção, já que `dp.read` documentadamente só resolve datasets da mesma pipeline, então nenhuma forma de argumento resolveria isso.

`dim_selecoes.py` foi revertido ao `spark.read.table("fifa_world_cup_2026.bronze.teams")` original (commit `55b74cb`). **Tasks 4 e 5 originais foram repactuadas abaixo:** a conversão de leituras bronze→gold para `dp.read` (Task 4) está cancelada — permanece `spark.read.table`. Task 5 (gold→gold, intra-pipeline) segue válida e não testada ainda.

<details>
<summary>Texto original da sonda (histórico)</summary>

A forma correta do argumento é desconhecida. O exemplo de produção disponível usa `dp.read('nome_da_funcao')` sobre datasets declarados **sem** `name=`; aqui todos os datasets são declarados com nome de três partes. Esta tarefa converte **um único arquivo** para descobrir a forma antes de reescrever treze.

`dim_selecoes.py` é a cobaia: uma leitura, sem joins, sem casts, e é dependência de quase todo o resto — se ele resolve, o padrão vale para os demais.

**Files:**
- Modify: `data-engineering/transformations/dim_selecoes.py:22`

**Interfaces:**
- Consumes: pipeline verde vinda da Task 2.
- Produces: **a forma confirmada de `dp.read`**, que as Tasks 4 e 5 aplicam mecanicamente. Registrar a forma vencedora num comentário no corpo do PR/commit para que quem executar as tarefas seguintes não precise redescobri-la.

- [ ] **Step 1: Aplicar a variante 1 (nome curto)**

Em `dim_selecoes.py`, trocar:

```python
        spark.read.table("fifa_world_cup_2026.bronze.teams")
```

por:

```python
        dp.read("teams")
```

- [ ] **Step 2: Verificar sintaxe**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/dim_selecoes.py && echo "sintaxe OK"
```

- [ ] **Step 3: Rodar a pipeline — GATE de descoberta**

Observar duas coisas, não uma:

1. A pipeline fica verde.
2. O DAG mostra a aresta `fifa_world_cup_2026.bronze.teams → fifa_world_cup_2026.gold.dim_selecoes`.

Se ficar verde **e** a aresta aparecer: variante 1 confirmada. Seguir para o Step 5.

- [ ] **Step 4: Se a variante 1 falhar, tentar as seguintes em ordem**

Testar uma por vez, rodando a pipeline entre cada tentativa:

```python
# variante 2 — dois níveis
dp.read("bronze.teams")
```

```python
# variante 3 — qualificado completo
dp.read("fifa_world_cup_2026.bronze.teams")
```

**Se apenas a variante 1 funcionar depois de remover a qualificação do `name=`** — ou seja, se `dp.read` só resolver datasets declarados com nome curto — **parar e reportar ao autor**. Isso aciona a decisão acoplada registrada na spec: adotar `dp.read` passaria a exigir derrubar os `name=` de três partes de todas as declarações, o que é maior que o escopo pedido e interage com o catálogo/schema alvo configurado na pipeline. A Task 4 deve ser repactuada antes de seguir, não executada como planejada.

Se **nenhuma** das três variantes resolver, parar e reportar — o pressuposto central do refactor cai e o plano precisa ser revisto.

- [ ] **Step 5: Commit**

```bash
git add data-engineering/transformations/dim_selecoes.py
git commit -m "refactor: le bronze via dp.read em dim_selecoes"
```

Incluir no corpo do commit qual variante foi confirmada, por exemplo: `Variante confirmada: dp.read("teams") (nome curto).`

</details>

---

## Task 4: Aplicar `dp.read` aos nove arquivos gold restantes — **CANCELADA**

**Cancelada em 2026-08-05.** A Task 3 derrubou a premissa: bronze e gold são pipelines Lakeflow separadas, e `dp.read` não alcança um dataset fora da pipeline atual em nenhuma forma de argumento. As nove leituras bronze→gold abaixo **permanecem em `spark.read.table`**, como já estavam. Nenhuma ação necessária nestes nove arquivos.

<details>
<summary>Texto original da tarefa (histórico, não executar)</summary>

Conversão mecânica, usando a forma confirmada na Task 3. Um commit só, porque o diff é uniforme e auditável de uma vez.

O código abaixo assume a **variante 1 (nome curto)**. Se a Task 3 confirmou a variante 2, prefixar cada argumento com `bronze.`; se confirmou a variante 3, usar o nome de três partes completo. A substituição é mecânica em qualquer caso.

**Files:**
- Modify: `data-engineering/transformations/dim_estadios.py:20`
- Modify: `data-engineering/transformations/dim_etapas.py:17`
- Modify: `data-engineering/transformations/dim_jogadores.py:24`
- Modify: `data-engineering/transformations/dim_arbitros.py:19`
- Modify: `data-engineering/transformations/ft_partidas.py:49`
- Modify: `data-engineering/transformations/ft_eventos.py:24`
- Modify: `data-engineering/transformations/ft_escalacoes.py:25`
- Modify: `data-engineering/transformations/ft_estatisticas_equipe.py:34`
- Modify: `data-engineering/transformations/ft_estatisticas_jogador.py:40`

**Interfaces:**
- Consumes: a forma de `dp.read` confirmada na Task 3.
- Produces: zero ocorrências de `spark.read.table` nos arquivos gold de dimensão e fato; nove arestas bronze→gold no DAG.

- [ ] **Step 1: Substituir as nove leituras**

| Arquivo | Trocar | Por |
|---|---|---|
| `dim_estadios.py` | `spark.read.table("fifa_world_cup_2026.bronze.venues")` | `dp.read("venues")` |
| `dim_etapas.py` | `spark.read.table("fifa_world_cup_2026.bronze.tournament_stages")` | `dp.read("tournament_stages")` |
| `dim_jogadores.py` | `spark.read.table("fifa_world_cup_2026.bronze.squads_and_players")` | `dp.read("squads_and_players")` |
| `dim_arbitros.py` | `spark.read.table("fifa_world_cup_2026.bronze.referees")` | `dp.read("referees")` |
| `ft_partidas.py` | `spark.read.table("fifa_world_cup_2026.bronze.matches")` | `dp.read("matches")` |
| `ft_eventos.py` | `spark.read.table("fifa_world_cup_2026.bronze.match_events")` | `dp.read("match_events")` |
| `ft_escalacoes.py` | `spark.read.table("fifa_world_cup_2026.bronze.match_lineups")` | `dp.read("match_lineups")` |
| `ft_estatisticas_equipe.py` | `spark.read.table("fifa_world_cup_2026.bronze.match_team_stats")` | `dp.read("match_team_stats")` |
| `ft_estatisticas_jogador.py` | `spark.read.table("fifa_world_cup_2026.bronze.player_stats")` | `dp.read("player_stats")` |

Atenção a `dim_etapas.py`, que é o único cujo corpo é uma expressão de uma linha:

```python
def dim_etapas():
    return dp.read("tournament_stages")
```

- [ ] **Step 2: Verificar sintaxe e invariantes**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/*.py && echo "sintaxe OK"
echo "spark.read.table nos dim_/ft_ (esperado 0):"
grep -c "spark.read.table" data-engineering/transformations/dim_*.py data-engineering/transformations/ft_*.py | grep -v ":0" || echo "  0 em todos"
echo "dp.read total nos dim_/ft_ (esperado 10):"
grep -h "dp.read(" data-engineering/transformations/dim_*.py data-engineering/transformations/ft_*.py | wc -l
```

Esperado: `sintaxe OK`; nenhum arquivo `dim_*`/`ft_*` com `spark.read.table`; total de `dp.read` = 10 (os 9 desta tarefa mais `dim_selecoes.py` da Task 3).

- [ ] **Step 3: Conferir que os casts de bronze sobreviveram**

Esta é a checagem que protege a constraint global mais fácil de violar por engano.

```bash
grep -c "\.cast(" data-engineering/transformations/ft_eventos.py \
                 data-engineering/transformations/ft_estatisticas_jogador.py
```

Esperado: `ft_eventos.py:6` e `ft_estatisticas_jogador.py:20`. Se algum caiu, foi removido indevidamente — reverter.

- [ ] **Step 4: Rodar a pipeline — GATE**

Esperado: verde, e o DAG mostrando dez arestas bronze→gold. Se falhar, capturar o erro e parar.

- [ ] **Step 5: Commit**

```bash
git add data-engineering/transformations/dim_*.py data-engineering/transformations/ft_*.py
git commit -m "refactor: le bronze via dp.read em todas as dimensoes e fatos"
```

</details>

---

## Task 5: Aplicar `dp.read` às oito leituras dos `vw_*` — **CONCLUÍDA**

**Resultado (2026-08-05):** variante 1 (nome curto) confirmada em duas etapas — sonda isolada em `vw_xpts_selecao_partida.py`, pipeline verde; depois aplicada aos três arquivos juntos, pipeline verde de novo com as oito arestas gold→vw no DAG. Commit `01ef766`.

**Não afetada pelo cancelamento da Task 4.** Estas oito leituras são gold→gold, todas dentro da pipeline `data-engineering` — o mesmo tipo de leitura intra-pipeline que a Task 3 comprovou funcionar (a leitura de `dim_selecoes.py` a partir de `vw_estabilidade_escalacao.py` etc. já é intra-pipeline hoje via `spark.read.table`). Ainda não testada com `dp.read`; ao executar, confirmar a variante correta do argumento antes de aplicar aos oito arquivos — provavelmente nome curto (`dp.read("dim_selecoes")`), já que é o mesmo padrão que funciona em qualquer pipeline Lakeflow para datasets locais, mas vale confirmar em um arquivo antes de propagar, como fez a Task 3.

Mesma conversão, agora nas leituras gold→gold. São oito chamadas em três arquivos.

Código abaixo assume a variante 1 (nome curto) — a única já demonstrada plausível para leituras intra-pipeline; se falhar, testar variante 2 como na Task 3.

**Files:**
- Modify: `data-engineering/transformations/vw_estabilidade_escalacao.py` (3 leituras)
- Modify: `data-engineering/transformations/vw_pontos_recuperados.py` (3 leituras)
- Modify: `data-engineering/transformations/vw_xpts_selecao_partida.py` (2 leituras)

**Interfaces:**
- Consumes: a forma de `dp.read` confirmada na Task 3; as materialized views publicadas na Task 2.
- Produces: zero ocorrências de `spark.read.table` no projeto inteiro; arestas gold→vw no DAG.

- [x] **Step 1: `vw_estabilidade_escalacao.py` — três leituras**

| Trocar | Por |
|---|---|
| `spark.read.table("fifa_world_cup_2026.gold.ft_escalacoes")` | `dp.read("ft_escalacoes")` |
| `spark.read.table("fifa_world_cup_2026.gold.ft_partidas")` | `dp.read("ft_partidas")` |
| `spark.read.table("fifa_world_cup_2026.gold.dim_selecoes")` | `dp.read("dim_selecoes")` |

- [x] **Step 2: `vw_pontos_recuperados.py` — três leituras**

| Trocar | Por |
|---|---|
| `spark.read.table("fifa_world_cup_2026.gold.ft_partidas")` | `dp.read("ft_partidas")` |
| `spark.read.table("fifa_world_cup_2026.gold.ft_eventos")` | `dp.read("ft_eventos")` |
| `spark.read.table("fifa_world_cup_2026.gold.dim_selecoes")` | `dp.read("dim_selecoes")` |

- [x] **Step 3: `vw_xpts_selecao_partida.py` — duas leituras**

| Trocar | Por |
|---|---|
| `spark.read.table("fifa_world_cup_2026.gold.ft_partidas")` | `dp.read("ft_partidas")` |
| `spark.read.table("fifa_world_cup_2026.gold.dim_selecoes")` | `dp.read("dim_selecoes")` |

- [x] **Step 4: Verificar o invariante final do refactor de leitura** — **(revisado: Task 4 cancelada, números originais não se aplicam mais)**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/*.py && echo "sintaxe OK"
echo "spark.read.table nos vw_ (esperado 0):"
grep -c "spark.read.table" data-engineering/transformations/vw_*.py
echo "dp.read nos vw_ (esperado 8):"
grep -h "dp.read(" data-engineering/transformations/vw_*.py | wc -l
```

Verificado: `sintaxe OK`; zero `spark.read.table` nos três `vw_*`; `dp.read` = 8. `spark.read.table` continua presente nas 10 leituras bronze→gold (`dim_*`/`ft_*`), por decisão da Task 4 cancelada — não é regressão.

- [x] **Step 5: Rodar a pipeline — GATE**

Verificado em duas rodadas: sonda isolada (`vw_xpts_selecao_partida.py` sozinho) verde; depois os três arquivos juntos, verde de novo com as oito arestas gold→vw no DAG.

- [x] **Step 6: Commit**

```bash
git add data-engineering/transformations/vw_*.py
git commit -m "refactor: le gold via dp.read nas views analiticas"
```

Commit real: `01ef766`.

---

## Task 6: Remover casts redundantes de `vw_estabilidade_escalacao.py` — **CONCLUÍDA**

**Resultado (2026-08-05):** aplicada, incluindo a limpeza do bloco `teams` que os Steps originais não cobriam (ver nota no Step 6). Invariante final batido (2 casts restantes, ambos em `F.lit(None)`). Commit `3cc9686`. Pipeline rodada com todas as mudanças das Tasks 6–8 juntas: verde, confirmado pelo autor.

O arquivo tem 32 chamadas `.cast(`. Duas delas se aplicam a `F.lit(None)` e **ficam** — ali o cast declara o tipo do ramo nulo. As demais são redundantes: as colunas vêm de `ft_escalacoes`, `ft_partidas` e `dim_selecoes`, que declaram `schema`.

**Files:**
- Modify: `data-engineering/transformations/vw_estabilidade_escalacao.py:33-189`

**Interfaces:**
- Consumes: `dp.read` aplicado na Task 5.
- Produces: mesmo schema de saída, mesma lógica; apenas menos ruído.

- [ ] **Step 1: Limpar o bloco `lineups`**

Trocar:

```python
    lineups = (
        dp.read("ft_escalacoes")
        .filter(F.col("is_starting_xi") == F.lit(True))
        .select(
            F.col("match_id").cast("int"),
            F.col("team_id").cast("int"),
            F.col("player_id").cast("int"),
        )
    )
```

por:

```python
    lineups = (
        dp.read("ft_escalacoes")
        .filter(F.col("is_starting_xi") == F.lit(True))
        .select("match_id", "team_id", "player_id")
    )
```

- [ ] **Step 2: Limpar o bloco `matches`**

Trocar:

```python
    matches = dp.read("ft_partidas").select(
        F.col("match_id").cast("int"),
        F.col("date").cast("date").alias("match_date"),
        F.col("kickoff_time_utc").cast("timestamp"),
        F.col("stage_id").cast("int"),
        F.col("home_team_id").cast("int"),
        F.col("away_team_id").cast("int"),
    )
```

por:

```python
    matches = dp.read("ft_partidas").select(
        "match_id",
        F.col("date").alias("match_date"),
        "kickoff_time_utc",
        "stage_id",
        "home_team_id",
        "away_team_id",
    )
```

O `.alias("match_date")` fica: renomeia de fato.

- [ ] **Step 3: Limpar `opponent_team_id` e `starting_xi_count` no bloco `starting_lineups`**

Trocar:

```python
            F.when(
                F.col("lineups.team_id") == F.col("matches.home_team_id"),
                F.col("matches.away_team_id"),
            )
            .when(
                F.col("lineups.team_id") == F.col("matches.away_team_id"),
                F.col("matches.home_team_id"),
            )
            .cast("int")
            .alias("opponent_team_id"),
```

por:

```python
            F.when(
                F.col("lineups.team_id") == F.col("matches.home_team_id"),
                F.col("matches.away_team_id"),
            )
            .when(
                F.col("lineups.team_id") == F.col("matches.away_team_id"),
                F.col("matches.home_team_id"),
            )
            .alias("opponent_team_id"),
```

E trocar:

```python
        .withColumn(
            "starting_xi_count",
            F.size("starting_players").cast("int"),
        )
```

por:

```python
        .withColumn("starting_xi_count", F.size("starting_players"))
```

- [ ] **Step 4: Limpar `compared_lineups`, preservando os dois casts de `F.lit(None)`**

Trocar:

```python
    compared_lineups = (
        starting_lineups.withColumn(
            "previous_match_id",
            F.lag("match_id").over(match_sequence_window).cast("int"),
        )
        .withColumn(
            "previous_starting_players",
            F.lag("starting_players").over(match_sequence_window),
        )
        .withColumn(
            "repeated_starters",
            F.when(
                F.col("previous_starting_players").isNull(),
                F.lit(None).cast("int"),
            )
            .otherwise(
                F.size(
                    F.array_intersect(
                        F.col("starting_players"),
                        F.col("previous_starting_players"),
                    )
                ).cast("int")
            )
            .cast("int"),
        )
        .withColumn(
            "lineup_stability_pct",
            F.when(
                F.col("previous_starting_players").isNull(),
                F.lit(None).cast("double"),
            )
            .otherwise(
                F.col("repeated_starters").cast("double")
                * F.lit(100.0)
                / F.lit(11.0)
            )
            .cast("double"),
        )
    )
```

por:

```python
    compared_lineups = (
        starting_lineups.withColumn(
            "previous_match_id",
            F.lag("match_id").over(match_sequence_window),
        )
        .withColumn(
            "previous_starting_players",
            F.lag("starting_players").over(match_sequence_window),
        )
        .withColumn(
            "repeated_starters",
            F.when(
                F.col("previous_starting_players").isNull(),
                F.lit(None).cast("int"),
            ).otherwise(
                F.size(
                    F.array_intersect(
                        F.col("starting_players"),
                        F.col("previous_starting_players"),
                    )
                )
            ),
        )
        .withColumn(
            "lineup_stability_pct",
            F.when(
                F.col("previous_starting_players").isNull(),
                F.lit(None).cast("double"),
            ).otherwise(
                F.col("repeated_starters") * F.lit(100.0) / F.lit(11.0)
            ),
        )
    )
```

Os dois `F.lit(None).cast(...)` permanecem. O `F.col("repeated_starters").cast("double")` sai porque a multiplicação por `F.lit(100.0)` já promove para double.

- [ ] **Step 5: Limpar o `select` final**

Trocar o `select` inteiro do `return` por:

```python
        .select(
            F.col("lineups.team_id").alias("team_id"),
            F.col("team.team_name").alias("team_name"),
            F.col("lineups.match_id").alias("match_id"),
            F.col("lineups.previous_match_id").alias("previous_match_id"),
            F.col("lineups.match_date").alias("match_date"),
            F.col("lineups.kickoff_time_utc").alias("kickoff_time_utc"),
            F.col("lineups.stage_id").alias("stage_id"),
            F.col("lineups.opponent_team_id").alias("opponent_team_id"),
            F.col("opponent.team_name").alias("opponent_name"),
            F.col("lineups.starting_players").alias("starting_players"),
            F.col("lineups.previous_starting_players").alias(
                "previous_starting_players"
            ),
            F.col("lineups.starting_xi_count").alias("starting_xi_count"),
            F.col("lineups.repeated_starters").alias("repeated_starters"),
            F.col("lineups.lineup_stability_pct").alias("lineup_stability_pct"),
        )
```

Os `.alias()` ficam aqui de propósito: com dois `teams` unidos sob apelidos diferentes (`team` e `opponent`), o alias explícito é o que deixa a origem de cada coluna legível — exatamente o tipo de clareza que a restrição didática pede. O que sai são só os casts.

- [ ] **Step 6: Verificar**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/vw_estabilidade_escalacao.py && echo "sintaxe OK"
echo "casts restantes (esperado 2, ambos em F.lit(None)):"
grep -c "\.cast(" data-engineering/transformations/vw_estabilidade_escalacao.py
echo "casts em lit(None) (esperado 2):"
grep -c "lit(None).cast(" data-engineering/transformations/vw_estabilidade_escalacao.py
```

Esperado: `sintaxe OK`; total de casts = 2; casts em `lit(None)` = 2. Os dois números serem iguais é a prova de que só sobraram os que deviam sobrar.

- [ ] **Step 7: Rodar a pipeline — GATE**

Esperado: verde. Conferir no Catalog Explorer que `gold.vw_estabilidade_escalacao` mantém os mesmos tipos de coluna declarados no bloco `schema`. Uma divergência de tipo faria a execução falhar em vez de passar silenciosamente — é por isso que o `schema` declarado é a rede de proteção desta tarefa.

- [ ] **Step 8: Commit**

```bash
git add data-engineering/transformations/vw_estabilidade_escalacao.py
git commit -m "refactor: remove casts redundantes em vw_estabilidade_escalacao"
```

---

## Task 7: Remover casts redundantes de `vw_pontos_recuperados.py` — **CONCLUÍDA**

**Resultado (2026-08-05):** aplicada conforme planejado, invariante final batido (0 casts restantes). Commit `5b7c098`. Pipeline verde (rodada junto com Tasks 6 e 8), confirmado pelo autor.

31 chamadas `.cast(`, nenhuma sobre `F.lit(None)` — todas saem, exceto onde o cast faz conversão real de tipo.

**Files:**
- Modify: `data-engineering/transformations/vw_pontos_recuperados.py:34-206`

**Interfaces:**
- Consumes: `dp.read` aplicado na Task 5.
- Produces: mesmo schema de saída, mesma lógica.

- [ ] **Step 1: Limpar o bloco `matches`**

Trocar:

```python
    matches = dp.read("ft_partidas").select(
        F.col("match_id").cast("int"),
        F.col("date").cast("date").alias("match_date"),
        F.col("kickoff_time_utc").cast("timestamp"),
        F.col("stage_id").cast("int"),
        F.col("home_team_id").cast("int"),
        F.col("away_team_id").cast("int"),
        F.col("home_score").cast("int"),
        F.col("away_score").cast("int"),
    )
```

por:

```python
    matches = dp.read("ft_partidas").select(
        "match_id",
        F.col("date").alias("match_date"),
        "kickoff_time_utc",
        "stage_id",
        "home_team_id",
        "away_team_id",
        "home_score",
        "away_score",
    )
```

- [ ] **Step 2: Limpar `home_perspective` e `away_perspective`**

Em ambos os blocos, remover o `.cast("int")` da expressão de pontos. Em `home_perspective`:

```python
        F.when(F.col("home_score") > F.col("away_score"), F.lit(3))
        .when(F.col("home_score") == F.col("away_score"), F.lit(1))
        .otherwise(F.lit(0))
        .alias("actual_points"),
```

Em `away_perspective`:

```python
        F.when(F.col("away_score") > F.col("home_score"), F.lit(3))
        .when(F.col("away_score") == F.col("home_score"), F.lit(1))
        .otherwise(F.lit(0))
        .alias("actual_points"),
```

Os literais já são inteiros; o cast não fazia nada.

- [ ] **Step 3: Limpar o bloco `goals`**

Trocar:

```python
    goals = (
        dp.read("ft_eventos")
        .filter(F.col("event_type") == F.lit("Goal"))
        .select(
            F.col("event_id").cast("int"),
            F.col("match_id").cast("int"),
            F.col("minute").cast("int"),
            F.col("team_id").cast("int").alias("scoring_team_id"),
        )
    )
```

por:

```python
    goals = (
        dp.read("ft_eventos")
        .filter(F.col("event_type") == F.lit("Goal"))
        .select(
            "event_id",
            "match_id",
            "minute",
            F.col("team_id").alias("scoring_team_id"),
        )
    )
```

- [ ] **Step 4: Limpar `disadvantages` e o bloco `teams`**

Em `disadvantages`, remover o `.cast("int")` do `agg`:

```python
        .agg(
            F.max(
                F.when(
                    F.col("running_goals_for")
                    < F.col("running_goals_against"),
                    F.lit(1),
                ).otherwise(F.lit(0))
            ).alias("was_behind")
        )
```

E trocar o bloco `teams`:

```python
    teams = dp.read("dim_selecoes").select("team_id", "team_name")
```

- [ ] **Step 5: Limpar `withColumn` e `select` finais**

Trocar os dois `withColumn`:

```python
        .withColumn(
            "was_behind",
            F.coalesce(F.col("disadvantages.was_behind"), F.lit(0)),
        )
        .withColumn(
            "recovered_points",
            F.when(
                F.col("was_behind") == F.lit(1),
                F.col("matches.actual_points"),
            ).otherwise(F.lit(0)),
        )
```

E o `select` final:

```python
        .select(
            F.col("matches.match_id").alias("match_id"),
            F.col("matches.match_date").alias("match_date"),
            F.col("matches.kickoff_time_utc").alias("kickoff_time_utc"),
            F.col("matches.stage_id").alias("stage_id"),
            F.col("matches.team_id").alias("team_id"),
            F.col("team.team_name").alias("team_name"),
            F.col("matches.opponent_team_id").alias("opponent_team_id"),
            F.col("opponent.team_name").alias("opponent_name"),
            F.col("matches.goals_for").alias("goals_for"),
            F.col("matches.goals_against").alias("goals_against"),
            F.col("matches.actual_points").alias("actual_points"),
            (F.col("was_behind") == F.lit(1)).alias("was_behind"),
            F.col("recovered_points").alias("recovered_points"),
        )
```

A linha `(F.col("was_behind") == F.lit(1)).alias("was_behind")` fica intacta: ela converte o inteiro interno no BOOLEAN que o `schema` declara, e é lógica, não ruído.

- [ ] **Step 6: Verificar**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/vw_pontos_recuperados.py && echo "sintaxe OK"
echo "casts restantes (esperado 0):"
grep -c "\.cast(" data-engineering/transformations/vw_pontos_recuperados.py
```

Esperado: `sintaxe OK`; zero casts.

- [ ] **Step 7: Rodar a pipeline — GATE**

Esperado: verde, e `gold.vw_pontos_recuperados` com `was_behind` do tipo BOOLEAN, conforme o `schema` declarado.

- [ ] **Step 8: Commit**

```bash
git add data-engineering/transformations/vw_pontos_recuperados.py
git commit -m "refactor: remove casts redundantes em vw_pontos_recuperados"
```

---

## Task 8: Remover casts redundantes de `vw_xpts_selecao_partida.py` — **CONCLUÍDA**

**Resultado (2026-08-05):** aplicada, invariante de contagem batido (5 casts restantes, exatamente `spark.range` ×2, `F.factorial` ×2, `actual_points` ×1). Commit `ed1650f`. Pipeline verde. Gate numérico do Step 8 confirmado por consulta real: `min_soma` = 1, `max_soma` = 1, `min_massa` = 0.996172 (próxima de 1.0, como esperado — nenhuma divisão inteira introduzida pela remoção de casts).

41 chamadas `.cast(` — a maior concentração do projeto. Nenhuma sobre `F.lit(None)`.

Atenção: nem todo cast aqui sai. `F.factorial(...).cast("double")` faz conversão real — `factorial` devolve BIGINT, e sem o cast a divisão vira inteira e destrói o cálculo de Poisson. Os dois casts de `spark.range` também convertem de verdade (BIGINT para int). Já `F.col("actual_points").cast("double")` é mantido por escolha de legibilidade, não por necessidade; ver Step 5.

**Files:**
- Modify: `data-engineering/transformations/vw_xpts_selecao_partida.py:36-239`

**Interfaces:**
- Consumes: `dp.read` aplicado na Task 5.
- Produces: mesmo schema de saída, mesma lógica; probabilidades e xPts numericamente idênticos.

- [ ] **Step 1: Limpar o bloco `matches`**

Trocar:

```python
    matches = (
        dp.read("ft_partidas")
        .select(
            F.col("match_id").cast("int"),
            F.col("date").cast("date").alias("match_date"),
            F.col("kickoff_time_utc").cast("timestamp"),
            F.col("stage_id").cast("int"),
            F.col("home_team_id").cast("int"),
            F.col("away_team_id").cast("int"),
            F.col("home_score").cast("int"),
            F.col("away_score").cast("int"),
            F.col("home_xg").cast("double"),
            F.col("away_xg").cast("double"),
        )
        .filter(F.col("home_xg").isNotNull() & F.col("away_xg").isNotNull())
    )
```

por:

```python
    matches = (
        dp.read("ft_partidas")
        .select(
            "match_id",
            F.col("date").alias("match_date"),
            "kickoff_time_utc",
            "stage_id",
            "home_team_id",
            "away_team_id",
            "home_score",
            "away_score",
            "home_xg",
            "away_xg",
        )
        .filter(F.col("home_xg").isNotNull() & F.col("away_xg").isNotNull())
    )
```

- [ ] **Step 2: Limpar `home_perspective` e `away_perspective`**

Remover o `.cast("int")` das expressões de pontos, exatamente como na Task 7 Step 2. Em `home_perspective`:

```python
        F.when(F.col("home_score") > F.col("away_score"), F.lit(3))
        .when(F.col("home_score") == F.col("away_score"), F.lit(1))
        .otherwise(F.lit(0))
        .alias("actual_points"),
```

Em `away_perspective`:

```python
        F.when(F.col("away_score") > F.col("home_score"), F.lit(3))
        .when(F.col("away_score") == F.col("home_score"), F.lit(1))
        .otherwise(F.lit(0))
        .alias("actual_points"),
```

- [ ] **Step 3: Preservar os casts do modelo de Poisson**

Os blocos `modeled_goals_for`, `modeled_goals_against`, `poisson_for` e `poisson_against` **não mudam**. Em particular, estes casts fazem conversão real e ficam:

```python
    modeled_goals_for = spark.range(0, 11).select(
        F.col("id").cast("int").alias("modeled_goals_for")
    )
    modeled_goals_against = spark.range(0, 11).select(
        F.col("id").cast("int").alias("modeled_goals_against")
    )
```

`spark.range` devolve BIGINT, então o cast para int é conversão real. E em `poisson_for`/`poisson_against`, `F.factorial(...).cast("double")` converte BIGINT para double, evitando divisão inteira — é lógica, não ruído.

Nota: `spark.range` é leitura de dados gerados em memória, não de tabela. Não vira `dp.read`.

- [ ] **Step 4: Limpar `outcome_probabilities` e `grouped_probabilities`**

Em `outcome_probabilities`, o produto de dois doubles já é double:

```python
    outcome_probabilities = scorelines.withColumn(
        "joint_probability",
        poisson_for * poisson_against,
    )
```

Em `grouped_probabilities`, remover os quatro `.cast("double")` dos `agg`, mantendo os `.alias()`:

```python
    ).agg(
        F.sum("joint_probability").alias("probability_mass_0_to_10"),
        F.sum(
            F.when(
                F.col("modeled_goals_for") > F.col("modeled_goals_against"),
                F.col("joint_probability"),
            ).otherwise(F.lit(0.0))
        ).alias("raw_win_probability"),
        F.sum(
            F.when(
                F.col("modeled_goals_for") == F.col("modeled_goals_against"),
                F.col("joint_probability"),
            ).otherwise(F.lit(0.0))
        ).alias("raw_draw_probability"),
        F.sum(
            F.when(
                F.col("modeled_goals_for") < F.col("modeled_goals_against"),
                F.col("joint_probability"),
            ).otherwise(F.lit(0.0))
        ).alias("raw_loss_probability"),
    )
```

- [ ] **Step 5: Manter o bloco `metrics` intacto, exceto o `teams`**

O bloco `metrics` não muda. Sobre `points_above_expected`, que usa `F.col("actual_points").cast("double")`: o Spark promoveria int para double sozinho na subtração, então esse cast não é estritamente necessário. Ele **fica mesmo assim**, porque torna explícita a promoção de tipo no único ponto do arquivo onde ela decide o resultado — e a restrição de clareza didática pesa a favor de deixar isso visível para o aluno. É uma escolha, não um descuido, e por isso entra na contagem esperada do Step 7.

Trocar apenas o bloco `teams`:

```python
    teams = dp.read("dim_selecoes").select("team_id", "team_name")
```

- [ ] **Step 6: Limpar o `select` final**

Trocar o `select` inteiro do `return` por:

```python
        .select(
            F.col("metrics.match_id").alias("match_id"),
            F.col("metrics.match_date").alias("match_date"),
            F.col("metrics.kickoff_time_utc").alias("kickoff_time_utc"),
            F.col("metrics.stage_id").alias("stage_id"),
            F.col("metrics.team_id").alias("team_id"),
            F.col("team.team_name").alias("team_name"),
            F.col("metrics.opponent_team_id").alias("opponent_team_id"),
            F.col("opponent.team_name").alias("opponent_name"),
            F.col("metrics.xg_for").alias("xg_for"),
            F.col("metrics.xg_against").alias("xg_against"),
            F.col("metrics.actual_points").alias("actual_points"),
            F.col("metrics.win_probability").alias("win_probability"),
            F.col("metrics.draw_probability").alias("draw_probability"),
            F.col("metrics.loss_probability").alias("loss_probability"),
            F.col("metrics.expected_points").alias("expected_points"),
            F.col("metrics.points_above_expected").alias("points_above_expected"),
            F.col("metrics.probability_mass_0_to_10").alias(
                "probability_mass_0_to_10"
            ),
        )
```

- [ ] **Step 7: Verificar**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/vw_xpts_selecao_partida.py && echo "sintaxe OK"
echo "casts restantes (esperado 5 — 2 de spark.range, 2 de factorial, 1 de actual_points):"
grep -c "\.cast(" data-engineering/transformations/vw_xpts_selecao_partida.py
echo "confere quais sobraram:"
grep -n "\.cast(" data-engineering/transformations/vw_xpts_selecao_partida.py
```

Esperado: `sintaxe OK`; 5 casts restantes, e o `grep -n` deve mostrar exatamente os de `F.col("id")` (×2), `F.factorial` (×2) e `F.col("actual_points")` (×1). Qualquer outro sobrando é limpeza incompleta; qualquer um desses faltando é remoção indevida.

- [ ] **Step 8: Rodar a pipeline — GATE de valores**

Esta tarefa mexe em código numérico, então a verificação vai além de "ficou verde". Rodar no SQL editor:

```sql
SELECT
  ROUND(MIN(win_probability + draw_probability + loss_probability), 6) AS min_soma,
  ROUND(MAX(win_probability + draw_probability + loss_probability), 6) AS max_soma,
  ROUND(MIN(probability_mass_0_to_10), 6) AS min_massa
FROM fifa_world_cup_2026.gold.vw_xpts_selecao_partida;
```

Esperado: `min_soma` e `max_soma` iguais a 1.0 (as três probabilidades são renormalizadas e devem somar 1), e `min_massa` próxima de 1.0. Se `min_soma` divergir de 1.0, uma remoção de cast introduziu divisão inteira — reverter e revisar o Step 3.

- [ ] **Step 9: Commit**

```bash
git add data-engineering/transformations/vw_xpts_selecao_partida.py
git commit -m "refactor: remove casts redundantes em vw_xpts_selecao_partida"
```

---

## Task 9: Declarar a FK faltante de `referee_id`

Correção de modelagem, não cosmética. `ft_partidas.referee_id` é a única FK do star schema sem `REFERENCES` declarado. O README apoia a importação no Power BI nos relacionamentos PK/FK declarados nas tabelas, então essa aresta ausente afeta o produto final da oficina.

**Files:**
- Modify: `data-engineering/transformations/ft_partidas.py:33`

**Interfaces:**
- Consumes: `dim_arbitros` publicada com `referee_id` como PRIMARY KEY (já é o caso).
- Produces: aresta `ft_partidas → dim_arbitros` visível no Catalog Explorer e no Power BI.

- [ ] **Step 1: Alterar a declaração da coluna**

Trocar:

```python
        referee_id INT COMMENT 'Identificador do arbitro principal da partida.',
```

por:

```python
        referee_id INT REFERENCES fifa_world_cup_2026.gold.dim_arbitros(referee_id) COMMENT 'Chave estrangeira para o arbitro principal da partida.',
```

O texto do `COMMENT` também muda, para ficar consistente com o padrão das outras FKs do arquivo, que todas dizem "Chave estrangeira para...".

- [ ] **Step 2: Verificar**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/ft_partidas.py && echo "sintaxe OK"
echo "FKs declaradas em ft_partidas (esperado 5):"
grep -c "REFERENCES" data-engineering/transformations/ft_partidas.py
```

Esperado: `sintaxe OK`; 5 `REFERENCES` — `stage_id`, `venue_id`, `home_team_id`, `away_team_id` e agora `referee_id`.

- [ ] **Step 3: Rodar a pipeline — GATE**

Esperado: verde. Uma FK só é aceita se a coluna referenciada for PRIMARY KEY na tabela destino; se falhar aqui, conferir que `dim_arbitros.referee_id` está declarado como `NOT NULL PRIMARY KEY` — está, na linha 12 de `dim_arbitros.py`.

Confirmar no Catalog Explorer, em `gold.ft_partidas` → aba de constraints, que o relacionamento com `dim_arbitros` aparece.

- [ ] **Step 4: Commit**

```bash
git add data-engineering/transformations/ft_partidas.py
git commit -m "fix: declara FK de referee_id para dim_arbitros em ft_partidas"
```

---

## Task 10: Padronizações finais de legibilidade

Duas mudanças pequenas e sem risco, agrupadas por serem ambas puramente textuais.

**Files:**
- Modify: `data-engineering/transformations/dim_arbitros.py:18-24`
- Modify: `data-engineering/transformations/ft_partidas.py:1-6`

**Interfaces:**
- Consumes: nada.
- Produces: nada que outra tarefa dependa. Esta é a última tarefa do plano.

- [ ] **Step 1: `selectExpr` → `select` em `dim_arbitros.py`**

É o único arquivo dos treze que usa `selectExpr`. Trocar:

```python
def dim_arbitros():
    return (
        dp.read("referees")
        .selectExpr(
            "referee_id",
            "name AS referee_name",
            "country",
        )
    )
```

por:

```python
def dim_arbitros():
    return dp.read("referees").select(
        "referee_id",
        F.col("name").alias("referee_name"),
        "country",
    )
```

Isso exige adicionar o import de `functions`, que o arquivo ainda não tem. No topo, trocar:

```python
from pyspark import pipelines as dp
```

por:

```python
from pyspark import pipelines as dp
from pyspark.sql import functions as F
```

- [ ] **Step 2: Corrigir a docstring obsoleta de `ft_partidas.py`**

A docstring atual descreve uma view achatada que não existe mais no arquivo. Trocar:

```python
"""
Camada GOLD — fatos do star schema da Copa do Mundo 2026.

Contem a tabela fato principal com as metricas dos jogos e uma view 
achatada (desnormalizada) enriquecida com metadados para otimizar as
respostas de IA no Databricks Genie e facilitar a criacao de dashboards.
"""
```

por:

```python
"""
Camada GOLD — fato principal do star schema da Copa do Mundo 2026.

Uma linha por jogo, com placar e metricas avancadas (xG). Usa dimensao
de papel duplo: dim_selecoes e referenciada duas vezes, uma para o time
mandante e outra para o visitante.
"""
```

- [ ] **Step 3: Verificar**

```bash
cd /home/otaviomaldaner/GitHub/oficina-semana-informatica-2026/.claude/worktrees/refactor-pipeline-declarativa
python3 -m py_compile data-engineering/transformations/*.py && echo "sintaxe OK"
echo "selectExpr no projeto (esperado 0):"
grep -rc "selectExpr" data-engineering/transformations/ | grep -v ":0" || echo "  0 em todos"
echo "mencao a view achatada (esperado 0):"
grep -rc "achatada" data-engineering/transformations/ | grep -v ":0" || echo "  0 em todos"
```

Esperado: `sintaxe OK`; zero `selectExpr`; zero menções a "achatada".

- [ ] **Step 4: Rodar a pipeline — GATE final**

Esperado: verde, DAG completo. Conferir que `gold.dim_arbitros` continua com a coluna `referee_name` (o `AS` do `selectExpr` virou `.alias()`; se o nome tivesse mudado, o `schema` declarado faria a execução falhar).

- [ ] **Step 5: Commit**

```bash
git add data-engineering/transformations/dim_arbitros.py \
        data-engineering/transformations/ft_partidas.py
git commit -m "refactor: padroniza select e corrige docstring obsoleta"
```

---

## Estado final esperado

Ao fim das dez tarefas (**Task 4 cancelada** — ver nota acima):

- `spark.read.table` continua nas 10 leituras bronze→gold (`dim_*`/`ft_*`, incluindo `dim_selecoes.py`) — cancelado por serem cross-pipeline. As 8 leituras gold→gold dos `vw_*` (Task 5) usam `dp.read`.
- `spark.read.csv` permanece intacto na bronze (1 ocorrência).
- Os três `vw_*` são materialized views publicadas em `fifa_world_cup_2026.gold`.
- Casts caíram de 104 para 7 nos `vw_*` (2 de `F.lit(None)` em estabilidade, 5 de conversão real em xPts); os 26 casts de bronze em `ft_eventos.py` e `ft_estatisticas_jogador.py` permanecem intocados.
- `ft_partidas` declara 5 FKs, incluindo `referee_id`.
- Nenhum `selectExpr`, nenhuma docstring obsoleta.
- O DAG mostra as relações gold→vw detectadas automaticamente dentro da pipeline `data-engineering`; a relação bronze→gold não aparece automaticamente no DAG por serem pipelines separadas — permanece como dependência implícita via `spark.read.table`.

## Riscos herdados da spec

| Risco | Onde é tratado |
|---|---|
| `dp.read` não alcançar bronze a partir de gold (pipelines separadas) | **Materializado.** Task 3 confirmado quebrado em execução real; Task 4 cancelada |
| Remover casts alterar tipos de saída | O `schema` declarado de cada MV faz a execução falhar em vez de passar silenciosamente; Tasks 6–8, Steps de GATE |
| Remoção de cast introduzir divisão inteira no modelo de Poisson | Task 8, Step 8 — consulta SQL que verifica se as probabilidades somam 1.0 |
| `DROP` das `vw_*` perder a definição atual | Task 1, Step 2 — `DESCRIBE EXTENDED` antes de destruir |
| Lógica analítica dos `vw_*` ter bugs preexistentes | Fora de escopo; registrar separadamente se a Task 2 revelar erro de resultado |
