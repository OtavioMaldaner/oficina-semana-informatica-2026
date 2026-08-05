# Refactor das pipelines declarativas: `dp.read` e legibilidade

Data: 2026-08-05

## Objetivo

Refatorar as transformações das camadas bronze e gold segundo as práticas da API
`pyspark.pipelines`, substituindo `spark.read.table` por `dp.read` onde a leitura
for de um dataset da própria pipeline, de modo que as relações do DAG sejam
detectadas automaticamente. Em paralelo, remover ruído de código que atrapalha a
leitura do material em sala.

## Contexto

O repositório é material de uma oficina de Ensino Médio (IFRS – Câmpus Feliz)
sobre a Copa do Mundo 2026. Duas pastas de transformações compõem **uma única
pipeline** no Lakeflow Pipelines Editor:

- `data-ingestion/transformations/main.py` — camada bronze, 12 materialized views
  geradas em laço a partir de CSVs de um Volume.
- `data-engineering/transformations/*.py` — camada gold, 13 arquivos
  (5 dimensões, 5 fatos, 3 views analíticas).

**A pipeline não roda hoje.** Ela falha nos três arquivos `vw_*`, adicionados no
commit `4cffcf1` e que nunca chegaram a executar.

### Restrição de projeto: clareza didática vence

Decisão do autor: quando boa prática de produção conflitar com legibilidade para
um aluno de 16 anos, **a legibilidade vence**. Cada transformação deve ser
legível de cima a baixo isoladamente, sem exigir pular de arquivo em arquivo.
Essa restrição é a regra de desempate de todo o documento e justifica as
não-mudanças da seção correspondente.

## Regra de leitura

Toda a decisão do refactor cabe numa tabela. A fronteira é **interno vs. externo
à pipeline**:

| Situação | Ocorrências | Hoje | Depois |
|---|---|---|---|
| bronze lê CSV do Volume | 1 (em laço, 12 tabelas) | `spark.read.csv(...)` | **inalterado** |
| gold lê bronze | 10 | `spark.read.table("fifa_world_cup_2026.bronze.X")` | `dp.read("X")` |
| `vw_*` lê gold | 8 | `spark.read.table("fifa_world_cup_2026.gold.X")` | `dp.read("X")` |
| leitura de tabela externa | 0 | — | `spark.table(...)` se vier a existir |

Consequência: as **18** chamadas `spark.read.table` do projeto são todas
intra-pipeline. Depois do refactor, `spark.read.table` desaparece completamente
da base. `spark.read.csv` permanece — é leitura de arquivo, não de tabela, e não
tem equivalente em `dp.read`.

O ganho didático é direto: a chamada passa a dizer na própria sintaxe se o dado
vem de dentro ou de fora da pipeline, em vez de o aluno ter que reconhecer isso
pelo prefixo do nome.

## Fases

O faseamento existe porque a pipeline nunca ficou verde. Cada fase é um commit e
termina com uma execução observada.

### Fase 1 — Desbloqueio e sonda

Objetivo duplo: fazer a pipeline rodar e descobrir a forma correta de `dp.read`
antes de reescrever treze arquivos.

1. Executar a pipeline e **capturar a mensagem de erro exata** dos `vw_*`.
2. Corrigir os três `vw_*` conforme a causa observada (ver hipóteses em
   Suposições). Independente da causa, os três passam a ser
   `@dp.materialized_view` publicadas em `fifa_world_cup_2026.gold.vw_*`,
   mantendo o bloco `schema` e as constraints `REFERENCES` — decisão já tomada
   pelo autor, para que Genie e Power BI possam consultá-las.
3. Converter **um único** arquivo, `dim_selecoes.py`, para `dp.read`. É o mais
   simples: uma leitura, sem joins, sem casts.
4. Rodar de novo. Verificar (a) que a pipeline fica verde e (b) que o DAG mostra
   a aresta `bronze.teams → gold.dim_selecoes`.

**Critério de saída:** pipeline verde e forma de `dp.read` confirmada
empiricamente.

### Fase 2 — `dp.read` em toda a base

Aplicar a forma confirmada na fase 1 às 17 leituras restantes: 9 arquivos gold
lendo bronze e os 3 `vw_*` lendo gold. Sem outras mudanças no mesmo commit, para
que o diff seja mecânico e auditável.

**Critério de saída:** pipeline verde, DAG com todas as arestas bronze→gold e
gold→vw.

### Fase 3 — Legibilidade e correções de modelagem

1. **Remover os casts redundantes nos `vw_*`.** Os três arquivos somam 104
   chamadas `.cast()`. Como leem de tabelas gold que já declaram `schema`, os
   casts sobre essas colunas são comprovadamente redundantes, e vêm quase sempre
   acompanhados de um `.alias()` para o mesmo nome que a coluna já tem:

   ```python
   # antes
   F.col("lineups.team_id").cast("int").alias("team_id")
   # depois
   F.col("lineups.team_id")
   ```

   Concentra-se nos `select` finais, que hoje ocupam 45–55 linhas cada e devem
   cair para 14–18.

2. **`selectExpr` → `select`** em `dim_arbitros.py`, para alinhar com os outros
   doze arquivos, que usam `select` com `F.col().alias()`.

3. **Docstring obsoleta** em `ft_partidas.py`: menciona "uma view achatada
   (desnormalizada)" que não existe mais no arquivo.

4. **FK faltante:** `ft_partidas.referee_id` não declara
   `REFERENCES fifa_world_cup_2026.gold.dim_arbitros(referee_id)`, enquanto
   todas as outras FKs do modelo declaram. Isso é correção de modelagem, não
   cosmética: o README apoia a importação no Power BI nos relacionamentos PK/FK
   declarados, e essa aresta está faltando.

**Critério de saída:** pipeline verde e comportamento idêntico ao da fase 2.

## O que deliberadamente não muda

Cada item abaixo é uma prática que seria defensável em produção e que é
**rejeitada aqui** pela restrição de clareza didática. Estão listados para que a
omissão fique registrada como escolha, não como esquecimento.

1. **A lógica mandante/visitante duplicada** entre `vw_pontos_recuperados.py` e
   `vw_xpts_selecao_partida.py` (os blocos `home_perspective` /
   `away_perspective` unidos por `unionByName`) **permanece duplicada**. Extrair
   para um módulo compartilhado obrigaria o aluno a abrir um segundo arquivo
   para entender o primeiro.
2. **O catálogo não é parametrizado** via `spark.conf.get("catalog")`, apesar de
   a documentação da Databricks recomendar isso. `fifa_world_cup_2026` continua
   literal no código.
3. **Os casts que leem de bronze permanecem** — 6 em `ft_eventos.py` e 20 em
   `ft_estatisticas_jogador.py`. A bronze lê CSV com `inferSchema=True`, então os
   tipos que chegam são imprevisíveis: esses casts são load-bearing, ao
   contrário dos dos `vw_*`. Esta é a distinção central da fase 3 e não deve ser
   aplicada em bloco.
4. **O prefixo `vw_` é mantido** mesmo com os datasets virando materialized
   views, porque distingue essas três views analíticas das `mv_*`, as Metric
   Views do Genie. Note que a pasta `metric-views/` foi removida no commit
   `4cffcf1` e o README ainda a descreve — a distinção de prefixo continua
   valendo se elas voltarem, e o desalinhamento do README está registrado
   abaixo.

## Suposições não verificadas

Ambas são resolvidas pela fase 1. Nenhuma pode ser resolvida a partir da
documentação — a lista de funções do módulo `pyspark.pipelines` publicada pela
Databricks **omite `read`**, que comprovadamente existe (verificado contra
código de produção fornecido pelo autor). A lista, portanto, não é fonte
confiável de ausência.

**A1 — Forma do argumento de `dp.read`.** O exemplo de produção disponível usa
`dp.read('df_manufacturing_order')` sobre datasets declarados **sem** `name=`,
cujo nome vem do nome da função. Neste projeto todos os datasets são declarados
com nome de três partes (`name="fifa_world_cup_2026.bronze.teams"`). Não se sabe
qual forma resolve. Ordem de tentativa na fase 1:

1. `dp.read("teams")` — nome curto
2. `dp.read("bronze.teams")` — dois níveis
3. `dp.read("fifa_world_cup_2026.bronze.teams")` — qualificado

**Decisão acoplada:** se apenas a forma (1) resolver, adotar `dp.read` exige
também remover a qualificação dos `name=` das declarações, o que é uma mudança
maior que a pedida e interage com o catálogo/schema alvo configurado na
pipeline. Nesse cenário a fase 2 deve ser repactuada com o autor antes de
prosseguir, não executada como planejado.

**A2 — Causa da falha nos `vw_*`.** A falha é observada; a causa não. Hipóteses:
(a) `@dp.view` não existe na API nova e o equivalente é `@dp.temporary_view`;
(b) o decorator existe mas o bloco `schema` com `REFERENCES` é rejeitado nesse
tipo de dataset; (c) o `name=` sem qualificação dos `vw_*` não resolve. A
correção depende de qual for, e o passo 1 da fase 1 existe para descobrir.

## Riscos

| Risco | Mitigação |
|---|---|
| A1 se resolve só com nome curto, exigindo mexer nos `name=` | Fase 1 detecta antes de tocar em 13 arquivos; repactuar escopo |
| Remover casts nos `vw_*` altera tipos de saída | O bloco `schema` de cada MV fixa os tipos; divergência falha a execução em vez de passar silenciosamente |
| Materializar os 3 `vw_*` aumenta uso de storage | Volume de dados de um torneio (104 partidas); desprezível na Free Edition |
| Os `vw_*` nunca rodaram, então a lógica em si pode ter bugs | Fora do escopo deste refactor, que é de forma e não de lógica; registrar como trabalho separado se a fase 1 revelar erros de resultado |

## Fora de escopo

- Correção de eventuais erros na **lógica** analítica dos `vw_*` (Window,
  modelo de Poisson). O refactor preserva comportamento.
- `genie_tools/` e o notebook `genie_creation.ipynb`.
- Atualização do README, exceto se a fase 1 mudar a lista de tabelas publicadas.

### Observação registrada, não tratada aqui

O README descreve uma pasta `metric-views/` com as Metric Views `mv_*` do Genie,
e instrui a executá-las no passo 6 do "Como rodar". Essa pasta **foi removida**
do repositório no commit `4cffcf1` ("fix tables and remove mvs") e não existe
mais. O README está, portanto, desalinhado com o repositório num ponto que afeta
quem tentar seguir a oficina. Isso é anterior e ortogonal a este refactor —
fica registrado como trabalho separado, a ser decidido pelo autor: restaurar as
Metric Views ou corrigir o README.
