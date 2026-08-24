# ReleaseGuard — 00_base_clean

Baseline funcional para a semana. Ainda não contém QA com IA, regressão visual automatizada nem SRE agentic.

## Rodar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Abra `http://localhost:8000/store` e `http://localhost:8000/docs`.

## Validar
```bash
python -m compileall -q .
pytest -q
python -m scripts.smoke_base
```

## Dia 1
```bash
python -m qa.run_demo
# live Ollama (API precisa estar rodando)
python -m qa.generate_plan
```
Workflow n8n: `n8n/qa_test_generator.json`. Configure a credencial Ollama após importar.

## Dia 2
Inicie a API e rode:
```bash
python -m visual.guided_demo --chromium /usr/bin/chromium
```
Artefatos reais ficam em `artifacts/visual/`.
