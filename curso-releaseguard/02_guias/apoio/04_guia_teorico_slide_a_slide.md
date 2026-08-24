# ReleaseGuard AI — Guia de fala slide a slide

> Este não é um resumo do deck. É um roteiro oral para explicar os 81 slides com profundidade, exemplos e conexões que não estão escritos na tela. Use a fala como apoio, não como texto para leitura literal.

## Como usar durante a aula

Em cada slide, comece por **Fala sugerida**, porque ali está o argumento completo. Use **Exemplo além do slide** quando precisar tornar a ideia concreta. A pergunta já vem acompanhada da resposta que vale a pena construir com a turma. Termine com a transição indicada para que a apresentação pareça uma narrativa contínua, e não 81 tópicos independentes.

Os comandos, checkpoints e procedimentos operacionais continuam nos guias de implementação de cada dia. Aqui o foco é dar repertório para explicar o significado das decisões técnicas.

---

# Dia 1 — QA funcional low-code

## Slide 01 — RELEASEGUARD AI: QA FUNCIONAL LOW-CODE

**Fala sugerida.** “Nesta semana nós não vamos estudar três projetos separados. Vamos acompanhar a mesma aplicação enquanto mudamos a pergunta de engenharia. No primeiro dia, perguntamos se uma regra de negócio funciona. No segundo, se a interface mudou de uma maneira relevante. No terceiro, por que o sistema está lento e se ainda é seguro liberar uma versão. A IA aparece nos três dias, mas nunca como fonte automática da verdade. Ela ajuda a propor, organizar ou interpretar. Quem transforma isso em evidência são contratos, execução real, métricas e políticas explícitas. Essa diferença é o fio condutor da semana.”

**Exemplo além do slide.** Um modelo pode escrever um caso de teste impecável em português e ainda usar um produto inexistente. Pode descrever corretamente um botão deslocado e errar o impacto. Pode produzir uma RCA convincente sem consultar uma única métrica. O curso começa justamente onde termina a demonstração superficial de IA.

**Pergunte à turma.** “Qual dessas três situações seria mais perigosa se aceitássemos a resposta da IA sem evidência?”

**Resposta que vale construir.** Todas podem causar dano, mas a gravidade muda conforme a autoridade concedida: sugerir texto é menos arriscado que bloquear release ou executar uma remediação.

**Transição.** “Por isso, antes de falar de ferramenta, precisamos falar sobre confiança.”

<!-- deck-primary: Um mesmo sistema será observado por três lentes: QA funcional, regressão visual e investigação SRE. -->
<!-- deck-engineering: IA amplia proposta e interpretação; contratos, evidência e política continuam determinísticos. -->
<!-- deck-caution: O objetivo não é revisar conceitos básicos de agentes nem vender autonomia total. -->
<!-- deck-question: Que automação vocês aceitariam sem revisão humana? -->

## Slide 02 — O PROBLEMA: TESTE GERADO NÃO É TESTE CONFIÁVEL

**Fala sugerida.** “Um teste não é confiável porque o código parece profissional. Ele é confiável quando sabemos o que está sendo exercitado, de onde veio o resultado esperado e que evidência foi realmente observada. LLMs são muito bons em produzir artefatos plausíveis: nomes de teste convincentes, steps organizados e explicações que soam corretas. O risco é que plausibilidade visual encobre erros semânticos. Um teste pode chamar o endpoint errado, usar um status que a API nunca documentou ou passar porque não chegou à condição que pretendia verificar. Nossa arquitetura separa três responsabilidades: o modelo propõe, o software valida e executa, e o oracle decide se o observado corresponde ao esperado.”

**Exemplo além do slide.** Imagine um teste chamado “bloqueia estoque insuficiente” que cria o carrinho, mas nunca adiciona o item. Ele pode terminar em HTTP 200 e ser reportado como sucesso se o oracle for mal definido. O nome do teste não prova que a regra foi exercitada.

**Pergunte à turma.** “Um teste que sempre passa pode ser pior do que não ter teste?”

**Resposta que vale construir.** Sim. Ele produz falsa confiança e pode autorizar uma release que não foi realmente verificada.

**Transição.** “Vamos então ver quais componentes produzem evidência e qual deles realmente decide o resultado.”

<!-- deck-primary: LLM pode gerar um teste plausível que verifica a coisa errada; confiança exige evidência verificável. -->
<!-- deck-engineering: Separar proposta probabilística, validação/execução determinística e oracle de engenharia. -->
<!-- deck-caution: Código bem formatado e JSON válido não demonstram correção semântica. -->
<!-- deck-question: Um teste que sempre passa pode ser pior que nenhum teste? -->

## Slide 03 — SISTEMA CENTRAL E EVIDÊNCIAS

**Fala sugerida.** “Este diagrama não é uma lista de tecnologias. Cada componente responde a uma pergunta diferente. FastAPI oferece comportamento real e contrato OpenAPI. A interface fornece um estado renderizado que o browser consegue capturar. Ollama propõe planos e interpreta imagens ou evidências. n8n torna a orquestração visível. Playwright controla a observação da UI. Prometheus responde sobre tendência e magnitude; Jaeger mostra o caminho e a duração de requisições específicas. O ponto importante é que todos observam a mesma aplicação e deixam artefatos que podem ser auditados depois. No final, o relatório de release não recebe uma opinião solta: recebe reports funcionais, métricas visuais e uma investigação SRE estruturada.”

**Exemplo além do slide.** Se o teste funcional passa, mas Prometheus mostra uma dependência degradada, as duas evidências não se anulam. Elas respondem a perguntas diferentes. A política final precisa combinar esses sinais sem fingir que existe um único score universal de qualidade.

**Pergunte à turma.** “Qual componente do desenho decide sozinho se a release passa?”

**Resposta que vale construir.** Nenhuma ferramenta isolada. A decisão nasce da política aplicada aos artefatos produzidos.

**Transição.** “Agora podemos definir o que low-code significa dentro dessa arquitetura.”

<!-- deck-primary: Uma aplicação comum produz evidências funcionais, visuais e operacionais que podem ser combinadas. -->
<!-- deck-engineering: Tratar ferramentas por responsabilidade e contrato, não como uma coleção de produtos. -->
<!-- deck-caution: Evidências diferentes respondem a perguntas diferentes e não devem virar um score arbitrário. -->
<!-- deck-question: Qual componente realmente decide se o teste ou a release passou? -->

## Slide 04 — DEFINIÇÃO CANÔNICA: LOW-CODE TESTING

**Fala sugerida.** “Low-code testing não significa testar sem código e também não significa permitir que qualquer pessoa automatize qualquer ação. Significa deslocar parte da composição do fluxo para abstrações configuráveis — nodes, conexões, formulários, expressões — enquanto os pontos que exigem garantia continuam implementados como contratos e código. No nosso caso, n8n mostra a sequência e facilita integração, mas não inventa a política de autorização nem substitui o executor. Pense em low-code como uma camada de composição: ela reduz o esforço de conectar etapas, mas não elimina a necessidade de definir o que cada etapa pode receber, produzir e fazer.”

**Exemplo além do slide.** Um HTTP Request node economiza código de plumbing. Mas, se ele aceitar qualquer URL gerada por um modelo, a facilidade de composição virou ampliação de risco. O desenho seguro é fazer o node chamar um endpoint controlado que valida o plano inteiro.

**Pergunte à turma.** “Onde termina a conveniência visual e começa a fronteira de segurança?”

**Resposta que vale construir.** Na capacidade efetiva: hosts, métodos, paths, credenciais e mutações precisam de controles independentes da interface.

**Transição.** “Para controlar um teste, primeiro precisamos distinguir o caso executado do mecanismo que julga o resultado.”

<!-- deck-primary: Low-code desloca composição para abstrações visuais sem eliminar contratos e extensões em código. -->
<!-- deck-engineering: n8n reduz plumbing; schema, policy e executor preservam a fronteira confiável. -->
<!-- deck-caution: Low-code e no-code são espectros, não selos de segurança ou qualidade. -->
<!-- deck-question: Onde um workflow visual precisa voltar ao código para ser seguro? -->

## Slide 05 — DEFINIÇÃO CANÔNICA: TEST CASE E TEST ORACLE

**Fala sugerida.** “Um test case descreve precondições, dados, ações e resultados esperados. O test oracle é o mecanismo que permite decidir se o comportamento observado está correto. Essa distinção importa porque executar passos não basta. O oracle pode vir de uma regra de negócio, de um contrato de API, de uma propriedade matemática, de uma versão anterior aprovada ou até de revisão humana. No exemplo de estoque, o valor esperado não surge porque o modelo prefere 409. Ele vem do comportamento documentado para uma tentativa que conflita com o estoque disponível. Se não conseguimos explicar a origem do esperado, temos um script, não uma evidência defensável.”

**Exemplo além do slide.** Em um cálculo de imposto, o oracle pode ser uma tabela legal. Em uma busca, pode ser um conjunto parcial de resultados relevantes. Em uma imagem, raramente existe um único pixel que diga “correto”; por isso o Dia 2 combinará métricas, região e julgamento.

**Pergunte à turma.** “Quem tem autoridade para alterar o resultado esperado de um teste?”

**Resposta que vale construir.** Quem governa o requisito ou contrato, com revisão e rastreabilidade — não o gerador do teste por conveniência.

**Transição.** “Vamos sair da definição e observar um resultado real antes de introduzir mais camadas.”

<!-- deck-primary: Test case organiza a execução; test oracle decide se o comportamento observado está correto. -->
<!-- deck-engineering: Ancorar o esperado em requisito, contrato ou evidência externa ao modelo gerador. -->
<!-- deck-caution: Oracles podem ser explícitos, parciais ou humanos; não existe uma forma universal. -->
<!-- deck-question: De onde vem o esperado de um teste gerado por IA? -->

## Slide 06 — EXECUTAR ANTES DE TEORIZAR

**Fala sugerida.** “A ordem deste curso é deliberada. Primeiro vamos provocar um comportamento observável; depois daremos nome às decisões que o tornaram confiável. Quando alguém vê uma chamada retornar 409, a discussão sobre oracle deixa de ser abstrata. Quando vê um JSON estruturalmente válido ser rejeitado pela policy, a diferença entre formato e autorização fica concreta. Essa estratégia também evita uma armadilha comum em aulas de IA: passar muito tempo descrevendo possibilidades sem mostrar onde o sistema falha. Aqui cada conceito será ligado a um comando, um output ou um artefato.”

**Exemplo além do slide.** Em vez de explicar placeholders por dez minutos, crie um carrinho, observe `cart-001` e mostre o segundo passo usando esse valor. A necessidade do contexto aparece sozinha.

**Pergunte à turma.** “Qual informação só descobrimos ao executar, e não apenas ao ler o requisito?”

**Resposta que vale construir.** Dados concretos, IDs dinâmicos, respostas reais, latência e detalhes do contrato em execução.

**Transição.** “A primeira execução começa com uma regra simples: não vender o que não existe.”

<!-- deck-primary: Executar primeiro cria evidência concreta; a teoria depois explica por que ela é confiável. -->
<!-- deck-engineering: Vincular cada conceito a comando, output e artefato observável. -->
<!-- deck-caution: Demonstração sem observação real vira apenas narrativa sobre a ferramenta. -->
<!-- deck-question: O que só descobrimos quando o teste realmente executa? -->

## Slide 07 — O REQUISITO DE ESTOQUE INSUFICIENTE

**Fala sugerida.** “O requisito diz que um usuário não pode adicionar uma quantidade maior que o estoque. Ainda faltam decisões para isso virar teste: qual produto, qual estoque real, qual quantidade atravessa a fronteira, qual sequência cria o estado necessário e qual resposta demonstra a rejeição. Consultamos `sku-001` e descobrimos estoque 3. Quantidade 4 é melhor que 99 para este exemplo porque evidencia exatamente a primeira posição inválida da fronteira. Precisamos criar um carrinho, capturar seu ID e tentar adicionar o item. O 409 é defensável porque representa o conflito documentado pela API, não porque seja uma convenção escolhida pelo modelo.”

**Exemplo além do slide.** Há três testes diferentes escondidos na frase: quantidade 3 deve ser aceita, quantidade 4 deve ser rejeitada e um produto inexistente deve seguir outra regra. Misturá-los em um único caso dificulta saber qual regra falhou.

**Pergunte à turma.** “Qual é o menor teste que prova a rejeição sem testar várias regras ao mesmo tempo?”

**Resposta que vale construir.** Criar carrinho e adicionar `sku-001` com quantidade 4, esperando 200 e depois 409.

**Transição.** “Agora precisamos representar esse raciocínio em uma estrutura que humanos, LLM e executor compartilhem.”

<!-- deck-primary: Transformar requisito em fixture, fronteira, sequência de estado e resposta esperada. -->
<!-- deck-engineering: Usar sku-001 com estoque 3 e quantidade 4 para testar a primeira entrada inválida. -->
<!-- deck-caution: O 409 vem do contrato do núcleo, não de uma preferência genérica do modelo. -->
<!-- deck-question: Qual é a menor sequência HTTP que realmente prova a regra? -->

## Slide 08 — SCHEMA CANÔNICO DO TESTPLAN

**Fala sugerida.** “O schema é a língua franca da pipeline. `HttpStep` descreve uma ação observável: nome, método, path, body e status esperado. `TestPlan` acrescenta intenção, risco e oracle para que o artefato não seja apenas uma coleção de requests. Os limites também comunicam desenho: métodos pertencem a um conjunto conhecido, status precisa estar na faixa HTTP e o plano tem no máximo oito passos. Isso reduz o espaço de saída do modelo e permite rejeitar cedo resultados malformados. Mas reparem no que o schema não sabe: ele aceita um path com formato correto mesmo que a rota não exista e aceita 418 mesmo que aquele endpoint nunca documente esse status.”

**Exemplo além do slide.** `POST /produto-inventado` pode satisfazer todos os tipos do Pydantic. A estrutura está correta; a semântica está errada. Essa diferença reaparecerá em toda a semana.

**Pergunte à turma.** “Por que guardar `risk` e `oracle` se o executor só compara status?”

**Resposta que vale construir.** Porque execução e auditabilidade são necessidades diferentes; esses campos explicam por que o teste existe e como interpretar sua relevância.

**Transição.** “O primeiro consumidor dessa estrutura é o Pydantic, antes de qualquer tráfego de rede.”

<!-- deck-primary: TestPlan é o contrato comum entre intenção, geração, validação e execução. -->
<!-- deck-engineering: Restringir forma e tamanho reduz saídas inválidas antes de qualquer chamada HTTP. -->
<!-- deck-caution: Schema válido não prova que endpoint, body ou status fazem sentido. -->
<!-- deck-question: Por que intenção, risco e oracle pertencem ao plano? -->

## Slide 09 — POR QUE PYDANTIC ENTRA ANTES DO HTTP

**Fala sugerida.** “Pydantic funciona como uma alfândega entre o componente probabilístico e o software que possui capacidade de agir. Antes de enviar qualquer request, verificamos se o objeto tem os campos esperados, tipos corretos e limites mínimos. Essa ordem importa: erros de representação devem falhar sem tocar o sistema-alvo. Structured output ajuda o modelo a produzir algo próximo do schema; Pydantic continua necessário porque a resposta recebida precisa ser validada no nosso processo, sob nossa versão do contrato. Uma camada orienta a geração, a outra aplica rejeição determinística.”

**Exemplo além do slide.** Se o modelo escrever `"expect_status": "conflict"`, o texto pode ser compreensível para uma pessoa, mas não é executável. Se enviar `DELETE`, o schema até pode aceitar porque o tipo lista esse método; a autorização será responsabilidade da próxima camada.

**Pergunte à turma.** “Por que não deixar o executor tentar e tratar qualquer erro depois?”

**Resposta que vale construir.** Porque falhar cedo reduz efeitos colaterais, simplifica diagnóstico e impede que dados incompletos alcancem uma capacidade real.

**Transição.** “Forma correta ainda não significa ação autorizada; agora entra a policy.”

<!-- deck-primary: Pydantic é a fronteira de contrato antes que uma saída probabilística alcance o HTTP. -->
<!-- deck-engineering: Structured output orienta a geração; validação local rejeita violações de forma. -->
<!-- deck-caution: Validação estrutural não substitui autorização nem validação semântica. -->
<!-- deck-question: Por que falhar antes do HTTP é melhor que tratar o erro depois? -->

## Slide 10 — POLÍTICA DE MÉTODO E PATH

**Fala sugerida.** “A policy responde a uma pergunta diferente do schema: mesmo sendo bem formado, este plano tem permissão para agir? O núcleo restringe hosts, métodos e prefixos de path. Essa decisão deve existir em código porque prompt é instrução, não barreira de segurança. Um modelo pode desobedecer, sofrer prompt injection ou simplesmente interpretar uma regra de forma diferente. A allowlist reduz a capacidade efetiva: não importa quão convincente seja o plano, um método ou destino fora do escopo não chega ao HTTP. Observem também que segurança aqui é sobre capacidade, não sobre intenção declarada. Um plano chamado ‘teste inofensivo’ recebe exatamente as mesmas restrições.”

**Exemplo além do slide.** Escrever “nunca use DELETE” no system prompt é equivalente a colocar uma placa de “não entre”. A policy é a porta trancada. As duas podem coexistir, mas cumprem funções diferentes.

**Pergunte à turma.** “Por que o schema admite DELETE se a policy bloqueia?”

**Resposta que vale construir.** O schema descreve a linguagem possível; policies diferentes podem conceder subconjuntos distintos conforme ambiente e risco.

**Transição.** “Com um plano válido e autorizado, finalmente podemos executar contra a aplicação real.”

<!-- deck-primary: Policy decide se um plano bem formado possui autorização para alcançar o sistema. -->
<!-- deck-engineering: Impor host, método e path por allowlist em código, independentemente do prompt. -->
<!-- deck-caution: Instrução ao modelo não é controle de acesso nem limite de capacidade. -->
<!-- deck-question: Por que o prompt não pode ser a única barreira contra DELETE? -->

## Slide 11 — EXECUTOR HTTP REAL

**Fala sugerida.** “O executor é propositalmente pouco inteligente. Ele recebe um plano já validado, resolve placeholders, faz requests HTTP reais e registra o que ocorreu. Quando `POST /cart` devolve um ID, esse valor entra no contexto e pode preencher `{cart_id}` nos passos seguintes. Isso evita hardcode e permite testar fluxos stateful. O timeout limita quanto uma chamada pode prender a execução. Para cada step, o PASS é uma comparação explícita entre status recebido e status esperado. Não pedimos ao modelo que interprete se 409 ‘parece adequado’ durante a execução. Quanto menor a ambiguidade no executor, mais fácil auditar o resultado.”

**Exemplo além do slide.** Se a API gerar `cart-017`, o plano continua válido porque depende do significado `cart_id`, não de um valor observado em outra execução. Isso diferencia uma sequência reproduzível de um script acidentalmente acoplado ao estado anterior.

**Pergunte à turma.** “O que aconteceria se o primeiro passo falhasse e não produzisse `cart_id`?”

**Resposta que vale construir.** O placeholder não poderia ser resolvido; um executor mais completo poderia interromper explicitamente e registrar dependência quebrada.

**Transição.** “Vamos olhar o artefato que prova o que realmente aconteceu.”

<!-- deck-primary: O executor resolve estado dinâmico, chama HTTP real e compara observado com esperado. -->
<!-- deck-engineering: Manter execução simples, limitada por timeout e separada da interpretação do LLM. -->
<!-- deck-caution: Placeholders só são válidos depois que um passo anterior produz o contexto necessário. -->
<!-- deck-question: Onde exatamente cada step recebe PASS ou FAIL? -->

## Slide 12 — DEMONSTRAÇÃO: 200 DEPOIS 409

**Fala sugerida.** “Aqui está a evidência, não uma descrição da evidência. O primeiro step criou um carrinho e recebeu 200. O segundo tentou adicionar quantidade inválida e recebeu 409, exatamente o esperado. `passed: true` não quer dizer que a operação de negócio foi bem-sucedida; quer dizer que o sistema se comportou conforme a regra. Esse é um ponto importante em testes negativos: receber um erro pode ser o resultado correto. Notem também que o ID do carrinho é incidental. Ele pode mudar em cada execução; o que importa é a relação entre os passos e os oracles.”

**Exemplo além do slide.** Se o segundo request retornasse 200, o HTTP estaria tecnicamente ‘bem-sucedido’, mas o teste deveria falhar porque a aplicação aceitou overselling. Ferramentas que tratam qualquer 2xx como sucesso não entendem o requisito.

**Pergunte à turma.** “Por que 409 produz um step verde?”

**Resposta que vale construir.** Porque o oracle esperava rejeição; sucesso do teste não é o mesmo que sucesso da operação testada.

**Transição.** “Agora que existe uma execução confiável, podemos escolher quais partes vale delegar à IA.”

<!-- deck-primary: O report prova 200 seguido de 409 e separa sucesso do teste de sucesso da operação. -->
<!-- deck-engineering: Persistir status observado, esperado, body e resultado para auditoria e release gates. -->
<!-- deck-caution: Um 2xx pode representar falha do requisito; um 4xx esperado pode representar PASS. -->
<!-- deck-question: Por que um step com HTTP 409 aparece como passed=true? -->

## Slide 13 — O QUE A IA PODE GERAR

**Fala sugerida.** “A melhor utilização da IA aqui é reduzir trabalho de tradução e exploração dentro de um espaço controlado. Ela pode decompor um requisito em passos, sugerir nomes claros, selecionar endpoints presentes no contrato, preencher valores a partir do contexto e explicitar intenção e risco. São tarefas com múltiplas formulações aceitáveis e alto custo manual de composição. Mas a saída deve chegar como `TestPlan`, não como um bloco de prosa ou código arbitrário. Quanto mais estreito o contrato, mais barato verificar se a proposta faz sentido.”

**Exemplo além do slide.** Para ‘pagamento com valor divergente’, o modelo pode propor criar carrinho, adicionar item, gerar pedido e enviar um amount diferente. Ainda assim, IDs precisam vir do runtime e o status precisa ser conferido no OpenAPI.

**Pergunte à turma.** “Qual campo vocês aceitariam com maior liberdade: `name`, `path` ou `expect_status`?”

**Resposta que vale construir.** `name` tolera variação estilística. `path` e `expect_status` precisam estar rigidamente ancorados no contrato.

**Transição.** “Essa assimetria mostra também o que não deve ser entregue ao modelo.”

<!-- deck-primary: IA é útil para decompor requisito e propor um plano dentro de contexto e contrato conhecidos. -->
<!-- deck-engineering: Receber a proposta como TestPlan estruturado, não como código ou texto livre. -->
<!-- deck-caution: Campos que controlam ação e oracle exigem validação mais forte que campos descritivos. -->
<!-- deck-question: Qual campo do TestPlan pode tolerar mais liberdade do modelo? -->

## Slide 14 — O QUE A IA NÃO DEVE DECIDIR

**Fala sugerida.** “O modelo não deve ser a única fonte de autorização, verdade esperada ou decisão final. Ele não escolhe livremente o host, não amplia métodos permitidos, não declara que um status não documentado é correto e não transforma sua própria confiança em aprovação de release. Existe um conflito de papéis quando o mesmo componente cria o teste, define o resultado esperado e julga a própria execução. Por isso, cada etapa da sequência tem uma responsabilidade: requisito fornece intenção; schema limita representação; policy limita capacidade; executor mede; oracle julga; report preserva evidência.”

**Exemplo além do slide.** Seria como pedir a um candidato que escrevesse a prova, escolhesse o gabarito e atribuísse a própria nota. Mesmo sem má-fé, não existe independência suficiente para confiar no resultado.

**Pergunte à turma.** “Qual dessas decisões é mais perigosa delegar: escolher um nome, escolher um endpoint ou alterar o oracle?”

**Resposta que vale construir.** Alterar o oracle pode tornar qualquer comportamento aceitável; endpoint amplia capacidade; ambos exigem controles determinísticos.

**Transição.** “Structured output ajuda a controlar a representação, mas precisamos entender exatamente o que ele garante.”

<!-- deck-primary: IA não deve controlar sozinha autorização, oracle ou decisão de release. -->
<!-- deck-engineering: Separar quem propõe o teste de quem limita a ação, mede e julga o resultado. -->
<!-- deck-caution: O mesmo modelo gerar, corrigir e aprovar seu teste cria conflito de papéis. -->
<!-- deck-question: O que acontece se o modelo puder alterar o próprio oracle? -->

## Slide 15 — OLLAMA STRUCTURED OUTPUT

**Fala sugerida.** “Aqui enviamos ao Ollama o JSON Schema do `TestPlan` e pedimos uma resposta compatível. Isso reduz problemas de parsing e evita a velha estratégia de procurar JSON dentro de texto cercado por explicações. Temperatura zero reduz variação, mas não transforma o modelo em função determinística. Depois da resposta, Pydantic valida novamente no nosso processo. Em seguida, uma verificação semântica consulta o OpenAPI. Notem a sequência de defesas: orientar formato, validar formato, verificar significado. Nenhuma camada sozinha resolve as três coisas.”

**Exemplo além do slide.** Um plano pode sair com todas as chaves corretas e ainda esperar 404 em uma operação cujo contrato só documenta 200 e 409. O parser ficará satisfeito; a semântica não.

**Pergunte à turma.** “Structured output elimina alucinação?”

**Resposta que vale construir.** Não. Ele restringe a forma da resposta; valores semanticamente incorretos continuam possíveis.

**Transição.** “Para melhorar o significado, precisamos fornecer evidência do mundo onde o plano será executado.”

<!-- deck-primary: Structured output restringe a forma; Pydantic e OpenAPI ainda precisam validar a resposta. -->
<!-- deck-engineering: Combinar schema, temperatura baixa e validação local antes de aceitar o plano. -->
<!-- deck-caution: JSON perfeito pode conter endpoint, body, fixture ou status semanticamente errados. -->
<!-- deck-question: Structured output elimina alucinação ou apenas restringe formato? -->

## Slide 16 — PROMPT COM OPENAPI E PRODUTOS REAIS

**Fala sugerida.** “Um requisito sozinho não contém detalhes suficientes para gerar um teste executável. O prompt recebe quatro fontes: a intenção de negócio, produtos reais do runtime, o contrato OpenAPI e o JSON Schema da saída. Cada uma reduz um tipo de incerteza. O requisito diz o que importa; os produtos fornecem fixtures existentes; OpenAPI define operações e respostas; o schema define a estrutura. Isso é grounding operacional: não estamos pedindo que o modelo recorde como a nossa API talvez funcione, estamos entregando evidência específica desta execução.”

**Exemplo além do slide.** Sem o runtime context, o modelo poderia escolher `sku-999` ou quantidade 10 acreditando testar estoque. Com `sku-001 stock=3`, quantidade 4 passa a ter justificativa verificável.

**Pergunte à turma.** “Se tivéssemos de remover uma dessas fontes, qual remoção produziria o erro mais perigoso?”

**Resposta que vale construir.** Depende do risco, mas remover OpenAPI ou requisito ameaça diretamente ação/oracle; remover fixtures aumenta planos inexequíveis.

**Transição.** “Mesmo com bom contexto, o modelo pode errar; por isso a correção precisa ser limitada e orientada por fatos.”

<!-- deck-primary: Requisito, fixtures reais, OpenAPI e JSON Schema reduzem incertezas diferentes. -->
<!-- deck-engineering: Fazer grounding com dados do runtime em vez de depender da memória do modelo. -->
<!-- deck-caution: Contexto grande ou truncado ainda pode omitir relações importantes; grounding não é garantia. -->
<!-- deck-question: Qual fonte impede o modelo de inventar produto, rota ou status? -->

## Slide 17 — CORREÇÃO LIMITADA E VALIDAÇÃO SEMÂNTICA

**Fala sugerida.** “A validação semântica pergunta se cada path e método existe, se o status esperado está documentado, se um body obrigatório foi fornecido e se placeholders aparecem somente depois de serem produzidos. Quando encontra um problema, o sistema devolve ao modelo uma lista concreta e permite nova tentativa. O limite de três tentativas é tão importante quanto o feedback. Sem limite, ‘self-healing’ pode virar loop caro, esconder um contrato incompatível ou fabricar sucessivas justificativas. Correção controlada significa corrigir a representação a partir de uma violação verificável — nunca mudar o produto ou o oracle só para o teste ficar verde.”

**Exemplo além do slide.** Se `/cart/{cart_id}/items` exige body e o plano envia `null`, o feedback pode dizer exatamente “requestBody obrigatório ausente”. “Tente novamente melhor” não cria uma condição de parada auditável.

**Pergunte à turma.** “Depois de três respostas inválidas, qual é o comportamento correto?”

**Resposta que vale construir.** Falhar explicitamente, preservar os erros e pedir intervenção; não relaxar validação automaticamente.

**Transição.** “A mesma pipeline pode ser vista em código ou orquestrada visualmente; agora entra o n8n.”

<!-- deck-primary: Validação semântica detecta rota, status, body e placeholders incorretos e orienta correção limitada. -->
<!-- deck-engineering: Usar feedback verificável e no máximo três tentativas antes de falhar explicitamente. -->
<!-- deck-caution: Self-healing não deve alterar requisito, produto ou oracle para fabricar um PASS. -->
<!-- deck-question: Quando o sistema deve parar de pedir correção ao modelo? -->

## Slide 18 — LOW-CODE NO N8N

**Fala sugerida.** “No n8n, a arquitetura fica visível como fluxo de dados. O trigger inicia uma execução controlada. `Requirement` fornece intenção. `Fetch OpenAPI` e `Fetch Products` buscam contexto verificável. A chain transforma esse contexto em `TestPlan`; o parser garante forma; o node JavaScript verifica invariantes do exercício; `Execute Plan` envia o plano para a fronteira Python; `Report` expõe a evidência final. O valor pedagógico do n8n é permitir abrir cada etapa e observar o que entrou e saiu. Ele torna a orquestração inspecionável, mas não remove nenhuma obrigação de engenharia.”

**Exemplo além do slide.** Se o workflow fica verde até `Generate TestPlan` e falha em `Validation`, sabemos que conectividade e geração funcionaram; o problema está no significado do plano. O canvas ajuda a localizar a fronteira que rejeitou o dado.

**Pergunte à turma.** “Qual node deveria ter menos liberdade de todos?”

**Resposta que vale construir.** `Execute Plan`, porque alcança capacidade real; por isso ele chama uma API controlada em vez de executar URLs arbitrárias.

**Transição.** “Reparem que usamos uma chain, não um agente. Essa escolha é intencional.”

<!-- deck-primary: n8n torna visível a mesma sequência de contexto, geração, validação, execução e evidência. -->
<!-- deck-engineering: Executar o plano por uma API Python controlada, preservando policy e executor únicos. -->
<!-- deck-caution: Canvas visual facilita composição, mas não concede segurança nem semântica automaticamente. -->
<!-- deck-question: Qual node possui a capacidade mais sensível do workflow? -->

## Slide 19 — BASIC LLM CHAIN, NÃO AI AGENT

**Fala sugerida.** “Esta tarefa é uma transformação de entrada para saída: temos contexto conhecido e queremos um `TestPlan`. Não precisamos que o modelo decida iterativamente qual ferramenta chamar. Uma Basic LLM Chain é menor, mais previsível e mais fácil de depurar. Chamar tudo de agente adiciona loop, estado e seleção de tools sem necessidade. Agentes fazem sentido quando a próxima ação depende da observação anterior e não pode ser definida antecipadamente — como na investigação SRE do Dia 3. A escolha da abstração deve seguir a estrutura do problema, não a novidade da ferramenta.”

**Exemplo além do slide.** Gerar um resumo a partir de um documento é transformação. Investigar latência escolhendo entre métricas, traces e mudanças é decisão iterativa. Ambos usam modelo, mas pedem arquiteturas diferentes.

**Pergunte à turma.** “Que mudança no problema justificaria trocar esta chain por um agente?”

**Resposta que vale construir.** Quando o modelo precisar escolher e repetir ferramentas com base em evidências desconhecidas antecipadamente.

**Transição.** “Com essa escolha clara, vamos percorrer o workflow completo de ponta a ponta.”

<!-- deck-primary: A tarefa é mapear contexto para estrutura; uma chain é suficiente e mais previsível. -->
<!-- deck-engineering: Reservar agent loop para problemas com escolha iterativa de ferramentas. -->
<!-- deck-caution: Usar agente sem necessidade aumenta estados, falhas e custo de depuração. -->
<!-- deck-question: O que precisaria mudar para uma chain deixar de ser suficiente? -->

## Slide 20 — WORKFLOW N8N VALIDADO

**Fala sugerida.** “Agora acompanhem o dado, não apenas as setas. O requisito começa como texto. OpenAPI e produto entram como evidência externa. A chain produz um objeto dentro de `output`. O parser confirma a forma. `Validation` retira o wrapper e confere exatamente dois passos, paths, statuses, produto e quantidade. Só então o plano alcança `/qa/execute-plan`, que reaplica schema, policy e executor no backend. Essa duplicação aparente de validação é defesa em profundidade: o node protege o exercício no workflow; a API protege sua própria capacidade independentemente de quem a chama.”

**Exemplo além do slide.** Se alguém chamar `/qa/execute-plan` sem passar pelo n8n, a policy Python continua ativa. Segurança que existe apenas no canvas desapareceria quando outro cliente surgisse.

**Pergunte à turma.** “Por que validar no JavaScript e novamente no Python?”

**Resposta que vale construir.** Porque cada fronteira deve proteger seus invariantes; nenhum cliente deve ser implicitamente confiável.

**Transição.** “Quando algo falha, essa separação também nos diz exatamente onde olhar.”

<!-- deck-primary: O workflow passa de intenção e contexto até execução, preservando validações em cada fronteira. -->
<!-- deck-engineering: Revalidar na API para que a segurança não dependa exclusivamente do cliente n8n. -->
<!-- deck-caution: Node verde indica execução técnica, não prova que o dado produzido é semanticamente correto. -->
<!-- deck-question: Por que a API valida um plano que o n8n já validou? -->

## Slide 21 — ONDE OBSERVAR CADA NODE

**Fala sugerida.** “Depurar low-code exige ler execution data. Um canvas todo verde pode esconder um plano errado se ninguém inspecionar outputs; um node vermelho só informa onde o erro apareceu, não necessariamente onde nasceu. Comecem pelo último dado correto. Em `Requirement`, confirmem intenção. Em `Fetch Products`, estoque. Em `Generate TestPlan`, abram `output.steps`. Em `Validation`, confirmem que o wrapper desapareceu. Em `Execute Plan`, comparem status observado e esperado. Esse hábito transforma n8n de caixa-preta visual em uma sequência auditável de contratos.”

**Exemplo além do slide.** Um 422 no `Execute Plan` pode nascer porque o parser colocou o plano dentro de `{"output": ...}` e o body enviou o wrapper inteiro. A conexão funcionou; o shape do payload não.

**Pergunte à turma.** “Se `Execute Plan` retorna 422, qual é a primeira comparação útil?”

**Resposta que vale construir.** Comparar o body enviado com o schema esperado pela API, começando pelo output de `Validation`.

**Transição.** “Essa disciplina é ainda mais importante quando a ferramenta promete corrigir o fluxo sozinha.”

<!-- deck-primary: Debug de low-code acontece pela inspeção de dados entre nodes, não apenas pelas cores do canvas. -->
<!-- deck-engineering: Comparar input e output em cada fronteira e localizar o último contrato válido. -->
<!-- deck-caution: O node onde o erro aparece pode não ser o node que produziu o dado incorreto. -->
<!-- deck-question: Diante de um HTTP 422, qual payload você inspeciona primeiro? -->

## Slide 22 — SELF-HEALING: ÚTIL OU PERIGOSO?

**Fala sugerida.** “Self-healing é um rótulo amplo. Corrigir um seletor depois de verificar que o elemento apenas mudou de atributo é diferente de atualizar automaticamente um oracle ou uma baseline. No primeiro caso, podemos estar reparando a representação do teste. No segundo, podemos apagar a evidência de uma regressão. A pergunta correta não é ‘o sistema consegue se corrigir?’, mas ‘o que ele tem autoridade para mudar, com base em qual evidência e com qual possibilidade de revisão?’. Reparos seguros tendem a ser limitados, reversíveis, registrados e incapazes de redefinir sucesso.”

**Exemplo além do slide.** Se o botão mudou de `id=pay` para `data-testid=pay`, uma estratégia pode sugerir novo seletor. Se o botão desapareceu, criar uma baseline sem ele seria normalizar o defeito.

**Pergunte à turma.** “Que artefato o sistema nunca deveria reescrever silenciosamente?”

**Resposta que vale construir.** Oracle, baseline aprovada e políticas que definem sucesso ou autoridade.

**Transição.** “Vamos organizar os erros do dia pelos controles que os contêm.”

<!-- deck-primary: Self-healing seguro corrige representação limitada; não redefine silenciosamente o que significa sucesso. -->
<!-- deck-engineering: Exigir evidência verificável, limite, reversibilidade, registro e revisão para reparos. -->
<!-- deck-caution: Atualizar oracle ou baseline automaticamente pode apagar uma regressão legítima. -->
<!-- deck-question: Qual artefato nunca deve ser reescrito silenciosamente? -->

## Slide 23 — FAILURE MODES DO DIA 1

**Fala sugerida.** “Cada failure mode pede um controle específico. JSON inválido é problema de forma: schema e Pydantic. Endpoint inventado é problema de semântica e capacidade: OpenAPI e policy. Oracle fraco é problema de engenharia de teste: requisito, contrato e revisão. Self-healing excessivo é problema de governança: limites e aprovação. Nenhuma técnica resolve tudo. Isso é importante porque equipes frequentemente adicionam um prompt maior para corrigir falhas que pertencem à arquitetura. Se o risco é autorização, mais texto no prompt não substitui allowlist.”

**Exemplo além do slide.** Um modelo gerar `/delete-cart` não deve ser resolvido apenas dizendo “essa rota não existe”. Mesmo que ela passe a existir no futuro, DELETE ainda pode continuar fora da capacidade autorizada para o agente.

**Pergunte à turma.** “Qual controle detecta um status 418 bem formado, mas não documentado?”

**Resposta que vale construir.** Validação semântica contra OpenAPI; Pydantic sozinho não detecta.

**Transição.** “Com esses controles em mente, podemos comparar arquiteturas sem procurar um vencedor universal.”

<!-- deck-primary: Falhas de forma, semântica, autorização e oracle exigem controles diferentes. -->
<!-- deck-engineering: Aplicar schema, OpenAPI, policy e revisão exatamente na fronteira correspondente. -->
<!-- deck-caution: Aumentar o prompt não corrige uma ausência de controle arquitetural. -->
<!-- deck-question: Qual camada rejeita um status válido como número, mas inválido para a operação? -->

## Slide 24 — COMPARAÇÃO: CÓDIGO, LOW-CODE E AGENTE

**Fala sugerida.** “Código puro oferece controle fino, testes tradicionais e versionamento direto, mas exige mais plumbing. Low-code acelera composição e torna o fluxo acessível visualmente, mas pode esconder detalhes em configuração e criar dependência da plataforma. Agentes lidam melhor com caminhos não conhecidos antecipadamente, mas acrescentam variabilidade, custo e necessidade de observabilidade da decisão. Não existe ranking universal. A arquitetura correta depende da estabilidade do processo, do risco da ação, da necessidade de auditoria e da variedade de caminhos possíveis. O ReleaseGuard é híbrido porque cada parte tem uma forma de incerteza diferente.”

**Exemplo além do slide.** Para mil regressões fixas de API, código parametrizado pode ser melhor que mil canvases. Para integrar um fluxo didático e inspecionar etapas, n8n ajuda. Para investigar um sintoma aberto, um loop com tools pode fazer sentido.

**Pergunte à turma.** “Qual abordagem usariam para uma suíte fixa executada a cada commit?”

**Resposta que vale construir.** Provavelmente código/CI como base, talvez low-code na orquestração; agente só se houver incerteza real que justifique o custo.

**Transição.** “Agora os grupos aplicarão essas escolhas a riscos diferentes.”

<!-- deck-primary: Código, low-code e agentes possuem trade-offs diferentes; arquitetura híbrida é frequentemente mais realista. -->
<!-- deck-engineering: Escolher pela estabilidade do fluxo, risco, auditabilidade e necessidade de decisão iterativa. -->
<!-- deck-caution: Não adotar agentes apenas por novidade nem low-code apenas por facilidade inicial. -->
<!-- deck-question: O que vocês escolheriam para uma suíte fixa executada em todo commit? -->

## Slide 25 — EXERCÍCIO MENTORADO DIA 1

**Fala sugerida.** “Cada grupo recebe um risco diferente, mas todos serão avaliados pela mesma cadeia de evidência. Primeiro reescrevam o requisito de forma testável. Depois descubram fixture, estado, ações e oracle. Criem o plano dentro de `student_work`, executem HTTP real e preservem o report. Não alterem o núcleo para fazer o caso passar: se o contrato existente torna o plano difícil, essa dificuldade faz parte do exercício. Casos stateful exigirão placeholders; boundary exige comparar os dois lados da fronteira; policy exige reconhecer que ser bloqueado pode ser o resultado correto.”

**Exemplo além do slide.** No grupo de host/método proibido, receber `ValueError` ou bloqueio da policy não é falha do trabalho. É a evidência de que a fronteira de segurança funcionou.

**Pergunte à turma.** “Antes de escrever código, qual frase cada grupo precisa conseguir completar?”

**Resposta que vale construir.** “Consideraremos o teste aprovado se observarmos ___, porque o requisito/contrato diz ___.”

**Transição.** “A rubrica foi desenhada para premiar justamente essa justificativa, não quantidade de código.”

<!-- deck-primary: Oito grupos transformam riscos distintos em TestPlan, HTTP real, oracle e report auditável. -->
<!-- deck-engineering: Trabalhar apenas em student_work e consumir o núcleo como contrato congelado. -->
<!-- deck-caution: Não adaptar app, schema, policy ou executor para fabricar o resultado desejado. -->
<!-- deck-question: Qual frase de oracle deve existir antes de começar a implementação? -->

## Slide 26 — CRITÉRIOS DE AVALIAÇÃO

**Fala sugerida.** “A maior parcela da nota está no oracle porque um teste tecnicamente executável pode ser conceitualmente inútil. Plano mínimo significa cobrir a regra sem misturar cenários que dificultem diagnóstico. Execução HTTP real impede que a equipe apresente apenas uma hipótese. Estado e placeholders mostram que o caso sobrevive a IDs dinâmicos. Segurança verifica se o grupo respeitou a fronteira, inclusive quando o resultado correto é um bloqueio. A apresentação vale menos pontos, mas precisa tornar o raciocínio rastreável. ‘Funcionou na minha máquina’ não responde de onde veio o esperado nem se o teste poderia passar por acidente.”

**Exemplo além do slide.** Um grupo pode ter `passed: true` e perder pontos se esperou 409 apenas porque viu uma execução anterior, sem ligar o valor ao contrato ou regra.

**Pergunte à turma.** “Que evidência mostra que um teste não passou por acidente?”

**Resposta que vale construir.** Plano mínimo, oracle fundamentado, output observado e explicação de falsos positivos possíveis.

**Transição.** “Antes de começar, vamos resumir a única frase que precisa sobreviver ao Dia 1.”

<!-- deck-primary: A rubrica privilegia oracle fundamentado, plano mínimo, HTTP real e estado correto. -->
<!-- deck-engineering: Avaliar rastreabilidade da decisão, não volume de código nem aparência do workflow. -->
<!-- deck-caution: passed=true sem justificativa pode representar um falso positivo bem formatado. -->
<!-- deck-question: Como provar que o teste não passou por acidente? -->

## Slide 27 — FECHAMENTO DIA 1

**Fala sugerida.** “A frase de fechamento é: o modelo propõe; schema e validação controlam representação; policy controla autoridade; HTTP produz observação; oracle julga; report preserva evidência. Se a turma lembrar apenas ‘usamos Ollama no n8n’, perdeu o ponto principal. As ferramentas podem mudar; essa separação continua válida. Guardem também o `functional_report.json`: ele não termina sua utilidade hoje. No Dia 3, será uma das entradas da decisão integrada de release. Isso mostra como uma evidência local pode ganhar valor quando possui estrutura e origem conhecidas.”

**Exemplo além do slide.** O 409 foi um oracle simples porque a API fornece um status discreto. Dizer que uma tela “parece correta” não tem uma resposta tão direta; pequenas diferenças podem ser ruído ou impacto real.

**Pergunte à turma.** “Como escreveriam um único `assert` para garantir que uma página parece correta?”

**Resposta que vale construir.** Não existe assert universal; precisaremos controlar captura, medir diferença, localizar região e aplicar política contextual.

**Transição.** “É exatamente essa ambiguidade que abre o Dia 2.”

<!-- deck-primary: LLM propõe; contratos limitam; HTTP observa; oracle decide; report preserva evidência. -->
<!-- deck-engineering: Reutilizar functional_report.json como entrada rastreável da decisão integrada. -->
<!-- deck-caution: O oracle discreto de uma API não se transfere diretamente para aparência visual. -->
<!-- deck-question: Como transformar “a página parece correta” em evidência verificável? -->

---

# Dia 2 — Regressão visual com Visual AI

## Slide 28 — DIA 2: REGRESSÃO VISUAL COM VISUAL AI

**Fala sugerida.** “Ontem o sistema nos deu respostas discretas: 200 ou 409. Hoje o objeto observado é uma imagem, e diferença não é sinônimo de defeito. Vamos renderizar a interface em um browser real, guardar uma referência, provocar uma mudança controlada, medir os pixels, localizar a região alterada e pedir a um modelo multimodal que descreva o que vê. Mesmo assim, o VLM não decide sozinho a release. O trabalho de hoje é construir um oracle visual em camadas: captura reproduzível, métricas, evidência espacial, interpretação e política.”

**Exemplo além do slide.** Dois screenshots podem diferir por antialiasing e continuar funcionalmente equivalentes. Duas imagens quase idênticas podem esconder o desaparecimento de um pequeno botão de pagamento com enorme impacto de negócio.

**Pergunte à turma.** “Qual das duas situações é pior: muitos pixels diferentes sem impacto ou poucos pixels diferentes numa ação crítica?”

**Resposta que vale construir.** O impacto depende da região e da função, não apenas da quantidade global de pixels.

**Transição.** “Começamos, portanto, abandonando a ideia de que toda diferença visual é bug.”

<!-- deck-primary: Browser real produz baseline, current e diff; métricas e VLM ajudam a interpretar a mudança. -->
<!-- deck-engineering: Construir o oracle visual em camadas, terminando em política explícita. -->
<!-- deck-caution: Nem diferença significa bug, nem similaridade alta significa ausência de impacto. -->
<!-- deck-question: Poucos pixels podem representar uma regressão crítica? -->

## Slide 29 — O PROBLEMA: IMAGEM DIFERENTE ≠ BUG

**Fala sugerida.** “Uma imagem muda por razões legítimas e ilegítimas. Timestamp, cursor, fonte ainda carregando, rasterização e conteúdo personalizado podem alterar pixels sem regressão. Por outro lado, CTA ausente, texto cortado ou contraste quebrado podem ocupar uma parcela pequena da tela e afetar diretamente o usuário. Por isso temos dois erros possíveis. False positive é bloquear uma mudança aceitável; false negative é aceitar uma regressão relevante. O threshold que reduz um costuma aumentar o outro. A escolha precisa refletir o custo de negócio e a região observada.”

**Exemplo além do slide.** Um banner promocional dinâmico pode alterar 20% da imagem e ser esperado. Um checkbox de consentimento invisível pode alterar menos de 0,1% e impedir o fluxo inteiro.

**Pergunte à turma.** “Um pixel-change ratio de 1% deveria sempre bloquear?”

**Resposta que vale construir.** Não. Precisamos saber onde mudou, o que existe naquela região e qual política se aplica.

**Transição.** “Agora podemos definir regressão visual sem reduzi-la a pixel-perfect.”

<!-- deck-primary: Imagem diferente pode ser ruído aceitável; mudança pequena pode ser regressão crítica. -->
<!-- deck-engineering: Tratar o oracle visual como política contextual apoiada por múltiplas evidências. -->
<!-- deck-caution: Threshold global único troca false positives por false negatives sem considerar impacto. -->
<!-- deck-question: Uma mudança de 1% dos pixels deve sempre bloquear? -->

## Slide 30 — DEFINIÇÃO CANÔNICA: VISUAL REGRESSION

**Fala sugerida.** “Visual regression testing compara o estado renderizado atual com uma referência aprovada para detectar mudanças inesperadas relevantes. Há três palavras importantes. ‘Renderizado’ significa observar o que o browser produziu, não apenas o HTML. ‘Referência aprovada’ significa que a baseline tem história e responsabilidade, não é qualquer screenshot antigo. ‘Relevante’ significa que a decisão depende de contexto, região e risco. O objetivo não é congelar todos os pixels para sempre; é tornar mudanças visuais detectáveis, explicáveis e governáveis.”

**Exemplo além do slide.** Uma atualização consciente de identidade visual deve mudar a imagem e, após revisão, gerar nova baseline. O sistema não falhou ao detectar a diferença; ele cumpriu seu papel de pedir que alguém reconheça a mudança.

**Pergunte à turma.** “Quem deveria aprovar uma nova baseline?”

**Resposta que vale construir.** Uma pessoa ou processo com contexto de produto/design e evidência da mudança intencional, com rastreabilidade.

**Transição.** “Para falar dessa governança, precisamos nomear os três artefatos básicos.”

<!-- deck-primary: Visual regression compara renderização atual com referência aprovada para detectar mudança relevante. -->
<!-- deck-engineering: Versionar baseline com contexto de ambiente e processo explícito de aprovação. -->
<!-- deck-caution: Pixel-perfect não é objetivo universal; referência aprovada também pode precisar mudar. -->
<!-- deck-question: Quem tem autoridade para atualizar uma baseline? -->

## Slide 31 — DEFINIÇÃO: BASELINE, CURRENT E DIFF

**Fala sugerida.** “Baseline é o estado visual aprovado sob condições conhecidas. Current é a captura produzida pela execução que estamos avaliando. Diff é a representação das diferenças entre os dois. Nenhum deles sozinho conta a história completa. A baseline sem contexto pode estar obsoleta. O current sem ambiente controlado pode carregar ruído. O diff mostra onde os pixels divergem, mas não explica automaticamente o significado. Tratem os três como evidências relacionadas: referência, observação e contraste.”

**Exemplo além do slide.** Se a baseline foi capturada em viewport 1280×800 e o current em 1024×768, o diff pode destacar a página inteira. Isso não prova regressão do produto; prova que a comparação foi mal controlada.

**Pergunte à turma.** “A baseline é a verdade?”

**Resposta que vale construir.** É uma referência aprovada e revisável, não uma verdade eterna. Ela também pode conter defeitos.

**Transição.** “Vamos ver qual parte da interface real será usada como nosso objeto visual.”

<!-- deck-primary: Baseline é referência aprovada, current é observação e diff evidencia a divergência. -->
<!-- deck-engineering: Guardar os três artefatos junto com condições de captura e versão. -->
<!-- deck-caution: Baseline pode envelhecer ou conter defeito; current só é comparável sob ambiente controlado. -->
<!-- deck-question: Baseline é verdade permanente ou referência governada? -->

## Slide 32 — UI REAL DO RELEASEGUARD

**Fala sugerida.** “A página de checkout é uma fixture visual real da aplicação, renderizada pelo FastAPI com template Jinja. O botão ‘Finalizar compra’ não executa o fluxo funcional completo; ele existe aqui como elemento visual crítico e controlável. Isso precisa ser dito claramente para não confundir a superfície do Dia 1 com a do Dia 2. Hoje não estamos validando pagamento ao clicar no botão. Estamos validando se a página renderizada mudou de forma mensurável quando um cenário altera sua posição.”

**Exemplo além do slide.** O link usa `href="#pay"`: clicar apenas muda o fragmento da URL. A funcionalidade de checkout real continua nos endpoints `/checkout` e `/payments`, exercitados via API.

**Pergunte à turma.** “Por que usar uma página simples em vez de um mock de imagem criado no Pillow?”

**Resposta que vale construir.** Porque queremos capturar HTML, CSS, template e browser reais, preservando os tipos de variação que surgem numa UI.

**Transição.** “Para observar essa UI de forma repetível, transformamos Playwright em nossa câmera.”

<!-- deck-primary: A captura vem da página Jinja real; o CTA é fixture visual, não o executor do checkout funcional. -->
<!-- deck-engineering: Separar claramente a superfície visual da API funcional testada no Dia 1. -->
<!-- deck-caution: Clicar em #pay não realiza pagamento; a página foi desenhada para regressão visual. -->
<!-- deck-question: Por que capturar browser real em vez de fabricar duas imagens? -->

## Slide 33 — PLAYWRIGHT COMO CÂMERA DETERMINÍSTICA

**Fala sugerida.** “Playwright não é apenas ferramenta de automação de clique. Aqui ele funciona como câmera controlada. Fixamos browser, viewport, device scale e momento da captura. Esperamos `networkidle` para reduzir o risco de fotografar a página durante carregamento. Quanto mais variáveis mantemos constantes, mais provável que uma diferença venha do produto. Ainda assim, determinismo absoluto é difícil: fontes, GPU, sistema operacional e versões do browser podem alterar rasterização. Por isso o ambiente precisa ser registrado junto com o artefato.”

**Exemplo além do slide.** O núcleo usa o Chromium gerenciado pelo Playwright, em vez de assumir `/usr/bin/chromium`. Essa escolha corrigiu uma falha concreta de portabilidade no macOS.

**Pergunte à turma.** “Que variável vocês fixariam primeiro se screenshots variassem entre CI e notebook?”

**Resposta que vale construir.** Browser/versão e viewport; depois fontes, scale, locale, timezone, animações e sistema de renderização.

**Transição.** “Com a câmera configurada, registramos primeiro o estado que consideramos saudável.”

<!-- deck-primary: Playwright controla browser, viewport, escala e timing para tornar screenshots comparáveis. -->
<!-- deck-engineering: Usar Chromium gerenciado e registrar condições de captura junto aos artefatos. -->
<!-- deck-caution: Browser controlado reduz, mas não elimina, diferenças de fonte, GPU e sistema operacional. -->
<!-- deck-question: Quais variáveis mudam pixels sem mudar o produto? -->

## Slide 34 — CAPTURA DE BASELINE

**Fala sugerida.** “Antes de capturar a baseline, o cenário é resetado para `normal`. Isso é uma precondição de teste, não um detalhe operacional. A captura só pode ser chamada de referência se sabemos qual estado da aplicação ela representa. Depois, o browser abre `/store/checkout`, aguarda estabilização e salva `baseline.png`. Em produção, além do arquivo, guardaríamos commit, browser, viewport, sistema, locale e responsável pela aprovação. Sem proveniência, uma baseline é apenas uma imagem órfã.”

**Exemplo além do slide.** Se alguém capturar a baseline enquanto `visual_checkout_shift` ainda está ativo, o teste futuro pode considerar o botão deslocado como normal e acusar o layout correto como regressão.

**Pergunte à turma.** “Que evidência provaria que esta baseline foi capturada no cenário saudável?”

**Resposta que vale construir.** Reset explícito, health/scenario registrado, comando reproduzível e metadados da execução.

**Transição.** “Agora alteramos exatamente uma variável para saber o que o diff deveria encontrar.”

<!-- deck-primary: Baseline é capturada com cenário normal e condições de browser conhecidas. -->
<!-- deck-engineering: Tratar estado da aplicação e proveniência como parte do artefato visual. -->
<!-- deck-caution: Uma baseline capturada sob defeito pode inverter o significado do teste. -->
<!-- deck-question: Como provar que a baseline representa o estado saudável? -->

## Slide 35 — CENÁRIO VISUAL CONTROLADO

**Fala sugerida.** “O cenário `visual_checkout_shift` altera uma única regra CSS: adiciona margem à esquerda do CTA. Isso cria um experimento controlado. Sabemos qual variável foi manipulada e qual região deveria responder. O objetivo não é simular toda a complexidade de uma regressão real, mas construir uma referência pedagógica para verificar se captura, diff, bbox, SSIM e VLM contam uma história coerente. Em um incidente real, não receberíamos o nome do cenário; aqui o usamos apenas para produzir ground truth durante a validação.”

**Exemplo além do slide.** É o equivalente visual de injetar latência conhecida no Dia 3: a falha é deliberada, mas a ferramenta de análise não deve receber a resposta pronta.

**Pergunte à turma.** “Por que mudar apenas o `margin-left` ajuda a avaliar a pipeline?”

**Resposta que vale construir.** Porque isola a causa conhecida e permite conferir se as evidências localizam e descrevem exatamente o efeito esperado.

**Transição.** “Mantemos a câmera igual e produzimos a observação atual.”

<!-- deck-primary: Um cenário controlado desloca apenas o CTA e fornece ground truth para validar a pipeline. -->
<!-- deck-engineering: Mudar uma variável por vez torna métricas e interpretação verificáveis. -->
<!-- deck-caution: Ground truth serve à validação; não deve ser entregue como resposta ao VLM. -->
<!-- deck-question: Por que uma única mudança CSS é um bom experimento controlado? -->

## Slide 36 — CAPTURA CURRENT

**Fala sugerida.** “Current deve repetir exatamente o protocolo da baseline, mudando somente o estado que queremos avaliar. Mesmo URL, browser, viewport, scale e espera; cenário diferente. Essa simetria é o coração de qualquer comparação. Se mudarmos aplicação e ambiente ao mesmo tempo, o diff não consegue separar causas. Após a captura, preservamos `current.png` em vez de apenas calcular um score e descartá-la, porque revisão humana e modelos posteriores precisam ver a evidência original.”

**Exemplo além do slide.** Rodar baseline no modo headless e current num browser visível pode introduzir diferenças de renderização. Um pipeline reproduzível encapsula configuração para evitar deriva entre os dois caminhos.

**Pergunte à turma.** “Qual é a única variável que deveria mudar entre baseline e current neste laboratório?”

**Resposta que vale construir.** O cenário da aplicação que desloca o CTA; todo o protocolo de captura permanece constante.

**Transição.** “Com as duas imagens comparáveis, começamos pela medida mais direta: quais pixels mudaram.”

<!-- deck-primary: Current repete o protocolo da baseline e altera somente o cenário sob teste. -->
<!-- deck-engineering: Preservar imagem original e configuração para revisão e reprocessamento posterior. -->
<!-- deck-caution: Mudar ambiente e produto simultaneamente torna a causa do diff ambígua. -->
<!-- deck-question: Qual variável deve diferir entre baseline e current? -->

## Slide 37 — PIXEL DIFF: O PRIMEIRO SINAL

**Fala sugerida.** “Pixel diff pergunta, de forma simples, quantas posições ultrapassaram uma tolerância de diferença. O ratio de aproximadamente 0,01148 significa que cerca de 1,15% dos pixels foram considerados diferentes. Isso prova que houve alteração mensurável, mas não diz se é bug, onde está nem qual função foi afetada. É um detector sensível, útil como primeiro sinal e como base para localizar regiões. O threshold por pixel também importa: tolerância zero reagiria a variações mínimas de rasterização; tolerância alta poderia esconder mudanças sutis.”

**Exemplo além do slide.** Mover um botão gera diferença tanto onde ele estava quanto onde passou a estar. Por isso a área de pixels diferentes pode ser maior que a área visível do próprio botão.

**Pergunte à turma.** “O ratio de 1,15% permite dizer que o impacto é baixo?”

**Resposta que vale construir.** Não. Ele mede extensão global da diferença, não criticidade da região.

**Transição.** “Para recuperar contexto espacial, calculamos a menor caixa que contém as diferenças.”

<!-- deck-primary: Pixel ratio quantifica extensão da mudança, mas não explica região, significado ou impacto. -->
<!-- deck-engineering: Aplicar tolerância explícita e preservar a máscara de pixels diferentes. -->
<!-- deck-caution: Percentual global pequeno não implica risco pequeno. -->
<!-- deck-question: O que 1,15% de pixels diferentes realmente permite concluir? -->

## Slide 38 — BOUNDING BOX: ONDE MUDOU

**Fala sugerida.** “A bounding box transforma uma lista dispersa de pixels em coordenadas espaciais: esquerda, topo, direita e base da menor região que contém a diferença. No nosso caso, ela envolve a posição original e a nova posição do CTA. Isso é valioso para revisão humana, para políticas regionais e para orientar o VLM. Mas bbox ainda é uma simplificação. Duas mudanças distantes podem produzir uma caixa enorme contendo espaço que não mudou. Sistemas mais avançados usam componentes conectados ou múltiplas regiões.”

**Exemplo além do slide.** Se preço e rodapé mudarem simultaneamente, uma única bbox poderia cobrir quase toda a página, embora apenas duas ilhas pequenas tenham diferenças.

**Pergunte à turma.** “Como a bbox ajuda a tratar um CTA de forma diferente de um fundo decorativo?”

**Resposta que vale construir.** Permite cruzar coordenadas com regiões críticas e aplicar thresholds/políticas específicos.

**Transição.** “Agora acrescentamos uma medida que observa estrutura local, e não apenas igualdade de pixels.”

<!-- deck-primary: Bounding box localiza espacialmente a mudança e permite políticas sensíveis à região. -->
<!-- deck-engineering: Cruzar região alterada com elementos críticos e, quando necessário, usar múltiplos componentes. -->
<!-- deck-caution: Uma única bbox pode incluir grandes áreas intactas quando há mudanças distantes. -->
<!-- deck-question: Como coordenadas ajudam a diferenciar CTA de decoração? -->

## Slide 39 — SSIM: SIMILARIDADE ESTRUTURAL

**Fala sugerida.** “SSIM compara padrões locais de luminância, contraste e estrutura. Diferente de uma contagem exata de pixels, ele tenta aproximar aspectos que o sistema visual humano percebe como semelhança. O resultado fica próximo de 1 quando as imagens têm estrutura muito semelhante. Nosso 0,9869 é alto porque quase toda a página permanece igual. Isso não contradiz o diff; responde a outra pergunta. Pixel ratio diz quanto divergiu sob uma regra. SSIM diz quão parecida permanece a estrutura global/local agregada.”

**Exemplo além do slide.** Uma pequena mudança de brilho em toda a tela pode alterar muitos pixels e ainda preservar estrutura. Um botão deslocado preserva a maior parte da página, mantendo SSIM alto, embora exista uma regressão localizada.

**Pergunte à turma.** “SSIM alto e pixel diff não zero podem ser verdade ao mesmo tempo?”

**Resposta que vale construir.** Sim. As métricas medem propriedades diferentes e devem ser interpretadas em conjunto.

**Transição.** “Vale abrir a fórmula apenas o suficiente para entender de onde essa sensibilidade vem.”

<!-- deck-primary: SSIM mede semelhança estrutural local agregando luminância, contraste e padrões. -->
<!-- deck-engineering: Interpretar SSIM junto com pixel ratio e região, não como oracle isolado. -->
<!-- deck-caution: Score próximo de 1 pode coexistir com defeito pequeno e crítico. -->
<!-- deck-question: Por que SSIM alto não contradiz um diff visível? -->

## Slide 40 — A MATEMÁTICA INTUITIVA DO SSIM

**Fala sugerida.** “Não precisamos decorar a fórmula. Pensem em janelas pequenas percorrendo as imagens. Em cada janela, comparamos brilho médio, variação de intensidade e a maneira como os padrões se movem juntos. Médias sustentam luminância; desvios sustentam contraste; covariância ajuda a comparar estrutura. Constantes evitam instabilidade quando os denominadores ficam próximos de zero. O código usa `data_range=255` porque trabalha com grayscale de 8 bits. O score final agrega essas comparações locais. É justamente essa agregação que pode diluir uma região pequena.”

**Exemplo além do slide.** Duas áreas totalmente brancas têm pouca variância; sem constantes de estabilização, a divisão seria numericamente frágil. Já contornos e texto carregam estrutura local forte.

**Pergunte à turma.** “O que perdemos ao converter RGB para grayscale?”

**Resposta que vale construir.** Mudanças puramente cromáticas podem ficar menos visíveis se preservarem luminância semelhante.

**Transição.** “Essa limitação matemática aparece claramente quando confrontamos o score com o CTA.”

<!-- deck-primary: SSIM percorre janelas e compara brilho, contraste e estrutura antes de agregar um score. -->
<!-- deck-engineering: Entender data range, canal e agregação para interpretar o número corretamente. -->
<!-- deck-caution: Grayscale pode reduzir sensibilidade a regressões apenas cromáticas. -->
<!-- deck-question: Que tipo de mudança pode desaparecer parcialmente ao remover cor? -->

## Slide 41 — SCORE GLOBAL E BUG LOCALIZADO

**Fala sugerida.** “Este é o paradoxo central do dia: 0,9869 parece excelente, mas o CTA está claramente fora da posição anterior. Um score global comprime a imagem inteira em um número. A área intacta domina a média. Em qualidade, agregação pode esconder caudas e regiões críticas — a mesma lógica que veremos em latência média versus requests lentos. Por isso a política precisa conhecer regiões de interesse. Uma mudança pequena no botão que conclui compra pode exigir review, enquanto uma mudança maior em fundo decorativo pode ser aceita.”

**Exemplo além do slide.** Em uma tela 1280×800 existem mais de um milhão de pixels. Um botão ocupa uma fração pequena, mas representa uma parcela enorme da jornada de conversão.

**Pergunte à turma.** “Qual métrica regional criariam para este CTA?”

**Resposta que vale construir.** Comparação ou threshold específico dentro da área do CTA, combinada com presença, posição e talvez acessibilidade.

**Transição.** “Vamos conferir se todas as evidências produzidas apontam para essa mesma interpretação.”

<!-- deck-primary: Score global alto pode esconder regressão localizada em uma região de alto impacto. -->
<!-- deck-engineering: Definir regiões críticas e políticas específicas em vez de depender apenas da média global. -->
<!-- deck-caution: Área em pixels e impacto de negócio não possuem relação proporcional. -->
<!-- deck-question: Que política regional protegeria melhor o CTA? -->

## Slide 42 — EVIDÊNCIA REAL VALIDADA

**Fala sugerida.** “Agora leiam os três números como uma narrativa. O ratio confirma diferença mensurável. A bbox restringe a mudança à faixa que contém o botão. O SSIM alto diz que a página como um todo permanece estruturalmente semelhante. Juntos, eles sustentam a frase: ‘houve uma alteração pequena e localizada no layout’. Eles ainda não sustentam ‘a conversão caiu’ nem ‘o checkout está quebrado’. Evidência forte inclui também saber o que não podemos concluir.”

**Exemplo além do slide.** Para provar impacto funcional, precisaríamos de teste de interação, acessibilidade, analytics ou experimento com usuário. Screenshot não mede clique nem conversão.

**Pergunte à turma.** “Qual é a afirmação mais forte que estes números permitem fazer sem exagero?”

**Resposta que vale construir.** Existe uma mudança visual localizada na região do CTA, enquanto o restante permanece altamente semelhante.

**Transição.** “Para comunicar isso rapidamente a uma pessoa ou modelo, produzimos um artefato visual de contraste.”

<!-- deck-primary: Ratio, bbox e SSIM juntos sustentam mudança pequena, localizada e estruturalmente limitada. -->
<!-- deck-engineering: Formular conclusões proporcionais ao que as métricas realmente observam. -->
<!-- deck-caution: Métrica visual não prova impacto funcional, conversão ou intenção de design. -->
<!-- deck-question: Qual é a conclusão mais forte sustentada pelos três números? -->

## Slide 43 — DIFF COMO ARTEFATO DE COMUNICAÇÃO

**Fala sugerida.** “O `diff.png` existe para tornar diferença perceptível e compartilhável. O código amplifica o contraste, porque a diferença bruta pode ser sutil demais para revisão rápida. Ele serve tanto para humanos quanto para o VLM, mas não é uma explicação semântica: pixels claros indicam divergência, não ‘erro’. Persistir baseline, current, diff e métricas permite reavaliar a decisão sem reproduzir imediatamente o ambiente. Isso é especialmente importante em CI, onde a execução pode ter desaparecido quando alguém revisa o resultado.”

**Exemplo além do slide.** Um reviewer consegue abrir três imagens lado a lado e verificar se a bbox realmente corresponde ao CTA. Sem os arquivos, teria apenas um score sem possibilidade de contestação.

**Pergunte à turma.** “Por que não guardar apenas `metrics.json`?”

**Resposta que vale construir.** Porque métricas comprimem informação; imagens preservam contexto para revisão, auditoria e novas análises.

**Transição.** “É sobre esse conjunto de evidências, e não sobre uma imagem solta, que o VLM fará triagem.”

<!-- deck-primary: Diff amplifica e comunica onde as imagens divergem para humanos e modelos. -->
<!-- deck-engineering: Persistir baseline, current, diff e métricas como pacote de evidência auditável. -->
<!-- deck-caution: Diff destaca mudança, mas não identifica sozinho bug, causa ou impacto. -->
<!-- deck-question: O que se perde quando guardamos apenas um score? -->

## Slide 44 — VLM COMO TRIADOR VISUAL

**Fala sugerida.** “O VLM recebe baseline, current, diff e métricas. Sua função é transformar evidência visual em uma descrição estruturada: tipo de mudança, severidade sugerida, região, justificativa e recomendação. Chamamos isso de triagem porque organiza o review; não chamamos de oracle final. No resultado validado, o modelo identifica `button_shift`, cita a região e relaciona ratio e SSIM. Isso é melhor que ‘há uma diferença’, porque produz linguagem que outra etapa consegue consumir. Ainda assim, `severity=low` é julgamento contextual e pode ser contestado.”

**Exemplo além do slide.** Para um blog, botão deslocado pode ser cosmético. Para pagamento, a mesma mudança pode afetar layout responsivo ou acessibilidade. A imagem não contém todo o contexto de negócio.

**Pergunte à turma.** “O que torna esta resposta mais auditável que uma frase livre?”

**Resposta que vale construir.** Schema, campos explícitos, referência à região e evidências citadas permitem validação e comparação downstream.

**Transição.** “A qualidade dessa triagem começa pela forma como descrevemos imagens e limites no prompt.”

<!-- deck-primary: VLM organiza evidência visual em triagem estruturada; não substitui o oracle ou a policy. -->
<!-- deck-engineering: Exigir tipo, região, evidência e recomendação em schema validável. -->
<!-- deck-caution: Severidade sugerida depende de contexto de negócio ausente na imagem. -->
<!-- deck-question: Por que chamamos o VLM de triador, e não de juiz? -->

## Slide 45 — O PROMPT MULTIMODAL

**Fala sugerida.** “Em prompt multimodal, ordem e papel das imagens precisam ser explícitos: baseline, current e diff. O texto também entrega métricas e exige que a evidência cite tanto a mudança visível quanto os números. A instrução de não inferir correção funcional evita que o modelo extrapole de layout para comportamento. O payload usa o formato nativo do Ollama: conteúdo textual e imagens base64 separadas. Uma implementação anterior enviava conteúdo no estilo de outra API e falhava na desserialização. Esse detalhe mostra que ‘multimodal’ não é um protocolo universal; cada runtime possui contrato próprio.”

**Exemplo além do slide.** Se baseline e current forem invertidas, o modelo pode descrever corretamente uma mudança na direção errada e sugerir que o estado saudável é o regressivo.

**Pergunte à turma.** “Que frase do prompt limita mais uma conclusão indevida?”

**Resposta que vale construir.** A proibição de inferir functional correctness e a obrigação de citar evidência específica.

**Transição.** “O resultado desse contrato é um objeto que podemos discutir campo por campo.”

<!-- deck-primary: Prompt define ordem das imagens, fornece métricas e limita explicitamente o escopo da interpretação. -->
<!-- deck-engineering: Usar payload nativo do runtime e structured output para receber triagem validável. -->
<!-- deck-caution: Ordem ambígua ou formato incompatível produz interpretação errada ou falha de transporte. -->
<!-- deck-question: Qual instrução impede o VLM de afirmar que o checkout funciona? -->

## Slide 46 — TRIAGEM ESTRUTURADA

**Fala sugerida.** “Leiam o objeto como uma hipótese de review. `change_type` nomeia o padrão. `affected_region` conecta texto à bbox. `evidence` explica por que a classificação foi feita. `recommendation=review` admite ambiguidade: há diferença real, mas falta autoridade para aceitar ou bloquear automaticamente. Structured output melhora consumo por software, porém não torna `low` objetivamente verdadeiro. Se duas pessoas discordarem da severidade, o pipeline não fracassou; revelou uma decisão que precisa de política ou contexto adicional.”

**Exemplo além do slide.** Poderíamos validar sintaticamente que severity pertence a `low|medium|high`, mas não que `low` é adequado ao checkout. Para isso precisamos de regras de criticidade ou revisão humana.

**Pergunte à turma.** “Qual campo é mais factual e qual é mais interpretativo?”

**Resposta que vale construir.** A região/métricas são mais diretamente observáveis; severidade e recomendação incorporam julgamento.

**Transição.** “Vamos explicitar agora as decisões que permanecem fora da autoridade do VLM.”

<!-- deck-primary: Saída estruturada separa descrição, região, evidência e recomendação para revisão. -->
<!-- deck-engineering: Validar formato e tratar severidade como julgamento sujeito a política e contexto. -->
<!-- deck-caution: Campo enumerado não transforma interpretação probabilística em fato objetivo. -->
<!-- deck-question: Quais campos são observação e quais são julgamento? -->

## Slide 47 — O QUE O VLM NÃO DECIDE

**Fala sugerida.** “O VLM não comprova que o botão funciona, não mede conversão, não sabe se o design foi aprovado, não atualiza baseline e não concede waiver. Ele descreve o que vê sob as instruções recebidas. Essa separação repete o Dia 1: o modelo propõe ou interpreta; outras camadas governam ação e decisão. Também evita um ciclo perigoso em que o mesmo modelo identifica mudança, declara que ela é aceitável e atualiza a referência, eliminando a possibilidade de auditoria.”

**Exemplo além do slide.** Para dizer que o deslocamento torna o botão inclicável, precisaríamos executar interação ou verificar sobreposição e hitbox. A posição nos pixels, isoladamente, não prova isso.

**Pergunte à turma.** “Que evidência adicional seria necessária para afirmar impacto funcional?”

**Resposta que vale construir.** Teste de interação, acessibilidade, DOM/layout, analytics ou regra explícita da região crítica.

**Transição.** “Essas evidências e responsabilidades são combinadas numa política de três estados.”

<!-- deck-primary: VLM descreve mudança; não prova função, atualiza baseline nem decide release sozinho. -->
<!-- deck-engineering: Separar diagnóstico visual de ações e decisões com impacto de governança. -->
<!-- deck-caution: Imagem não contém automaticamente intenção de design ou efeito sobre usuário. -->
<!-- deck-question: O que falta para provar que o CTA deslocado quebra a jornada? -->

## Slide 48 — POLÍTICAS VISUAIS: ACCEPT/REVIEW/BLOCK

**Fala sugerida.** “Três estados evitam forçar uma resposta binária onde existe incerteza. `ACCEPT` significa mudança dentro de tolerância conhecida ou explicitamente aprovada. `REVIEW` significa evidência real, mas impacto ou intenção ainda precisam de decisão humana. `BLOCK` significa violação clara de uma regra crítica. A precedência e os critérios pertencem à policy, não ao estilo de escrita do modelo. Em produção, políticas podem variar por componente, branch, severidade e região. O mesmo pixel ratio pode ser aceitável numa página interna e exigir review no checkout.”

**Exemplo além do slide.** Ausência do logo numa página de teste pode gerar review; ausência do botão de confirmar transferência pode bloquear por regra regional, mesmo com SSIM alto.

**Pergunte à turma.** “Quando `REVIEW` é melhor que escolher o threshold mais conservador?”

**Resposta que vale construir.** Quando o custo de falso positivo e falso negativo é alto e a evidência não resolve intenção/impacto automaticamente.

**Transição.** “Um dos maiores produtores de review desnecessário é conteúdo dinâmico não tratado.”

<!-- deck-primary: ACCEPT, REVIEW e BLOCK representam tolerância, ambiguidade e violação crítica. -->
<!-- deck-engineering: Definir critérios por região, risco e contexto, independentemente da linguagem do VLM. -->
<!-- deck-caution: Política visual não deve ser reduzida a um threshold global ou à recomendação do modelo. -->
<!-- deck-question: Quando REVIEW é mais seguro que uma decisão binária automática? -->

## Slide 49 — CONTEÚDO DINÂMICO E MÁSCARAS

**Fala sugerida.** “Datas, IDs, avatares, anúncios e preços voláteis criam diferenças esperadas. Uma máscara exclui ou flexibiliza a comparação em regiões conhecidas. Isso reduz ruído, mas cada máscara retira capacidade de detecção. Portanto, ela precisa ser estreita, justificada e revisada. A solução preferível muitas vezes é controlar o dado — relógio fixo, fixture estável, animação desabilitada — antes de mascarar. Máscara deve ser último recurso para variabilidade legítima, não uma borracha aplicada depois que o teste fica vermelho.”

**Exemplo além do slide.** Mascarar toda a área do resumo de pedido impediria detectar preço cortado ou quantidade errada. Mascarar apenas o timestamp pode preservar o restante da validação.

**Pergunte à turma.** “Quando é melhor estabilizar o dado do que mascarar a região?”

**Resposta que vale construir.** Sempre que controlamos a fonte com baixo custo, porque isso preserva maior cobertura visual.

**Transição.** “Máscaras mostram na prática como reduzir ruído pode aumentar cegueira.”

<!-- deck-primary: Máscaras tratam regiões legitimamente dinâmicas, mas removem capacidade de detectar regressões. -->
<!-- deck-engineering: Preferir estabilização de dados; manter máscaras pequenas, justificadas e revisáveis. -->
<!-- deck-caution: Máscaras amplas reduzem false positives às custas de false negatives. -->
<!-- deck-question: Quando controlar a fonte é melhor que mascarar o resultado? -->

## Slide 50 — FALSE POSITIVES E FALSE NEGATIVES

**Fala sugerida.** “False positive é acusar regressão onde a mudança é aceitável. Ele consome tempo, gera fadiga e leva equipes a ignorar alertas. False negative é aceitar uma regressão relevante. Ele preserva velocidade no curto prazo e transfere o custo para usuário ou produção. Thresholds, máscaras e políticas deslocam esse equilíbrio. Não existe configuração universal; precisamos perguntar qual erro custa mais em cada região. Em checkout, invisibilidade ou deslocamento de CTA tende a justificar sensibilidade maior que em decoração.”

**Exemplo além do slide.** Se uma suíte gera cem falsos alarmes por dia, reviewers podem aprovar tudo mecanicamente. Uma ferramenta extremamente sensível pode, paradoxalmente, reduzir segurança por fadiga.

**Pergunte à turma.** “Qual erro é mais caro neste CTA e por quê?”

**Resposta que vale construir.** Provavelmente false negative, por estar ligado a conclusão da compra; mas frequência e custo de review ainda importam.

**Transição.** “O caso mais perigoso ocorre quando normalizamos o defeito na própria referência.”

<!-- deck-primary: False positive gera ruído e fadiga; false negative deixa regressão relevante escapar. -->
<!-- deck-engineering: Ajustar sensibilidade por custo do erro e criticidade da região. -->
<!-- deck-caution: Sensibilidade extrema pode produzir rubber-stamping e reduzir segurança real. -->
<!-- deck-question: Qual erro é mais caro na região do CTA? -->

## Slide 51 — BASELINE POLLUTION

**Fala sugerida.** “Baseline pollution acontece quando uma mudança não validada entra na referência e passa a ser tratada como normal. A partir daí, o teste não apenas deixa de detectar o defeito; pode acusar uma correção futura como regressão. Isso transforma atualização de baseline em ação de governança. O arquivo precisa estar ligado a uma mudança intencional, revisão e histórico. Atualizar automaticamente porque ‘o teste falhou’ equivale a reescrever o gabarito depois de ver a resposta.”

**Exemplo além do slide.** Se o CTA desaparecer e o pipeline aceitar `current.png` como nova baseline, a próxima execução sem botão terá score perfeito. A métrica estará correta; a referência estará corrompida.

**Pergunte à turma.** “Qual condição mínima deveria existir antes de promover current para baseline?”

**Resposta que vale construir.** Mudança intencional identificada, evidência revisada, aprovação autorizada e registro da versão.

**Transição.** “Os grupos agora vão trabalhar exatamente nesses trade-offs de referência, ruído e impacto.”

<!-- deck-primary: Baseline pollution normaliza um defeito e pode transformar a correção futura em falso alarme. -->
<!-- deck-engineering: Exigir revisão, intenção e histórico antes de promover current para referência. -->
<!-- deck-caution: Atualizar baseline para fazer o teste passar reescreve o oracle visual. -->
<!-- deck-question: O que precisa acontecer antes de current virar baseline? -->

## Slide 52 — EXERCÍCIO MENTORADO DIA 2

**Fala sugerida.** “Cada grupo recebe uma variação visual, mas não basta produzir imagens diferentes. Vocês precisam controlar o ambiente, explicar a origem da diferença, interpretar métricas, discutir false positive e false negative e propor uma policy defensável. Grupos de viewport e fonte devem mostrar por que ambiente cria ruído. Grupos de CTA ausente ou região crítica devem mostrar por que score global pode falhar. O grupo de desacordo entre VLM e threshold precisa separar observação, interpretação e decisão. Trabalhem em `student_work`; não alterem o comparador ou o triador congelado para favorecer o resultado.”

**Exemplo além do slide.** Se o grupo muda viewport e conclui “o produto regrediu”, faltou reconhecer que a condição de captura também mudou. A evidência correta pode ser “comparação inválida por ambiente incompatível”.

**Pergunte à turma.** “Qual informação deve aparecer em todo report antes de qualquer score?”

**Resposta que vale construir.** Condições de captura: browser, viewport, scale, cenário e origem da baseline.

**Transição.** “A rubrica valoriza precisamente a qualidade dessa interpretação.”

<!-- deck-primary: Grupos analisam oito variações com captura, métricas, policy e discussão de FP/FN. -->
<!-- deck-engineering: Trabalhar em student_work e preservar comparador, VLM e cenários do núcleo. -->
<!-- deck-caution: Imagens diferentes sob ambientes diferentes não sustentam conclusão de regressão. -->
<!-- deck-question: Que metadados precisam acompanhar todo score visual? -->

## Slide 53 — RUBRICA VISUAL

**Fala sugerida.** “A policy vale mais porque é onde a equipe traduz evidência em decisão de risco. Captura reproduzível vem em seguida: sem comparabilidade, métricas perdem validade. Interpretar score significa dizer o que ele mede e o que não mede. A discussão de falsos positivos e negativos mostra maturidade para operar o sistema. Evidência visual e apresentação completam a rastreabilidade. Não pontuamos quem obtiver o menor diff; pontuamos quem construir a conclusão mais defensável para o cenário.”

**Exemplo além do slide.** Um grupo com SSIM 0,99 pode ter trabalho excelente se identificar um defeito crítico localizado e justificar review/block. Um grupo com SSIM 0,80 pode estar apenas comparando browsers diferentes.

**Pergunte à turma.** “Como provar que o ambiente foi controlado?”

**Resposta que vale construir.** Registrar configuração, reutilizar o mesmo protocolo, mostrar cenário e preservar comandos/artefatos.

**Transição.** “Vamos fechar o dia separando novamente medição, interpretação e autoridade.”

<!-- deck-primary: A avaliação privilegia policy alinhada ao risco, captura reproduzível e interpretação correta. -->
<!-- deck-engineering: Julgar qualidade da evidência e da decisão, não buscar o menor score. -->
<!-- deck-caution: Score preciso sobre comparação inválida continua sendo evidência inválida. -->
<!-- deck-question: Como o grupo demonstra que só o produto mudou? -->

## Slide 54 — FECHAMENTO DIA 2

**Fala sugerida.** “A frase do Dia 2 é: Playwright controla a observação; pixel diff mede extensão; bbox localiza; SSIM estima semelhança estrutural; VLM descreve; policy decide. Nenhuma dessas camadas deve fingir ser a outra. Guardamos os artefatos porque amanhã eles entram no relatório integrado junto com o teste funcional. A ponte para o Dia 3 é importante: em produção, também teremos sinais incompletos e agregados. Uma métrica alta não conta a causa; um trace lento não autoriza remediação; uma narrativa do agente não substitui política.”

**Exemplo além do slide.** `current.png` é a observação visual de uma execução. No Dia 3, o equivalente será um conjunto de séries e traces observados numa janela de incidente.

**Pergunte à turma.** “Qual sinal operacional faria o papel mais próximo do current?”

**Resposta que vale construir.** Métricas e traces da janela atual comparados a comportamento saudável ou SLO, preservando contexto.

**Transição.** “Amanhã deixamos de perguntar ‘o que mudou na tela?’ e passamos a perguntar ‘o que explica o sintoma em produção?’.”

<!-- deck-primary: Captura mede, métricas quantificam, VLM interpreta e policy governa a decisão visual. -->
<!-- deck-engineering: Preservar artifacts/visual como evidência para o release report integrado. -->
<!-- deck-caution: Triagem visual não prova função nem autoriza decisão final isoladamente. -->
<!-- deck-question: Que sinal operacional substitui a imagem current num incidente de latência? -->

---

# Dia 3 — Assistente SRE inteligente

## Slide 55 — DIA 3: ASSISTENTE SRE INTELIGENTE

**Fala sugerida.** “Nos dois primeiros dias, sabíamos antecipadamente o caminho de execução. Hoje começamos apenas com um sintoma: checkout mais lento que o esperado. O agente não recebe `payment_latency`, nem a causa, nem o nome correto do serviço no Jaeger. Ele precisa escolher evidências, consultar ferramentas read-only e produzir uma conclusão proporcional aos dados. Essa é a primeira tarefa da semana que realmente justifica um loop agentic, porque a próxima consulta depende do que foi observado. Mesmo assim, autonomia termina antes de qualquer mutação: o agente investiga e propõe; uma pessoa autoriza ação.”

**Exemplo além do slide.** Um diagnóstico pode apontar para payment provider, banco, saturação de CPU, mudança recente ou telemetria insuficiente. O agente precisa reduzir esse espaço sem começar pela resposta conhecida do laboratório.

**Pergunte à turma.** “Qual é a diferença entre gerar uma explicação e conduzir uma investigação?”

**Resposta que vale construir.** Investigação formula hipóteses, coleta evidência que pode contradizê-las e revisa a conclusão; explicação pode apenas soar plausível.

**Transição.** “O primeiro risco do dia é justamente uma RCA convincente fabricada sem dados.”

<!-- deck-primary: O agente recebe um sintoma e investiga com métricas e traces sem conhecer o cenário injetado. -->
<!-- deck-engineering: Usar loop agentic read-only e separar investigação de qualquer ação mutável. -->
<!-- deck-caution: Narrativa causal plausível não é evidência de causa raiz. -->
<!-- deck-question: O que diferencia investigação de explicação convincente? -->

## Slide 56 — O PROBLEMA: INVESTIGAR SEM INVENTAR RCA

**Fala sugerida.** “LLMs completam padrões. Diante de ‘checkout lento’, eles conseguem listar causas frequentes e construir uma narrativa coerente. Em SRE, isso é perigoso porque familiaridade não é evidência. Uma RCA exige linha temporal, sinais, hipóteses testadas, fatores contribuintes e limites do que foi verificado. O agente deve poder terminar com ‘evidência insuficiente’. Essa resposta é mais valiosa que uma certeza inventada. Também precisamos separar sintoma, correlação, causa provável e causa raiz verificada. Cada degrau exige evidência adicional.”

**Exemplo além do slide.** Encontrar um deploy recente e aumento de latência na mesma janela é correlação. Para fortalecer causalidade, precisaríamos comparar versões, reproduzir, fazer rollback controlado ou observar mecanismo específico.

**Pergunte à turma.** “O que torna uma narrativa causal falsificável?”

**Resposta que vale construir.** Ela explicita hipótese, evidência esperada, observações contrárias e quais experimentos poderiam refutá-la.

**Transição.** “Para obter essas observações, precisamos de instrumentação que revele estados internos.”

<!-- deck-primary: RCA não é texto plausível; é processo de hipótese, evidência, revisão e limites. -->
<!-- deck-engineering: Permitir conclusão de evidência insuficiente e exigir afirmações falsificáveis. -->
<!-- deck-caution: Coincidência temporal e padrão comum não provam causa raiz. -->
<!-- deck-question: Que propriedade torna uma hipótese operacional falsificável? -->

## Slide 57 — DEFINIÇÃO CANÔNICA: OBSERVABILIDADE

**Fala sugerida.** “Observabilidade é a capacidade de inferir estados internos a partir de sinais externos úteis. Não é sinônimo de instalar Prometheus ou Jaeger. Uma aplicação pode exportar milhares de métricas e continuar impossível de investigar se não há nomes consistentes, dimensões relevantes ou ligação com a jornada do usuário. Monitoring tende a acompanhar condições conhecidas e alertas predefinidos; observabilidade ajuda a fazer perguntas novas durante incidentes. Não são opostos: bons monitores iniciam investigações, e boa observabilidade permite explicar alertas.”

**Exemplo além do slide.** Saber que CPU está em 90% não informa se usuários sofrem. Saber que checkout p95 violou objetivo e que spans de payment dominam a duração aproxima sinal técnico do impacto.

**Pergunte à turma.** “Ter dashboards significa ter observabilidade?”

**Resposta que vale construir.** Não. Precisamos de instrumentação relevante, contexto, qualidade dos dados e capacidade de formular consultas úteis.

**Transição.** “As consultas serão feitas sobre sinais com granularidades diferentes.”

<!-- deck-primary: Observabilidade permite inferir estado interno a partir de sinais externos relevantes. -->
<!-- deck-engineering: Projetar instrumentação para perguntas e jornadas, não apenas instalar ferramentas. -->
<!-- deck-caution: Volume de telemetria e quantidade de dashboards não garantem investigabilidade. -->
<!-- deck-question: O que falta quando há dashboard, mas ninguém consegue explicar o alerta? -->

## Slide 58 — MÉTRICAS, LOGS E TRACES

**Fala sugerida.** “Métricas resumem comportamento ao longo do tempo e são eficientes para tendência, magnitude e alerta. Logs registram eventos e contexto textual; ajudam em detalhes, mas podem ser inconsistentes e caros. Traces acompanham uma requisição e distribuem duração entre operações, revelando caminho e relações. Nenhum sinal substitui os outros. Métrica pode dizer que latência aumentou; trace mostra quais operações ocuparam tempo; log pode explicar um erro específico. SLO não é um quarto sinal bruto, mas a regra operacional que dá significado a indicadores.”

**Exemplo além do slide.** Um histograma mostra aumento de latência do payment provider. Um trace mostra `payment.request` com 253 ms. Um log downstream poderia revelar throttling — mas o laboratório não possui esse último dado, então não devemos inventá-lo.

**Pergunte à turma.** “Qual sinal vocês consultariam primeiro num alerta de latência?”

**Resposta que vale construir.** Métrica para confirmar escopo/tendência, depois traces para localizar requisições e operações; a ordem depende do alerta e custo.

**Transição.** “Existem heurísticas úteis para escolher métricas, mas elas não substituem objetivos.”

<!-- deck-primary: Métricas mostram tendência, logs detalham eventos e traces distribuem caminho e duração. -->
<!-- deck-engineering: Combinar sinais e declarar quando um tipo de evidência não está disponível. -->
<!-- deck-caution: Nenhum sinal isolado prova causalidade ou substitui SLO. -->
<!-- deck-question: Qual sinal confirma magnitude e qual localiza a operação lenta? -->

## Slide 59 — RED E USE

**Fala sugerida.** “RED organiza sinais de serviços: Rate, Errors e Duration. USE organiza recursos: Utilization, Saturation e Errors. RED começa mais perto da experiência de uma API; USE ajuda quando suspeitamos de infraestrutura. Utilização é quanto do recurso está ocupado. Saturação é trabalho esperando porque a capacidade foi excedida — filas, throttling, run queue. Uma CPU alta pode ser eficiente e saudável; uma CPU moderada com fila bloqueada pode ser problemática. Heurísticas orientam onde olhar, mas o SLO diz quando o usuário está fora do aceitável.”

**Exemplo além do slide.** Checkout lento com CPU normal não elimina dependência externa. Payment duration alta, sem erros, mostra que RED pode detectar degradação mesmo quando disponibilidade permanece 100%.

**Pergunte à turma.** “CPU em 90% é incidente?”

**Resposta que vale construir.** Não por si só. Precisamos de saturação, duração, erros e impacto sobre SLI/SLO.

**Transição.** “Para transformar sinal em consequência operacional, definimos indicador, objetivo e orçamento.”

<!-- deck-primary: RED observa serviço; USE observa recursos; ambos orientam investigação sem substituir SLO. -->
<!-- deck-engineering: Distinguir utilização de saturação e conectar sinais à experiência do usuário. -->
<!-- deck-caution: Métrica de recurso alta isoladamente não define incidente. -->
<!-- deck-question: CPU alta basta para concluir impacto no usuário? -->

## Slide 60 — SLI, SLO E ERROR BUDGET

**Fala sugerida.** “SLI é a medida: por exemplo, proporção de checkouts abaixo de 300 ms. SLO é o objetivo sobre essa medida numa janela: 99,9% em 30 dias. Error budget é a parcela de falha ou degradação que o objetivo permite. SLA é compromisso externo, geralmente com consequências contratuais; não deve ser confundido com objetivo interno. O orçamento permite equilibrar confiabilidade e velocidade. Buscar 100% pode ser economicamente irracional e tecnicamente impossível. Também não podemos inferir violação de SLO a partir de uma única requisição lenta; precisamos da distribuição e da janela.”

**Exemplo além do slide.** Em um milhão de checkouts com SLO 99,9%, aproximadamente mil podem ficar fora do indicador antes de consumir todo o orçamento — dependendo da definição exata.

**Pergunte à turma.** “Qual SLI escolheriam para o checkout: média de latência ou proporção abaixo de limite?”

**Resposta que vale construir.** Proporção/percentil alinhado à experiência tende a ser mais útil que média, que pode esconder caudas.

**Transição.** “No laboratório não implementamos um motor completo de SLO; injetamos um sinal concreto para investigar.”

<!-- deck-primary: SLI mede, SLO define objetivo em uma janela e error budget quantifica tolerância. -->
<!-- deck-engineering: Escolher indicadores próximos da experiência e interpretar distribuição, não um request isolado. -->
<!-- deck-caution: O núcleo demonstra sinais, mas não implementa cálculo completo de SLO/SLA. -->
<!-- deck-question: Por que média de latência pode ser um SLI fraco? -->

## Slide 61 — FALHA REAL: PAYMENT_LATENCY

**Fala sugerida.** “O cenário injeta aproximadamente 250 ms dentro da operação de pagamento. A aplicação continua respondendo e o pagamento pode ser aprovado; a falha é degradação, não indisponibilidade. Isso é importante porque muitos incidentes não aparecem como 500. O usuário sente lentidão, enquanto health check permanece verde. O laboratório mede uma execução normal e outra degradada para construir contraste. O agente, porém, recebe apenas ‘latência acima do esperado’. O nome do cenário pertence ao mecanismo de injeção, não à evidência de investigação.”

**Exemplo além do slide.** Um health endpoint que responde `ok` verifica que o processo está vivo. Ele não prova que todas as dependências estão dentro do objetivo de desempenho.

**Pergunte à turma.** “Como o sistema pode estar healthy e ainda ter incidente?”

**Resposta que vale construir.** Health cobre disponibilidade básica; SLO e dependências cobrem qualidade do serviço percebida.

**Transição.** “A primeira marca observável da injeção aparece numa métrica de dependência.”

<!-- deck-primary: payment_latency degrada uma dependência sem derrubar a API ou tornar health vermelho. -->
<!-- deck-engineering: Comparar comportamento normal e degradado sem revelar o cenário ao investigador. -->
<!-- deck-caution: Health check verde não demonstra que latência ou SLO estão saudáveis. -->
<!-- deck-question: Como existe incidente com status HTTP 200 e health=ok? -->

## Slide 62 — MÉTRICA REAL EXPOSTA

**Fala sugerida.** “O histograma de dependência registra tempo gasto em `payment_provider`. A série `_sum` acumula duração observada e `_count` acumula ocorrências. Dividir sum por count dá média no conjunto consultado; buckets permitem estimar distribuição/quantis quando usados corretamente. No laboratório, uma ocorrência torna o sum muito próximo da duração daquele pagamento. O label `dependency` permite agrupar por dependência sem usar IDs de alta cardinalidade. A métrica é evidence de que tempo foi medido nesse trecho; não prova o mecanismo interno do provedor.”

**Exemplo além do slide.** Se houver dez pagamentos, `_sum=2.5` não significa um request de 2,5 s. Precisamos de count/buckets ou traces para interpretar distribuição.

**Pergunte à turma.** “Por que consultar somente `_sum` pode enganar?”

**Resposta que vale construir.** Porque soma cresce com volume; sem count/janela não distinguimos frequência de duração individual.

**Transição.** “Prometheus transforma essa exposição local em séries consultáveis ao longo do tempo.”

<!-- deck-primary: Histograma de dependência registra sum, count e buckets para payment_provider. -->
<!-- deck-engineering: Interpretar sum junto com count/janela e manter labels de cardinalidade controlada. -->
<!-- deck-caution: Tempo medido na dependência não prova automaticamente causa física downstream. -->
<!-- deck-question: O que falta para interpretar corretamente uma série _sum? -->

## Slide 63 — PROMETHEUS COMO FONTE DE EVIDÊNCIA

**Fala sugerida.** “Prometheus coleta `/metrics` a cada cinco segundos e adiciona contexto de série. Antes de confiar em uma query, verificamos `/targets`: se `releaseguard` não estiver UP, resultado vazio pode significar ausência de coleta, não ausência de problema. A API de query retorna estrutura consistente e permite ao agente pedir exatamente o sinal necessário, em vez de despejar todo o exposition format no contexto. Labels tornam filtros possíveis, mas precisam de disciplina: `dependency=payment_provider` é estável; `order_id` criaria uma série por pedido e explosão de cardinalidade.”

**Exemplo além do slide.** Uma query vazia pode significar zero eventos, nome errado, janela errada ou target down. O agente deve distinguir essas hipóteses antes de concluir “não há latência”.

**Pergunte à turma.** “Por que verificar target antes de interpretar ausência de série?”

**Resposta que vale construir.** Porque precisamos saber se a ausência é dado do sistema ou falha de observação.

**Transição.** “Métrica mostra padrão agregado; para localizar uma requisição, instrumentamos spans.”

<!-- deck-primary: Prometheus coleta séries consultáveis; target health faz parte da validade da evidência. -->
<!-- deck-engineering: Consultar API com queries focadas e labels de baixa cardinalidade. -->
<!-- deck-caution: Resultado vazio não significa automaticamente ausência de incidente. -->
<!-- deck-question: Como distinguir zero eventos de falha de coleta? -->

## Slide 64 — OPENTELEMETRY NO FASTAPI

**Fala sugerida.** “OpenTelemetry fornece APIs e protocolos vendor-neutral para instrumentação e exportação. O `TracerProvider` cria spans; `Resource` identifica o processo com `service.name=releaseguard`; `BatchSpanProcessor` agrupa exportação; OTLP envia ao backend Jaeger. O nome do serviço parece detalhe, mas é chave de descoberta. Sem ele, o agente pode procurar `checkout`, enquanto o backend registra serviço desconhecido, e concluir incorretamente que não há traces. Instrumentação útil exige identidade consistente, nomes de operação estáveis e atributos sem dados sensíveis.”

**Exemplo além do slide.** O incidente fala em serviço lógico “checkout”, mas o processo instrumentado é `releaseguard`. O agente primeiro lista serviços para descobrir o nome real, em vez de assumir equivalência.

**Pergunte à turma.** “O que quebra quando equipes usam nomes diferentes para o mesmo serviço?”

**Resposta que vale construir.** Descoberta, dashboards, queries, correlação e automações passam a tratar evidência existente como ausente.

**Transição.** “Com identidade correta, o Jaeger consegue organizar as requisições por serviço e operação.”

<!-- deck-primary: OpenTelemetry instrumenta e exporta spans; service.name conecta processo à descoberta no Jaeger. -->
<!-- deck-engineering: Padronizar identidade, operação e atributos antes de automatizar investigação. -->
<!-- deck-caution: Nome lógico do incidente pode diferir do service.name registrado. -->
<!-- deck-question: Como identidade inconsistente produz falso diagnóstico de telemetria ausente? -->

## Slide 65 — JAEGER E TRACES DISTRIBUÍDOS

**Fala sugerida.** “Um trace representa a trajetória de uma requisição; spans representam operações com início, duração, atributos e relações. Em sistemas distribuídos, propagação de contexto conecta serviços diferentes numa árvore ou grafo temporal. Nosso laboratório possui spans simples, mas o princípio é o mesmo. Jaeger permite buscar pelo serviço real e comparar operações. Trace ajuda a localizar onde o tempo foi observado e qual request sofreu. Não revela automaticamente por que o código ou dependência levou aquele tempo.”

**Exemplo além do slide.** Um span de banco com 300 ms pode resultar de query ruim, lock, rede ou pool saturado. O trace localiza a fronteira; diagnóstico do mecanismo exige evidência adicional.

**Pergunte à turma.** “Qual a diferença entre dizer ‘o tempo está no payment span’ e ‘o provedor é a causa raiz’?”

**Resposta que vale construir.** A primeira é observação localizada; a segunda afirma mecanismo causal que ainda não foi verificado.

**Transição.** “Vamos comparar exatamente esse span entre comportamento normal e degradado.”

<!-- deck-primary: Trace individualiza a jornada; span localiza operação e duração dentro dela. -->
<!-- deck-engineering: Usar traces para reduzir o espaço de investigação, não para declarar causalidade automática. -->
<!-- deck-caution: O span mais lento indica onde o tempo apareceu, não necessariamente o mecanismo causal. -->
<!-- deck-question: O que um trace prova e o que ele apenas sugere? -->

## Slide 66 — SPAN PAYMENT.REQUEST

**Fala sugerida.** “A operação normal ficou abaixo de um milissegundo; a degradada chegou a aproximadamente 254 ms. A métrica e o trace convergem para a mesma fronteira: payment. Essa convergência aumenta confiança porque uma fonte agregada e uma requisição individual contam histórias compatíveis. Ainda assim, nossa formulação deve ser cuidadosa: ‘latência associada à operação payment.request’ ou ‘dependência de pagamento é causa provável’. Não temos telemetria interna do provedor para declarar falha raiz verificada.”

**Exemplo além do slide.** Se o trace mostrasse checkout lento, mas payment rápido, a hipótese de dependência seria enfraquecida e deveríamos procurar outro span ou trabalho não instrumentado.

**Pergunte à turma.** “Que evidência tornaria a causa externa mais forte?”

**Resposta que vale construir.** Traces/logs/métricas do provedor, erro ou saturação downstream, comparação de rede e reprodução isolada.

**Transição.** “O agente precisa transformar essa incerteza em uma sequência de hipóteses e consultas.”

<!-- deck-primary: Métrica e trace convergem para payment.request com aproximadamente 254 ms. -->
<!-- deck-engineering: Usar convergência de fontes para elevar confiança sem exagerar a causalidade. -->
<!-- deck-caution: Não há telemetria interna suficiente para declarar root cause externa verificada. -->
<!-- deck-question: Que evidência adicional provaria o mecanismo downstream? -->

## Slide 67 — HIPÓTESE ANTES DA TOOL

**Fala sugerida.** “Tool calling útil começa com uma hipótese e uma pergunta que reduz incerteza. ‘Checkout lento’ pode levar a payment, inventário, deploy ou saturação. Em vez de chamar todas as ferramentas, perguntamos: qual evidência diferenciaria essas alternativas? Métrica de dependência testa se o tempo aparece em payment. Lista de serviços evita consultar Jaeger com nome inventado. Traces testam se requests específicos concentram duração. Mudanças recentes verificam correlação temporal. Depois de cada observação, a hipótese deve ser mantida, enfraquecida ou revisada.”

**Exemplo além do slide.** Consultar CPU sem qualquer indício pode produzir um número interessante, mas pouco informativo. Tool call não é evidência útil apenas por retornar dados.

**Pergunte à turma.** “Qual consulta reduz mais incerteza entre payment e inventory?”

**Resposta que vale construir.** Métricas/traces específicos das duas dependências ou operações, comparados na mesma janela.

**Transição.** “O loop do agente operacionaliza esse ciclo, mas com limites explícitos.”

<!-- deck-primary: Hipótese define a evidência necessária; tool call deve reduzir incerteza e permitir revisão. -->
<!-- deck-engineering: Escolher consultas discriminativas em vez de coletar toda telemetria disponível. -->
<!-- deck-caution: Mais tool calls podem aumentar ruído, custo e viés de confirmação. -->
<!-- deck-question: Qual query diferencia duas hipóteses concorrentes? -->

## Slide 68 — TOOL CALLING SRE

**Fala sugerida.** “O modelo recebe mensagens e especificações de tools. Ele pode solicitar uma chamada; o código confere o nome na allowlist, executa e devolve o resultado como mensagem de tool. O ciclo tem no máximo seis passos e depois força uma finalização estruturada. Temperatura zero reduz variação; `think=false` evita depender de raciocínio oculto; o schema final exige evidências, causa provável, confiança, claims não suportados, opções de remediação e necessidade de humano. O modelo escolhe a consulta, mas nunca executa código arbitrário.”

**Exemplo além do slide.** Se o modelo pedir `restart_service`, `execute()` rejeita porque a capacidade não existe. A proteção real é ausência da tool, não uma frase no system prompt.

**Pergunte à turma.** “Onde está o limite contra loop infinito?”

**Resposta que vale construir.** `max_steps`, timeouts e finalização forçada; produção também precisaria de orçamento e cancelamento.

**Transição.** “Vamos abrir a allowlist e observar o que o agente realmente consegue fazer.”

<!-- deck-primary: O modelo escolhe tools; o código executa somente allowlist dentro de um loop limitado. -->
<!-- deck-engineering: Impor max_steps, timeouts e schema final para manter investigação auditável. -->
<!-- deck-caution: O modelo não deve receber execução arbitrária nem depender apenas de instrução para evitar mutações. -->
<!-- deck-question: Quais limites impedem loop, custo e ação fora do escopo? -->

## Slide 69 — TOOLS READ-ONLY

**Fala sugerida.** “As tools permitem consultar métricas, descobrir serviços, buscar traces, verificar health e mudanças. Não há restart, rollback, escala ou alteração de feature flag. Essa ausência é uma decisão de least privilege. O agente pode investigar automaticamente porque o blast radius das consultas é baixo. Descobrir serviços antes de buscar traces também evita assumir que o nome lógico `checkout` coincide com `service.name`. Uma tool pequena e específica é mais fácil de auditar que um shell genérico ou um cliente HTTP aberto.”

**Exemplo além do slide.** Dar `curl(url)` genérico permitiria ao modelo acessar destinos não previstos ou endpoints mutáveis. `query_metrics(query)` ainda precisa de limites, mas reduz muito a superfície.

**Pergunte à turma.** “Qual seria a primeira tool mutável que vocês adicionariam?”

**Resposta que vale construir.** Talvez nenhuma inicialmente; se necessária, preferir ação reversível, escopo estreito, dry-run e aprovação explícita.

**Transição.** “Além de limitar capacidade, precisamos registrar como ela foi usada.”

<!-- deck-primary: Tools read-only cobrem métricas, traces, health e mudanças sem capacidade de remediação. -->
<!-- deck-engineering: Aplicar least privilege na própria interface de tools, com descoberta antes de consulta. -->
<!-- deck-caution: Cliente HTTP ou shell genérico amplia capacidade muito além do necessário. -->
<!-- deck-question: Qual ação mutável, se alguma, seria segura sem aprovação? -->

## Slide 70 — REGISTRO DE TOOL CALLS

**Fala sugerida.** “Cada solicitação do assistant e cada resultado de tool entram na trajetória de mensagens. Isso permite reconstruir quais dados sustentaram a conclusão. É observabilidade do agente, diferente da observabilidade da aplicação. Em produção registraríamos tool, argumentos sanitizados, identidade, timestamp, duração, resultado resumido, erro e decisão posterior. O núcleo trunca resultados grandes para controlar contexto; truncamento também precisa ser visível, porque pode remover evidência relevante. Auditoria não é armazenar pensamento privado do modelo; é preservar ações e evidências observáveis.”

**Exemplo além do slide.** Se a conclusão cita um trace que nunca apareceu em tool result, podemos detectar unsupported claim. Sem trajetória, resta confiar na prosa final.

**Pergunte à turma.** “Que dados nunca deveriam entrar crus nesse log?”

**Resposta que vale construir.** Tokens, segredos, PII e payloads sensíveis; aplicar redaction e retenção adequada.

**Transição.** “Essa trajetória também prova que o agente não recebeu a resposta escondida no input.”

<!-- deck-primary: Trajetória registra tool calls e resultados para reconstruir a base da conclusão. -->
<!-- deck-engineering: Auditar ações observáveis com sanitização, duração, erro e truncamento explícito. -->
<!-- deck-caution: Auditoria sem redaction pode transformar observabilidade em vazamento de dados. -->
<!-- deck-question: O que precisa ser registrado e o que precisa ser removido? -->

## Slide 71 — INVESTIGAÇÃO SEM SCENARIO

**Fala sugerida.** “O `Incident` contém serviço lógico, sintoma e janela. Não contém `payment_latency`, root cause ou query correta. Isso evita data leakage: se o benchmark fornece a resposta no input, mede capacidade de repetir, não de investigar. O agente precisa descobrir que o serviço observado no Jaeger é `releaseguard`, consultar o sinal de dependência e juntar evidências. Esse cuidado vale para avaliações de agentes em geral. Fixtures e nomes de arquivo podem revelar ground truth sem que a equipe perceba.”

**Exemplo além do slide.** Um dataset com campo `scenario=database_timeout` torna irrelevante avaliar se o agente identificou banco como causa. Basta copiar a etiqueta.

**Pergunte à turma.** “Como validar o agente sem revelar a resposta e ainda manter avaliação objetiva?”

**Resposta que vale construir.** Injetar falha conhecida fora do input, registrar ground truth separadamente e avaliar consultas/evidências/conclusão.

**Transição.** “Mesmo chegando à hipótese correta, precisamos escolher palavras proporcionais ao grau de prova.”

<!-- deck-primary: O agente recebe apenas sintoma, serviço lógico e janela; ground truth fica fora do contexto. -->
<!-- deck-engineering: Avaliar descoberta e evidência contra falha injetada conhecida separadamente. -->
<!-- deck-caution: Nomes, campos e fixtures podem vazar a causa e invalidar o benchmark. -->
<!-- deck-question: Como testar investigação sem entregar a resposta no input? -->

## Slide 72 — CAUSA PROVÁVEL VS VERIFICADA

**Fala sugerida.** “Construam uma escada verbal. ‘Latência aumentou’ é observação. ‘O span de payment concentra o tempo’ é correlação localizada. ‘Payment provider é causa provável’ é inferência sustentada por métrica e trace. ‘O provedor estava saturado por limite X’ seria mecanismo verificado, mas não temos essa evidência. A linguagem precisa conservar incerteza. Isso não enfraquece o relatório; impede que uma hipótese vire fato por repetição. Uma boa investigação diz o que sabe, o que infere e o que falta.”

**Exemplo além do slide.** “May be causing” ou “likely associated with” são adequados aqui. “Root cause confirmed” não é.

**Pergunte à turma.** “Que experimento moveria causa provável para verificada?”

**Resposta que vale construir.** Observar mecanismo downstream, reproduzir sob controle ou eliminar a degradação ao remover a condição causal.

**Transição.** “E mesmo uma causa verificada não concede automaticamente autoridade para agir.”

<!-- deck-primary: Separar observação, correlação, causa provável e causa raiz verificada. -->
<!-- deck-engineering: Usar linguagem calibrada e explicitar qual evidência falta para fortalecer a conclusão. -->
<!-- deck-caution: O span mais lento não deve ser promovido automaticamente a root cause confirmada. -->
<!-- deck-question: Que evidência transformaria provável em verificada? -->

## Slide 73 — AUTONOMIA POR RISCO

**Fala sugerida.** “Autonomia não é uma propriedade binária do agente. Ela deve ser concedida por capability. Consultas read-only podem ser automáticas. Escritas reversíveis e de baixo blast radius podem exigir condições e rollback. Ações de infraestrutura, dados ou segurança pedem aprovação e, em alguns casos, nunca devem ser automatizadas pelo mesmo agente investigador. Três critérios ajudam: impacto máximo, reversibilidade e confiança baseada em evidência. Também devemos considerar frequência, segregação de funções e estado do sistema.”

**Exemplo além do slide.** Reiniciar um único pod stateless pode parecer reversível, mas durante incidente pode apagar evidência, deslocar carga ou ampliar outage. O contexto muda o risco.

**Pergunte à turma.** “Um restart de pod é sempre uma ação de baixo risco?”

**Resposta que vale construir.** Não. Depende de redundância, estado, tráfego, evidência, rollout e capacidade de reversão.

**Transição.** “O núcleo escolhe o limite conservador: investigar automaticamente e propor remediação para aprovação.”

<!-- deck-primary: Autonomia é concedida por capability conforme blast radius, reversibilidade e evidência. -->
<!-- deck-engineering: Automatizar leitura; condicionar escritas; exigir aprovação para ações de maior impacto. -->
<!-- deck-caution: Ação aparentemente reversível pode destruir evidência ou ampliar incidente. -->
<!-- deck-question: Em que condições um restart deixa de ser auto-safe? -->

## Slide 74 — HUMAN-IN-THE-LOOP

**Fala sugerida.** “HITL não significa apenas mostrar um botão ‘aprovar’. O humano precisa receber informação suficiente para tomar decisão: sintoma, escopo, evidências, hipótese, confiança não calibrada, riscos da ação, rollback e alternativas. Caso contrário, a aprovação vira rubber stamp. Também devemos separar `propose`, `approve` e `execute`, idealmente com identidades e logs diferentes. No núcleo, `requires_human=true` e ausência de tools mutáveis tornam essa fronteira explícita.”

**Exemplo além do slide.** Uma solicitação ‘reiniciar payment porque confidence=0.85’ é fraca. Uma solicitação com traces afetados, janela, impacto, ação limitada, verificação pós-ação e rollback é revisável.

**Pergunte à turma.** “Qual informação faria vocês rejeitarem uma aprovação imediatamente?”

**Resposta que vale construir.** Ausência de evidência, escopo indefinido, irreversibilidade não tratada ou falta de plano de verificação/rollback.

**Transição.** “Vamos ler a saída do agente como o pacote que alimentaria essa revisão.”

<!-- deck-primary: HITL é fronteira de autoridade com evidência suficiente, não um botão decorativo. -->
<!-- deck-engineering: Separar proposta, aprovação e execução com risco, rollback e verificação explícitos. -->
<!-- deck-caution: Revisão sem contexto produz rubber-stamping e falsa sensação de controle. -->
<!-- deck-question: Que dados mínimos tornam uma solicitação de ação aprovável? -->

## Slide 75 — SRE AGENT OUTPUT

**Fala sugerida.** “Leiam apenas os campos decisivos. `evidence` cita métrica e trace reais. `probable_cause` usa linguagem cautelosa. `confidence=0.85` é autorrelato do modelo, não probabilidade calibrada. `active_incident=true` alimenta a policy. `unsupported_claims=[]` declara que o modelo não reconheceu extrapolações — ainda precisamos validar isso contra a trajetória. `remediation_options` são propostas, e `requires_human=true` impede confundir recomendação com execução. A qualidade está menos na eloquência e mais na rastreabilidade entre cada afirmação e um dado.”

**Exemplo além do slide.** Se 100 relatórios com confidence 0.85 estiverem corretos apenas 60 vezes, o número não é calibrado. Calibração exige avaliação histórica, não aparência decimal.

**Pergunte à turma.** “0.85 significa 85% de chance real de a hipótese estar correta?”

**Resposta que vale construir.** Não necessariamente; é um sinal autorrelatado até ser calibrado por evals.

**Transição.** “Por isso a decisão de release usa fatos/policies, não o número de confiança.”

<!-- deck-primary: Output conecta evidência, causa provável, incidente ativo, remediação proposta e revisão humana. -->
<!-- deck-engineering: Verificar cada claim contra a trajetória e tratar confidence como não calibrada. -->
<!-- deck-caution: Um decimal de confiança não é probabilidade real sem avaliação empírica. -->
<!-- deck-question: O que seria necessário para calibrar confidence? -->

## Slide 76 — RELEASE POLICY

**Fala sugerida.** “A policy recebe artefatos dos três dias. Falha funcional crítica gera motivo de block. Regressão visual classificada ou governada como block também. Incidente ativo gera block. Se não há blocker, mas evidência visual pede revisão, o resultado é review. Caso contrário, pass. A precedência é explícita: block vence review. Reparem no que não aparece na condição: prosa do modelo, estética do report ou confidence 0.85. O código decide a partir de campos governados. A policy é simples para aula; produção precisaria de severidade, waivers, expiração, branch, SLO e ownership.”

**Exemplo além do slide.** Funcional PASS + visual REVIEW + incidente ativo resulta BLOCK, porque uma evidência bloqueante não é cancelada por duas evidências favoráveis.

**Pergunte à turma.** “Por que não calcular média dos três resultados?”

**Resposta que vale construir.** Riscos não são compensáveis dessa forma; um incidente crítico não deixa de existir porque outro teste passou.

**Transição.** “O relatório integrado mostra essa decisão e preserva os motivos.”

<!-- deck-primary: Policy combina evidências por regras e precedência explícitas, não por opinião do modelo. -->
<!-- deck-engineering: BLOCK vence REVIEW; incidente ativo e falha crítica não são compensados por outros passes. -->
<!-- deck-caution: A policy didática precisa ser expandida com contexto e governança antes da produção. -->
<!-- deck-question: Por que não tirar uma média das evidências dos três dias? -->

## Slide 77 — RELATÓRIO INTEGRADO

**Fala sugerida.** “O relatório reúne evidências independentes sem apagar sua origem. O funcional registra 200/409 e passa. O visual registra diferença localizada e pede review. O SRE registra incidente ativo e exige humano. A decisão final é BLOCK com motivo explícito. O valor do relatório é rastreabilidade: um reviewer consegue voltar ao `functional_report`, às imagens/métricas e à investigação. Ele também evita que o resumo final reinterprete silenciosamente os fatos. Artefatos estruturados permitem refazer a policy sem repetir toda a coleta.”

**Exemplo além do slide.** Se a organização mudar a regra visual de review para accept, pode recalcular o resultado a partir dos mesmos artefatos, preservando o histórico da observação original.

**Pergunte à turma.** “Por que o BLOCK atual não significa que o laboratório falhou?”

**Resposta que vale construir.** Porque o cenário injetado deixou evidência real de incidente; bloquear é o comportamento correto da policy.

**Transição.** “Vamos comparar explicitamente os três estados possíveis.”

<!-- deck-primary: Release report agrega evidências preservando origem, motivos e decisão reproduzível. -->
<!-- deck-engineering: Manter artefatos independentes para reprocessar política sem repetir coleta. -->
<!-- deck-caution: BLOCK esperado por falha injetada é sucesso da validação, não falha do ambiente. -->
<!-- deck-question: Por que o resultado final correto desta execução é BLOCK? -->

## Slide 78 — DECISÃO PASS/REVIEW/BLOCK

**Fala sugerida.** “PASS significa que nenhuma evidência acionou review ou block sob a policy atual. Não significa ausência absoluta de risco. REVIEW significa que o sistema detectou algo real, mas não possui contexto ou autoridade para decisão automática. BLOCK significa que uma regra impeditiva foi satisfeita. Esses estados devem vir acompanhados de razões e evidências, não apenas de cor. Waivers também precisam ser explícitos, temporários e vinculados a responsável; caso contrário, review vira pass informal.”

**Exemplo além do slide.** Um CTA deslocado pode receber review. Se o design owner aprova a mudança e gera nova baseline com rastreabilidade, execução futura pode passar. Incidente ativo não deveria receber waiver apenas porque o visual foi aprovado.

**Pergunte à turma.** “Que evidência permite converter REVIEW visual em ACCEPT?”

**Resposta que vale construir.** Confirmação de intenção, análise de impacto, aprovação autorizada e baseline/policy atualizada com histórico.

**Transição.** “Os grupos aplicarão esse raciocínio a incidentes com níveis diferentes de evidência.”

<!-- deck-primary: PASS, REVIEW e BLOCK expressam ausência de gatilho, ambiguidade governada e impedimento explícito. -->
<!-- deck-engineering: Sempre acompanhar estado com razões, artefatos e processo rastreável de waiver. -->
<!-- deck-caution: PASS não elimina risco e REVIEW não deve virar aprovação informal. -->
<!-- deck-question: O que transforma review visual em accept de forma auditável? -->

## Slide 79 — EXERCÍCIO MENTORADO DIA 3

**Fala sugerida.** “Comecem pelo sintoma, nunca pela causa. Escrevam pelo menos duas hipóteses, escolham a consulta que melhor as diferencia, registrem resultado e revisem a hipótese. Citem métricas e traces específicos. Se a telemetria for insuficiente, essa pode ser a conclusão correta, desde que mostrem o que tentaram e o que falta. Não executem mutações. Grupos de autonomia e release gate devem justificar fronteiras de ação; grupos de payment/inventory devem evitar confundir cenário conhecido pelo instrutor com evidência disponível ao agente.”

**Exemplo além do slide.** O grupo “ausência de mudanças” não deve concluir automaticamente que deploy não causou o incidente; deve dizer apenas que essa fonte não sustenta a hipótese de mudança recente.

**Pergunte à turma.** “Qual frase deve aparecer antes da primeira tool call?”

**Resposta que vale construir.** “Minha hipótese é ___; esta consulta pode fortalecê-la ou enfraquecê-la porque ___.”

**Transição.** “Antes de encerrar, generalizamos as lições num checklist de produção.”

<!-- deck-primary: Grupos investigam por sintoma, hipótese, tool, evidência, revisão, confiança e HITL. -->
<!-- deck-engineering: Registrar hipóteses concorrentes e consultas que possam refutá-las. -->
<!-- deck-caution: Não usar o nome do cenário como evidência nem executar qualquer mutação. -->
<!-- deck-question: Que frase deve justificar cada tool call? -->

## Slide 80 — CHECKLIST DE PRODUÇÃO

**Fala sugerida.** “Contratos estruturam entradas e saídas. Instrumentação fornece evidência relevante. Identidade consistente torna dados descobríveis. Tools estreitas aplicam menor privilégio. Limites de passos, tempo e custo contêm loops. Auditoria registra ações e resultados. Evals medem factualidade, seleção de tools, custo e calibração. HITL governa autoridade. Release policy transforma sinais em decisão reproduzível. Artefatos versionáveis preservam contexto. Cada item nasceu de uma falha concreta do laboratório: schema incompatível, fixture inventada, service name ausente, trace consultado com nome errado, payload multimodal incorreto ou report não persistido.”

**Exemplo além do slide.** Uma prova de conceito pode funcionar sem auditoria. Em produção, sem trajetória não há como explicar por que uma ação foi sugerida, investigar erro ou melhorar evals.

**Pergunte à turma.** “Qual item falta para o ambiente real da empresa de vocês?”

**Resposta que vale construir.** Respostas variarão: segurança de dados, tenancy, custos, compliance, rollback, ownership, incident command ou gestão de modelos.

**Transição.** “Fechamos voltando à tese que conecta os três dias.”

<!-- deck-primary: Produção exige contratos, instrumentação, identidade, least privilege, auditoria, evals, HITL e policy. -->
<!-- deck-engineering: Ligar cada controle a failure modes observados e ao contexto real da organização. -->
<!-- deck-caution: Checklist genérico não substitui threat modeling, SLO e governança específicos. -->
<!-- deck-question: Qual controle adicional o sistema real de vocês exigiria? -->

## Slide 81 — FECHAMENTO DA SEMANA

**Fala sugerida.** “A tese final é ‘evidência antes de autonomia’. No Dia 1, o modelo propôs um teste, mas contrato, policy, HTTP e oracle sustentaram o resultado. No Dia 2, o VLM descreveu uma mudança, mas captura, métricas, região e policy governaram a decisão. No Dia 3, o agente escolheu consultas e produziu causa provável, mas métricas, traces, least privilege e aprovação limitaram autoridade. IA aumenta a capacidade de produzir e interpretar sinais. Engenharia define o que conta como evidência, quem pode agir e como uma decisão será auditada. Se trocarmos Ollama, n8n ou Jaeger, essa arquitetura de confiança continua útil.”

**Exemplo além do slide.** O projeto não é valioso porque contém muitas ferramentas. Ele é valioso porque cada ferramenta possui fronteira clara e deixa um artefato que a próxima camada consegue verificar.

**Pergunte à turma.** “Qual parte levariam primeiro para produção?”

**Resposta que vale construir.** Começar pela parte read-only, bem instrumentada e com oracle/policy claros; ampliar autonomia somente após medir qualidade.

**Transição.** “Encerrar retomando: proposta pode ser probabilística; autoridade e evidência precisam ser projetadas.”

<!-- deck-primary: Evidência antes de autonomia conecta QA funcional, regressão visual e investigação SRE. -->
<!-- deck-engineering: Começar read-only, medir qualidade e ampliar capacidades somente com controles proporcionais. -->
<!-- deck-caution: Ferramentas mudam; fronteiras de contrato, evidência, policy e autoridade permanecem. -->
<!-- deck-question: Qual componente do ReleaseGuard está mais pronto para adoção real e por quê? -->
