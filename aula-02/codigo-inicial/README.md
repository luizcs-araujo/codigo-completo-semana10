# Código inicial — SupportOps Agent

Starter usado no live coding da Aula 2. O backend simulado, os dados e o modelo de saída já estão prontos. Os pontos didáticos permanecem marcados com `TODO AULA`.

## Preparação

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen3:4b
python -m supportops.doctor
```

O Ollama precisa estar em execução. Em instalações desktop, normalmente ele inicia como serviço. Em Linux, pode ser necessário executar `ollama serve` em outro terminal.

## Primeiro contraste

```bash
python -m supportops.baseline TCK-4821
```

A baseline não possui tools e não tem como conhecer o ticket.

## Projeto a implementar

```bash
python -m supportops.main TCK-4821
```

A execução mostra uma linha do tempo com o raciocínio retornado pelo modelo,
chamadas e retornos de tools, diagnóstico final e uso agregado de tokens. O
Ollama fornece `eval_count` como total de tokens de saída, sem separar o
raciocínio; para fins didáticos, o projeto conta os tokens do trace visível por
meio dos logprobs e identifica essa métrica explicitamente na tela.

No estado inicial, esse comando interrompe nos `TODO AULA`. Siga o guia incremental.

## Testes que já devem passar

```bash
pytest -q
```
