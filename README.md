# Dashboard Radar de Ódio

Dashboard Streamlit para análise de discurso de ódio em múltiplas redes sociais
no banco PostgreSQL `radar_odio`.

O painel usa como fonte principal a view `public.v_gemma_hate_results`, com
resultados do modelo `gemma3:4b`. Quando disponíveis, também exibe agregações
das views `public.v_radar_nli_layer3_results` e
`public.v_radar_nli_layer4_results`.

## Como Rodar Localmente

```powershell
cd "C:\Users\carlo\OneDrive\Documents\ESTUDOS\MESTRADO\Trabalho Radar Ódio\dashboard_radar"
python -m pip install -r requirements.txt
python run_dashboard.py
```

O app abre em `http://localhost:8501`.

## Acesso Externo com Cloudflare Tunnel

O projeto inclui um script para publicar o dashboard via Cloudflare Tunnel sem
expor o servidor Streamlit diretamente para a internet.

### 1. Instalar o cloudflared

```powershell
winget install --id Cloudflare.cloudflared
```

Feche e abra o PowerShell depois da instalação, para atualizar o `PATH`.

### 2. Abrir uma URL temporária

Use este modo para compartilhar rapidamente o dashboard:

```powershell
cd "C:\Users\carlo\OneDrive\Documents\ESTUDOS\MESTRADO\Trabalho Radar Ódio\dashboard_radar"
.\scripts\start_cloudflare_tunnel.ps1
```

O terminal vai mostrar uma URL parecida com:

```text
https://algum-nome.trycloudflare.com
```

Envie essa URL para as pessoas acessarem o painel enquanto o terminal estiver
aberto.

### 3. Usar um domínio fixo

Se você tiver um domínio configurado na Cloudflare:

```powershell
cloudflared tunnel login
.\scripts\start_cloudflare_tunnel.ps1 -Hostname "radar.seudominio.com" -TunnelName "radar-dashboard"
```

Não coloque tokens, credenciais do banco ou arquivos `.pem` dentro do projeto.
O túnel deve ficar autenticado pela instalação local do `cloudflared`.

## Banco de Dados

O dashboard procura a conexão nesta ordem:

1. `POSTGRES_URI` ou `DATABASE_URL` no `.env` do próprio dashboard.
2. `POSTGRES_URI` no arquivo `.env` da pasta irmã `social_data_pipeline`.
3. Variáveis separadas como `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e
   `DB_PASSWORD`.

Nenhuma credencial é exibida na interface.

## Comportamento Atual

- Não há filtro global lateral.
- As páginas carregam o banco completo por padrão.
- A navegação lateral fica apenas para trocar de página.
- A página de busca tem um campo próprio: vazio mostra a base paginada; preenchido pesquisa o termo.
- A página de comentários analisados tem filtro local por plataforma.
- As consultas seguem agregando e paginando no PostgreSQL.
- Análises temporais ignoram datas futuras em relação ao dia atual.

## Views Usadas

- `v_gemma_hate_results`: fonte principal das análises de hate e não hate.
- `v_gemma_hate_summary`: apoio para opções e agregações leves.
- `v_radar_nli_layer3_results`: análises NLI layer 3.
- `v_radar_nli_layer4_results`: análises NLI layer 4.

## Páginas

- Plataformas: volume, prevalência, fontes, idioma e comparação entre plataformas sociais e apps de mensagens.
- Categorias: tipologias, categorias Gemma, coocorrência e probabilidades.
- Temporal: evolução por mês, semana, dia ou ano.
- Busca: consulta textual e tabela paginada.
- Léxico: termos frequentes e nuvem de palavras.
- Rede: grafo entre redes, conteúdo, tipos e coocorrências.
- Autores: perfis anonimizados e concentração de hate.
- Posts: posts/threads com maior concentração de hate.
- NLI layers: layer 3 e layer 4.
- Toxicidade por tipo: série temporal por hate_type, com média de `hate_probability`.
- Comentários e LLM: consulta de comentários, evidência textual, alvo e justificativa da Gemma.
