# ReleaseGuard — 00_base_clean

Baseline funcional preparada para iniciar o exercício mentorado do Dia 3. Ela já
contém a infraestrutura que os alunos **não** devem construir durante o exercício:
observabilidade, tools SRE somente leitura, agente SRE e release policy. O trabalho
dos grupos fica isolado em `student_work/day3/<grupo>/`.

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

## Dia 3 — exercício mentorado

Esta cópia está preparada com observabilidade, tools SRE read-only, agente e
release policy. Antes da aula, consulte [`DAY3_START_READINESS.md`](DAY3_START_READINESS.md)
para subir a infraestrutura e executar os checkpoints.
