# Dashboard Radar de Ódio — TypeScript

Reescrita completa do dashboard em **TypeScript**: React + Vite no cliente, Fastify +
`pg` no servidor, **ECharts** para os gráficos. Fonte de dados: a view de
compatibilidade `public.v_bert_hate_results`, que expõe a tabela do pipeline BERT
`public.periodo_eleicoes_1_turno_bert` (bancos `radar_odio`).

## Por que ficou mais responsivo

- SPA renderizada no cliente (sem recarregar a página ao navegar entre seções).
- Gráficos ECharts redimensionados por `ResizeObserver` (`src/components/EChart.tsx`).
- Layout com breakpoints: a barra de navegação rola na horizontal em telas estreitas e
  o cabeçalho enxuga (contexto e subtítulo da marca somem abaixo de 860/720px);
  tabelas com rolagem própria e cards empilhados em telas estreitas.
- **Filtros globais na URL** (`?platforms=…&predLabels=…`): o recorte vale para todas
  as páginas, é compartilhável e sobrevive ao F5.

## Como rodar

```bash
npm install

# desenvolvimento (API + cliente com hot reload)
npm run dev            # cliente em http://localhost:5173

# produção (build do cliente + servidor Fastify servindo tudo)
npm run build
npm start              # http://localhost:8787
```

Variáveis opcionais: `API_PORT` (default `8787`), `DASHBOARD_MIN_DATE`
(default `2026-09-01`), `MODEL_NAME` (default `radarodio-v01-bert`), `DATABASE_URL`.

A conexão é resolvida assim: `DATABASE_URL` → `.env` do pipeline
(`../Trabalho Radar Ódio/social_data_pipeline/.env`, que aponta para o Postgres
oficial na porta 5433) → variáveis `DB_*`. Nenhuma credencial vai para o cliente:
todo acesso ao banco passa pelo servidor.

## Estrutura

```
dashboard_radar_ts/
├── shared/labels.ts        rótulos, hierarquia de categorias e cores
├── server/
│   ├── db.ts               conexão (pg) + janela do painel
│   ├── queries.ts          todas as consultas SQL (parametrizadas)
│   └── index.ts            rotas /api/* + estáticos (SPA fallback)
└── src/
    ├── api.ts              cliente HTTP, formatadores pt-BR, IC de Wilson
    ├── filters.tsx         filtros globais persistidos na URL
    ├── components/         EChart, cards/KPI/tabela, filtros, probabilidades
    └── pages/              12 páginas
```

## API

| Rota | Conteúdo |
|---|---|
| `GET /api/meta` | opções de filtro, modelo, janela e contagem |
| `GET /api/overview` | KPIs, comparativo com período anterior, série diária, tipos |
| `GET /api/platforms` | volume/taxa por plataforma e tipo de conteúdo |
| `GET /api/categories` | frequência, plataforma × tipo, coocorrência |
| `GET /api/category-probabilities` | média/mediana/máx. por categoria (hierarquia) |
| `GET /api/temporal?grain=` | série por dia/semana/mês/ano |
| `GET /api/toxicity?grain=&limit=` | participação e volume por tipo |
| `GET /api/intersectionality` | matriz de sobreposição |
| `GET /api/authors` | perfis anonimizados |
| `GET /api/posts` | threads e posts |
| `GET /api/threads?limit=` | respostas × 1º nível, taxa por tamanho de thread e posts que mais atraem ódio |
| `GET /api/threshold` | curva de sensibilidade, histograma e fronteira real de decisão do modelo |
| `GET /api/records/post/:key` | registros de uma thread |
| `GET /api/network` | arestas do grafo |
| `GET /api/terms` | termos frequentes (geral e ódio) |
| `GET /api/quality` | duplicatas, vazios, datas, rótulos nulos |

Todas aceitam os filtros globais: `platforms`, `contentKinds`, `predLabels`,
`hateTypes`, `dateStart`, `dateEnd`, `search` (listas separadas por vírgula) e
`excludePolitical=1` (flag: retira os conteúdos cujo **único** tipo de ódio é o
político; quem é político + outro preconceito permanece).

## Melhorias de análise em relação à versão anterior

1. **Intervalo de confiança de Wilson (95%)** na taxa de ódio por plataforma — evita
   ler percentuais instáveis de amostras pequenas.
2. **Comparativo com o período anterior** de mesma duração no panorama (deltas nos KPIs).
3. **Média móvel de 7 dias** na série diária.
4. **Probabilidade média/mediana/máxima por categoria** (e quantos registros passam
   de 0,50), montada na ordem da hierarquia de tipos.
5. **Volume vs. prevalência** (dispersão em escala log) para plataformas e threads.
6. **Filtros globais** aplicados a todas as análises, com recorte por período,
   plataforma, tipo, classificação, tipologia e busca textual.
7. **Painel de qualidade dos dados** (duplicatas, textos vazios, datas, rótulos nulos).
8. **Probabilidades por categoria por registro** (detalhe de comentário/thread), em
   substituição aos campos que vinham do modelo LLM (alvo/justificativa), removidos.

## Correções aplicadas

- **Busca com debounce (400 ms)**: antes cada tecla disparava um `ILIKE` sobre toda a
  base; agora 5 teclas digitadas viram 1 requisição.
- **Guarda de corrida no `useApi`**: respostas antigas não sobrescrevem mais a mais recente.
- **Aviso de versão** (`src/components/UpdateBanner.tsx`): a SPA não se recarrega sozinha
  quando o `dist/` é republicado, então ela compara o bundle carregado com o do
  `index.html` atual (a cada 60 s, ao voltar o foco e ao ficar visível) e mostra um
  botão "Recarregar" no canto. Sem isso, quem já está com a página aberta continua vendo
  a versão antiga sem ter como saber.
- **Evolução diária** (Panorama) mostra **apenas** as barras de discurso de ódio: a série
  de "Conteúdos" e a linha de taxa saíram (com ela, o 2º eixo e a legenda). **Evolução**
  (Temporal) também ficou só com o ódio; a taxa continua em card próprio naquela página.
- **Paginação**: volta à página 1 e fecha o detalhe ao mudar qualquer filtro; a página
  é limitada ao total de páginas do recorte atual.
- **Período anterior** no panorama agora mede a duração pelo intervalo de datas
  observado (buracos na série não encolhem mais a janela de comparação).
- **Grafo da Rede**: nó recebe categoria pelo seu prefixo (`rede`/`tipo`/`conteudo`),
  não pela posição na aresta — antes o mesmo nó trocava de cor; legenda corrigida.
- **Datas invertidas** no filtro são ajustadas automaticamente, com aviso na tela.
- Botões de ação (abrir/ver) receberam rótulo acessível e o "Limpar" passou a limpar
  todos os filtros, não só as listas.

## Design

- Design system em `src/styles/` (base, filtros, componentes, responsivo) com tokens
  de cor, raio e sombra, **tema claro/escuro** alternável (persistido em
  `localStorage`, respeita `prefers-color-scheme`).
- Navegação em **barra horizontal fixa no topo**: marca à esquerda, contexto (registros
  classificados e janela) e alternador de tema à direita, e uma faixa de seções em
  *pills* logo abaixo, **centralizada** na largura da janela. A barra é *sticky*, então as seções continuam à mão durante a
  rolagem, e rola sozinha na horizontal quando não cabe. O conteúdo usa a **largura
  inteira** da janela (antes o menu lateral de 250px comia esse espaço).
- Filtros em **barra única**: busca textual à esquerda, menus suspensos (Plataforma,
  Tipo, Classificação, Tipos de preconceito, Período) e a alavanca **"Sem ódio político"**
  — todos fecham ao clicar fora ou com Esc. A alavanca remove da análise os conteúdos cujo
  único tipo é o ódio político (político + outro preconceito continua contando), o que muda
  numerador e denominador das taxas em todas as páginas. Cada filtro aparece **uma vez só** — como chip removível abaixo da barra, com
  contador e "Limpar tudo". O menu de período traz atalhos (todo o período, últimos 3/7/15 dias).
  No mobile os menus viram folha inferior e a barra reorganiza em 2 colunas.
- KPIs com trilho de destaque e chip de variação colorido; tabelas com linhas
  zebradas e cabeçalho fixo; carregamento com *skeleton* em vez de texto.
- Nuvem de palavras desenhada no cliente (layout em espiral com detecção de colisão,
  tamanho por frequência, cores por tema); termos com stopwords de português e inglês
  removidos na consulta.
- Cores de eixo/grid dos gráficos escolhidas para funcionar nos dois temas.

## Observações de dados

- O painel mostra apenas a janela do período eleições (`DASHBOARD_MIN_DATE` → hoje) e
  registros classificados (`status = 'ok'`).
- O fluxo de classificação é hierárquico: o modelo multilabel só roda quando o binário
  aponta ódio, então categorias existem apenas em registros de ódio.
- Sem métricas de engajamento e sem `alvo`/`justificativa`: a tabela BERT não as produz.
