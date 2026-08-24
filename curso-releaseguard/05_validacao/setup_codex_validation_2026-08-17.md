# ReleaseGuard AI — relatório de setup do Codex

Data: 2026-08-17  
Host: macOS Darwin arm64  
Resultado: **PASS**

## Resumo

O pacote congelado foi verificado pelo checksum publicado e extraído em
`releaseguard_course/`. O ambiente Python 3.12 foi recriado, as dependências e o
Chromium gerenciado pelo Playwright foram instalados, e os serviços locais foram
iniciados nas portas padrão. Nenhum arquivo de código do núcleo congelado foi
alterado.

A validação offline terminou com `OFFLINE COURSE VALIDATION: PASS` e executou os
57 testes de referência. Todos os gates ao vivo também passaram. A decisão final
`BLOCK` é esperada: ela deriva do cenário de latência de pagamento injetado para
o exercício SRE, não de uma falha de instalação.

## Gates

| Etapa | Resultado | Comando/evidência |
| --- | --- | --- |
| 1. Sistema | PASS | `uname -a`: Darwin arm64. |
| 2. Python | PASS | `python3.12 --version`: Python 3.12.13. |
| 3. Núcleo | PASS | Checksum SHA-256 do ZIP: `abe1690e79c127ac221eb28fb8669f611fcc5cbdcca4c4006caa34e787018f32`; `requirements.txt`, `app/`, `qa/`, `visual/` e `sre/` presentes. |
| 4. Venv/dependências | PASS | `python3.12 -m venv .venv`; `pip install -r requirements.txt`; imports de FastAPI, HTTPX e Pydantic concluídos. |
| 5. Chromium | PASS | `python -m playwright install chromium`; executável existente em `~/Library/Caches/ms-playwright/chromium-1234/.../Google Chrome for Testing`. |
| 6. Ollama | PASS | Ollama 0.31.1; `qwen3:8b` e `qwen3-vl:8b` presentes em `ollama list`. |
| 7. Ambiente | PASS | `.env` criado a partir de `.env.example`; `/api/tags` do Ollama retornou JSON e HTTP 200. |
| 8. Docker | PASS | Docker 29.3.1; Compose v5.1.1. |
| 9. Infraestrutura | PASS | `docker compose -f infra/docker-compose.yml up -d`; n8n, Prometheus e Jaeger em estado `Up`. |
| 10. FastAPI | PASS | Uvicorn em `0.0.0.0:8000`; `/health` retornou HTTP 200 e `status=ok`. |
| 11. UI | PASS | `/store` e `/store/checkout` retornaram HTTP 200. |
| 12. Prometheus | PASS | `/-/healthy` retornou HTTP 200; target `releaseguard` retornou `up=1`. |
| 13. Jaeger | PASS | `/api/services` listou `releaseguard`; traces contêm `checkout.create` e `payment.request`. |
| 14. Validação offline | PASS | `complete/.venv/bin/python scripts/validate_course.py`: 7 + 10 + 11 + 13 + 16 = 57 testes; saída final `OFFLINE COURSE VALIDATION: PASS`. |
| 15. Dia 1 | PASS | `python -m qa.run_demo`: fluxo 200 → 409, `passed: true`, artefato funcional persistido. |
| 16. Plano com Ollama | PASS | `python -m qa.generate_plan`: plano JSON válido com `sku-001`, quantidade 4, rotas executáveis e oracle 409. |
| 17. Dia 2 | PASS | `python -m visual.guided_demo`: ratio `0.0114814453125`, SSIM `0.9869284082954217`, bbox `[285, 237, 567, 297]`. |
| 18. VLM | PASS | `qwen3-vl:8b` retornou `VisualTriage` válido, mudança `button_shift`, evidência visual fundamentada e recomendação `review`. |
| 19. Dia 3 | PASS | `python -m scripts.smoke_dia3`: latência real de aproximadamente 0.259 s e métrica `payment_provider`. |
| 20. Clientes SRE | PASS | Prometheus retornou soma `0.25508879200788215`; Jaeger retornou spans `payment.request` de até 255537 us. |
| 21. SRE Agent | PASS | Consultou métricas e traces reais; causa provável cautelosa, confiança 0.85, `active_incident=true`, `requires_human=true`, sem claims não suportados. |
| 22. Report integrado | PASS | `python -m complete_report`; JSON e Markdown gerados; decisão `BLOCK` derivada do incidente injetado ativo. |
| 23. Auditoria de artefatos | PASS | Todos os nove artefatos obrigatórios existem, não estão vazios e passaram validação estrutural. |

## Portas e skips

- Portas alternativas: nenhuma.
- Portas usadas: FastAPI 8000, n8n 5678, Prometheus 9090, Jaeger UI 16686,
  OTLP gRPC 4317, OTLP HTTP 4318 e Ollama 11434.
- Skips: nenhum.
- Observação de execução: a primeira tentativa do validador offline, dentro do
  sandbox sem acesso a sockets locais, não conseguiu iniciar o servidor temporário
  do smoke test do Dia 2. A repetição do mesmo comando com acesso ao host passou
  integralmente; isso foi uma restrição do executor, não uma falha do projeto.

## Estado deixado em execução

- FastAPI ReleaseGuard: ativo na porta 8000.
- n8n, Prometheus e Jaeger: ativos via Docker Compose.
- Cenário da API: `payment_latency`, preservado para manter a evidência SRE e a
  decisão integrada esperada em `BLOCK`.
