# Roteiro de Apresentação do Dashboard RADAR

## 1. Objetivo da Apresentação

Apresentar o dashboard RADAR como um painel analítico para monitoramento do discurso de ódio em plataformas digitais brasileiras, combinando métricas quantitativas, análise temporal, tipologias de preconceito, consulta qualitativa de comentários e camadas semânticas NLI.

Mensagem central:

> O dashboard não substitui análise humana, mas organiza evidências em escala para apoiar leitura crítica, comparação entre plataformas e identificação de padrões de discurso de ódio.

---

## 2. Preparação Antes de Apresentar

### Checklist Técnico

- Abrir o dashboard com antecedência.
- Confirmar que o PostgreSQL está ativo.
- Confirmar que o banco `radar_odio` está acessível.
- Carregar a página inicial antes da apresentação.
- Testar as abas: Plataformas, Categorias de preconceito, Temporal, Nuvem de palavras, NLI, Toxicidade por tipo e Comentários analisados.
- Evitar reiniciar o app durante a apresentação.
- Ter prints ou vídeo curto como plano B, caso o banco demore.
- Deixar palavras-chave prontas para busca qualitativa.

### Buscas Sugeridas Para Demonstração

- `gordo`
- `mulher`
- `feminista`
- `gay`
- `imigrante`
- `religião`
- `Lula`
- `Bolsonaro`
- `nordestino`
- `favela`

Para a busca por gordofobia, use termos como:

- `gordo`
- `gorda`
- `obeso`
- `obesa`
- `corpo`
- `emagrecer`

---

## 3. Abertura da Apresentação

Fala sugerida:

> Este painel foi desenvolvido para analisar discurso de ódio em plataformas digitais brasileiras. A base reúne conteúdos de diferentes ambientes, incluindo plataformas sociais e apps de mensagens. As classificações foram produzidas automaticamente por um modelo de linguagem, o Gemma 3:4b, e o objetivo aqui é observar padrões agregados, não julgar casos individuais de forma definitiva.

Complemento:

> A ideia é combinar uma leitura quantitativa, com volumes e percentuais, com uma leitura qualitativa, olhando trechos, justificativas e evidências apontadas pelo modelo.

---

## 4. Página Inicial: Panorama Multirrede

### O Que Mostrar

- Total de conteúdos analisados.
- Total de conteúdos classificados como discurso de ódio.
- Percentual geral de discurso de ódio.
- Separação entre plataformas sociais e apps de mensagens.
- Tipologias principais.
- Gráfico de toxicidade por tipo.

Fala sugerida:

> A página inicial funciona como um resumo executivo. Aqui eu observo primeiro o tamanho do corpus, depois a proporção geral de discurso de ódio e, em seguida, a distribuição entre tipos de plataforma.

Ponto de atenção:

> É importante ler percentual e volume juntos. Uma plataforma pode ter percentual alto, mas volume pequeno; isso exige cuidado para não superinterpretar o resultado.

---

## 5. Plataformas

### O Que Mostrar

- Comparação entre plataformas sociais e apps de mensagens.
- Volume total por plataforma.
- Percentual de discurso de ódio por plataforma.
- Diferença entre volume absoluto e prevalência percentual.

Fala sugerida:

> Nesta aba, a comparação é feita por plataforma. Eu separo plataformas sociais de apps de mensagens porque são ambientes comunicacionais diferentes. Um espaço aberto, como YouTube ou Twitter, não funciona da mesma maneira que WhatsApp ou Telegram.

Interpretação sugerida:

> O ranking percentual ajuda a identificar prevalência, mas o volume absoluto mostra onde há maior quantidade de ocorrências. As duas leituras precisam caminhar juntas.

---

## 6. Categorias de Preconceito

### O Que Mostrar

- Tipos de preconceito mais frequentes.
- Distribuição das categorias por plataforma.
- Coocorrência entre tipos.

Fala sugerida:

> Aqui o foco deixa de ser apenas quanto discurso de ódio existe e passa a ser que tipo de preconceito aparece. Isso permite diferenciar ódio político, racismo, sexismo, xenofobia, intolerância religiosa, gordofobia e outras categorias.

Ponto metodológico:

> Um mesmo conteúdo pode receber mais de uma categoria. Por isso, as menções por tipo podem somar mais do que o número total de registros classificados como discurso de ódio.

---

## 7. Toxicidade Por Tipo

### O Que Mostrar

- Evolução dos tipos de preconceito ao longo do tempo.
- Percentual de participação de cada tipo.
- Ranking do período.

Fala sugerida:

> Este gráfico mostra a participação de cada tipo de preconceito entre as menções classificadas como discurso de ódio. Ele é útil para observar mudanças de composição ao longo do tempo, e não apenas volume bruto.

Como explicar:

> Se uma linha sobe, isso significa que aquele tipo passou a representar uma fatia maior das menções de discurso de ódio naquele período.

Cuidados:

> A leitura temporal depende da qualidade das datas disponíveis e da distribuição da coleta. Picos podem refletir eventos sociais, mudanças na coleta ou concentração de conteúdos em determinados períodos.

---

## 8. Temporal

### O Que Mostrar

- Evolução do volume total.
- Evolução do volume de discurso de ódio.
- Percentual ao longo do tempo.
- Picos e quedas.

Fala sugerida:

> A aba temporal permite observar quando o discurso de ódio aparece com mais intensidade. Essa leitura pode ajudar a levantar hipóteses sobre eventos políticos, sociais ou midiáticos associados a aumentos no volume.

Frase de cautela:

> O gráfico mostra associação temporal, não causalidade. Para afirmar causa, seria necessário cruzar com eventos externos e fazer validação qualitativa.

---

## 9. Nuvem de Palavras

### O Que Mostrar

- Termos frequentes nos conteúdos classificados.
- Filtros por plataforma, classificação, tipo de conteúdo e tipo de preconceito.
- Comparação entre evidência textual do modelo e texto completo.

Fala sugerida:

> A nuvem de palavras ajuda a observar vocabulário recorrente. Ela não prova sozinha a existência de discurso de ódio, mas orienta a leitura qualitativa e ajuda a encontrar termos de alto rendimento analítico.

Exemplo de demonstração:

> Vou filtrar por discurso de ódio e pesquisar o termo “gordo”. Assim conseguimos observar como aparecem comentários relacionados a corpo, aparência e culpabilização individual.

---

## 10. Comentários Analisados

### O Que Mostrar

- Filtro por plataforma.
- Busca por palavra-chave.
- Comentário analisado.
- Classificação.
- Probabilidade de discurso de ódio.
- Tipos de preconceito.
- Evidência textual.
- Justificativa curta do modelo.
- Alvo identificado.

Fala sugerida:

> Esta é a parte qualitativa do painel. Aqui eu consigo sair do agregado e examinar exemplos concretos. O objetivo não é tratar um comentário isolado como prova estatística, mas entender como o modelo justificou a classificação.

Exemplo com gordofobia:

> Ao buscar “gordo”, posso observar se o comentário usa o termo apenas de forma descritiva, autodepreciativa, crítica ou como ataque dirigido a uma pessoa ou grupo. Essa distinção é importante para interpretar a classificação.

Frase de cuidado:

> Como a classificação é automatizada, os exemplos devem ser vistos como pistas analíticas. Casos sensíveis exigem revisão humana.

---

## 11. NLI: Análise Semântica

### O Que Mostrar

- Camada 3.
- Camada 4.
- Relação entre toxicidade semântica e classificação Gemma.
- Diferenças por plataforma.
- Dimensões predominantes.

Fala sugerida:

> A análise semântica adiciona uma camada complementar. Enquanto a classificação Gemma identifica discurso de ódio e tipos de preconceito, as camadas NLI ajudam a observar relações semânticas mais finas, como intensidade, enquadramento e dimensões discursivas.

Ponto de interpretação:

> Essa camada não deve ser lida isoladamente. Ela funciona melhor quando combinada com os resultados de classificação e com a leitura qualitativa dos exemplos.

---

## 12. Interseccionalidade

### O Que Mostrar

- Sobreposição entre tipos de preconceito.
- Pares de categorias que aparecem juntas.
- Matriz de coocorrência.

Fala sugerida:

> Nesta aba, observo quando diferentes tipos de preconceito aparecem juntos. Isso é importante porque discursos discriminatórios raramente são isolados; muitas vezes combinam raça, gênero, política, religião, classe ou corpo.

Frase de cautela:

> Coocorrência não significa necessariamente relação causal. Ela indica que categorias apareceram juntas em registros classificados pelo modelo.

---

## 13. Como Responder Perguntas Prováveis

### “O modelo acerta sempre?”

Resposta:

> Não. A classificação é automatizada e pode conter falsos positivos e falsos negativos. Por isso o painel separa métricas agregadas, evidências textuais e justificativas, permitindo auditoria humana.

### “Por que não olhar só percentual?”

Resposta:

> Porque percentual sem volume pode distorcer a leitura. Uma plataforma com poucos registros pode parecer muito problemática proporcionalmente, mas ter baixa sustentação amostral.

### “Um comentário pode ter mais de um tipo de preconceito?”

Resposta:

> Sim. Um mesmo conteúdo pode conter múltiplos tipos de preconceito. Por isso, nas tipologias, contamos menções por categoria, não apenas registros únicos.

### “A nuvem de palavras prova discurso de ódio?”

Resposta:

> Não. Ela mostra frequência lexical. A interpretação precisa considerar contexto, classificação, evidência textual e leitura qualitativa.

### “Dá para concluir que uma plataforma é pior que outra?”

Resposta:

> Dá para comparar padrões observados no dataset, mas com cautela. As diferenças dependem do volume coletado, do período, do tipo de conteúdo e do viés da coleta.

---

## 14. Fechamento

Fala sugerida:

> Em síntese, o dashboard permite monitorar discurso de ódio em escala, comparar plataformas, observar tipos de preconceito, acompanhar variações temporais e acessar evidências qualitativas. A contribuição principal é organizar o fenômeno de forma exploratória e auditável, sempre preservando a leitura crítica sobre limites da classificação automatizada.

Frase final:

> O painel deve ser entendido como uma ferramenta de apoio à pesquisa, à curadoria analítica e à validação humana, não como uma sentença definitiva sobre cada conteúdo.

---

## 15. Ordem Recomendada Para Demonstração Ao Vivo

1. Página inicial.
2. Plataformas.
3. Categorias de preconceito.
4. Toxicidade por tipo.
5. Temporal.
6. Nuvem de palavras.
7. Comentários analisados.
8. NLI.
9. Interseccionalidade.
10. Limitações e fechamento.

---

## 16. Versão Curta Para Falar Em 2 Minutos

> Este dashboard analisa discurso de ódio em plataformas digitais brasileiras a partir do banco `radar_odio`. A classificação foi produzida pelo modelo Gemma 3:4b e está organizada por plataforma, tipo de conteúdo, tipo de preconceito e período.
>
> Na página inicial, temos o panorama geral: total de conteúdos, total e percentual de discurso de ódio, comparação entre plataformas sociais e apps de mensagens, além das principais tipologias. Depois, nas páginas internas, aprofundo a comparação por plataforma, a distribuição das categorias de preconceito, a evolução temporal e as análises semânticas NLI.
>
> A parte qualitativa aparece na consulta de comentários, onde é possível ler o texto, a evidência apontada pelo modelo e a justificativa da classificação. Isso é importante porque os números indicam padrões, mas os exemplos ajudam a interpretar como esses padrões aparecem na linguagem.
>
> Por fim, é importante destacar que os resultados são automatizados e podem conter erros. Portanto, o painel deve ser usado como apoio à análise, sempre com validação humana e leitura metodológica cuidadosa.

