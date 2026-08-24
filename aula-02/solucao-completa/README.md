# Solução completa — SupportOps Agent

Agente local com LangChain, Ollama e Qwen 3. Ele investiga tickets usando tools somente leitura, executa um loop agêntico e produz um diagnóstico Pydantic validado.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen3:4b
python -m supportops.doctor
```

## Executar

```bash
python -m supportops.main TCK-4821
```

Saída JSON pura:

```bash
python -m supportops.main TCK-4821 --json
```

Inspecionar apenas a primeira decisão de tool calling:

```bash
python -m supportops.probe_tool_call
```

Testar outro caso:

```bash
python -m supportops.main TCK-4822
```

## Testes determinísticos

```bash
pytest -q
```

Os testes não precisam do Ollama. O teste ponta a ponta exige o serviço local e o modelo baixado.

## Configuração

Variáveis opcionais:

```bash
export OLLAMA_MODEL=qwen3:8b
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_NUM_CTX=8192
export AGENT_MAX_GRAPH_STEPS=14
```

Cada execução salva uma trilha resumida em `runs/`.
