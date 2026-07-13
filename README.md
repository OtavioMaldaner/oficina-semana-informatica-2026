# Da Bola aos Dados: Engenharia e Ciência de Dados na Copa do Mundo 2026

Oficina de Ciências e Engenharia de Dados da Semana da Informática do IFRS – Câmpus Feliz, para turmas do Ensino Médio.

Usando estatísticas reais da Copa do Mundo 2026 (a primeira com 48 seleções, sediada por Estados Unidos, México e Canadá), a turma percorre a jornada completa de um dado: ingestão de arquivos brutos no Databricks, modelagem em um star schema, construção de uma pipeline declarativa, criação de uma camada semântica para consultas em linguagem natural com o Databricks Genie, e visualização final no Power BI.

## Sobre os dados

Os dados vêm do **[FIFA World Cup 2026 Dataset – Live & Updated Stats](https://www.kaggle.com/datasets/mominullptr/fifa-world-cup-2026-dataset)**, de MD Mominul Islam, publicado no Kaggle sob licença **CC0-1.0 (domínio público)**. É um dataset já relacional (não um CSV único e achatado), o que o torna especialmente adequado para ensinar modelagem dimensional — o [repositório no GitHub do autor](https://github.com/mominullptr/FIFA-World-Cup-2026-Dataset) documenta o diagrama de entidade-relacionamento original.

Como o torneio estava em andamento durante a preparação desta oficina (11/jun a 19/jul de 2026), o dataset é atualizado continuamente pelo mantenedor. Os arquivos usados aqui são um retrato (*snapshot*) baixado manualmente — não há download automático de dentro do Databricks (ver seção de pré-requisitos).

## Arquitetura

Arquitetura Medallion com três destinos dentro do catálogo Unity Catalog `fifa_world_cup_2026`:

```
Volume (CSVs brutos)  →  bronze (1 tabela por arquivo)  →  gold (star schema)  →  Genie / Power BI
fifa_world_cup_2026.raw_data.bronze   fifa_world_cup_2026.bronze.*   fifa_world_cup_2026.gold.*
```

A camada gold segue um modelo dimensional clássico (star schema):

| Tabela | Tipo | Descrição |
|---|---|---|
| `dim_selecoes` | Dimensão | Seleções participantes: nome, código FIFA, grupo, confederação, ranking pré-torneio |
| `dim_estadios` | Dimensão | Estádios sede nos EUA, México e Canadá: cidade, capacidade, altitude |
| `dim_etapas` | Dimensão | Fases do torneio (grupos até final), com flag de mata-mata |
| `dim_jogadores` | Dimensão | Elenco convocado: posição, clube, altura, data de nascimento — FK para `dim_selecoes` |
| `dim_arbitros` | Dimensão | Árbitros principais e sua média histórica de cartões |
| `ft_partidas` | Fato | Uma linha por jogo: placar, xG. `home_team_id`/`away_team_id` referenciam `dim_selecoes` duas vezes (dimensão de papel duplo) |
| `ft_eventos` | Fato | Um evento por linha: gol, cartão, assistência, revisão de VAR — grão mais fino do modelo |
| `ft_estatisticas_equipe` | Fato | Posse, chutes, escanteios, faltas por seleção por partida |
| `ft_estatisticas_jogador` | Fato | Estatísticas acumuladas do torneio inteiro por jogador (artilharia, assistências, nota média) |
| `ft_escalacoes` | Fato | Uma linha por jogador convocado por partida: titular ou reserva, posição tática, minutos jogados |

Sobre essa base, `metric-views/` define **Metric Views** (`fifa_world_cup_2026.gold.mv_*`) — uma camada semântica em YAML com dimensões e métricas de negócio nomeadas em português, pensada especificamente para o **Databricks Genie** responder perguntas em linguagem natural. Vale notar: o conector do Power BI para Databricks não reconhece nativamente as métricas de uma Metric View (ele consulta a view como uma tabela comum) — por isso o Power BI se conecta direto nas tabelas `gold.dim_*`/`gold.ft_*`, usando os relacionamentos PK/FK já declarados nelas, e não nas `mv_*`.

## Estrutura do repositório

```
assets/                              CSVs brutos (upload manual no Volume)
data-ingestion/transformations/      Pipeline declarativa — camada bronze (leitura crua dos CSVs)
data-engineering/transformations/    Pipeline declarativa — camada gold (dimensões e fatos)
metric-views/                        Metric Views em SQL/YAML para o Genie
```

## Pré-requisitos

- **Conta no Databricks Free Edition** (gratuita, sem cartão de crédito) — [cadastro](https://www.databricks.com/learn/free-edition) · [documentação oficial](https://docs.databricks.com/aws/en/getting-started/free-edition). A Free Edition roda em ambiente serverless com acesso à internet restrito — por isso o download dos CSVs precisa acontecer *antes*, fora do notebook.
- **Power BI Desktop** (Windows) — [download](https://www.microsoft.com/en-us/power-platform/products/power-bi/desktop)
- Opcional: **conta no Kaggle**, só se quiser baixar uma versão mais atualizada do dataset — [cadastro](https://www.kaggle.com/account/login)

## Como rodar

1. Crie sua conta no Databricks Free Edition.
2. No Catalog Explorer, crie o catálogo `fifa_world_cup_2026`, o schema `raw_data` e, dentro dele, o Volume `bronze`.
3. Baixe os CSVs listados em `assets/` (mais `teams.csv` e `venues.csv` do Kaggle) e faça upload no Volume pela interface (`Upload` → selecionar arquivos).
4. Crie uma pipeline no Lakeflow Pipelines Editor com catálogo de destino `fifa_world_cup_2026`, e adicione os arquivos de `data-ingestion/transformations/` e `data-engineering/transformations/` como transformações.
5. Rode a pipeline e confira o DAG bronze → gold.
6. Execute os scripts de `metric-views/` no SQL editor para criar as Metric Views.
7. Crie um Genie Space apontando para as tabelas `gold.mv_*` e teste perguntas em português.
8. Abra o Power BI Desktop, conecte no SQL Warehouse do Databricks e importe as tabelas `gold.dim_*` / `gold.ft_*`.

## Referências

- [FIFA World Cup 2026 Dataset – Live & Updated Stats (Kaggle)](https://www.kaggle.com/datasets/mominullptr/fifa-world-cup-2026-dataset)
- [Schema/ER diagram do dataset (GitHub)](https://github.com/mominullptr/FIFA-World-Cup-2026-Dataset)
- [Cadastro no Databricks Free Edition](https://www.databricks.com/learn/free-edition)
- [Documentação da Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition)
- [Lakeflow Declarative Pipelines](https://docs.databricks.com/aws/en/dlt/)
- [Metric Views](https://docs.databricks.com/aws/en/business-semantics/metric-views/create-edit)
- [Databricks Genie](https://docs.databricks.com/aws/en/genie/)
- [Download do Power BI Desktop](https://www.microsoft.com/en-us/power-platform/products/power-bi/desktop)