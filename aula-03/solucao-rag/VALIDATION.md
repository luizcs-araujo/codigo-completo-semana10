# Relatório de validação — Aula 3

Data da validação: 16/07/2026

## Ambiente usado

- Python 3.13.5
- langchain 1.3.14
- langchain-ollama 1.1.0
- langgraph 1.2.9
- langchain-text-splitters 1.1.2
- pydantic 2.13.4
- numpy 2.5.1
- pytest 9.1.1

## Validações executadas

```bash
python -m compileall -q .
RAG_EMBEDDING_BACKEND=hash pytest -q
```

Resultado:

```text
11 passed
```

Os testes cobrem:

- parsing e validação de metadata dos documentos;
- chunking por headings;
- reprodução garantida da recuperação de documento obsoleto;
- exclusão de documentos obsoletos e de ambiente incorreto;
- recuperação do runbook atual por código de erro e intenção;
- recusa por evidência insuficiente;
- backend mockado expandido;
- circuit breaker;
- schema Pydantic;
- execução ponta a ponta do agente LangChain com model mockado, tools reais, RAG real e structured output.

## Demonstrações executadas

```bash
RAG_EMBEDDING_BACKEND=hash python -m supportops.demo_broken
RAG_EMBEDDING_BACKEND=hash python -m supportops.demo_fixed
```

A primeira demonstração recuperou como resultado principal o runbook `v1.0` obsoleto e repetiu a mesma busca três vezes. A segunda recuperou apenas fontes atuais de `prod` e marcou a evidência como suficiente.

## Limite desta validação

O container de validação não possui um serviço Ollama ativo. Por isso, a inferência real com `qwen3:4b` e os embeddings reais com `qwen3-embedding:0.6b` não foram executados aqui. A integração foi validada por:

1. imports e construção das classes atuais `ChatOllama` e `OllamaEmbeddings`;
2. construção e execução do `create_agent` atual;
3. agente ponta a ponta com modelo roteirizado compatível com tool calling;
4. tool calls, execução de tools, RAG e `ToolStrategy` reais;
5. `doctor.py`, que verifica Ollama e os dois modelos antes da aula.

Na máquina da aula, execute:

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
python -m supportops.doctor
python -m supportops.main TCK-4821
```
