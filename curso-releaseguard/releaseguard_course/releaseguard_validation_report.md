# ReleaseGuard local validation and remediation report

Validation date: 2026-08-17  
Validation host: macOS Darwin arm64, 24 GiB RAM  
Python: 3.12.13  
Docker / Compose: 29.3.1 / v5.1.1  
Ollama: 0.31.1  
Playwright: 1.62.0, managed Chromium 151.0.7922.34  
Text model: `qwen3:8b`  
Vision model: `qwen3-vl:8b`

## Executive result

All runbook gates passed after the remediations documented below. The final offline validator compiled all five course versions, ran 57 tests, and passed every smoke test. The live stack returned HTTP 200 for ReleaseGuard, n8n, Prometheus, and Jaeger.

The final integrated report intentionally returns `BLOCK` because the validation leaves a real injected payment-latency incident in its evidence. Independent policy checks returned `PASS` for healthy evidence, `REVIEW` for visual-regression evidence, and `BLOCK` for an active incident. This is the expected evidence-driven behavior, not a remaining product failure.

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| 0 - Environment | PASS after repair | Python 3.12.13; Docker and Compose available; Ollama models present; Playwright Chromium installed. |
| 1 - Offline suite | PASS | `7 + 10 + 11 + 13 + 16 = 57` tests passed; all compile and smoke checks passed; final validator printed `OFFLINE COURSE VALIDATION: PASS`. |
| 2 - Local infrastructure | PASS | n8n, Prometheus, and Jaeger containers running; all health/UI requests returned 200. |
| 3 - ReleaseGuard API/UI | PASS | `/health`, `/products`, `/metrics`, `/store`, `/store/checkout`, and `/docs` returned 200. |
| 4 - Deterministic QA | PASS | Real POST sequence returned 200 then expected 409; final report `passed: true`. |
| 5 - Ollama QA generation | PASS after repair | qwen3:8b produced Pydantic-valid, semantically validated plan using `/cart` and `/cart/{cart_id}/items`, concrete `sku-001`, quantity 4, and expected 409. |
| 6 - n8n workflow | PASS after repair | Import succeeded; Ollama, parser, Validation, HTTP execution, and Report nodes succeeded; final report observed 200 then 409 and `passed: true`. |
| 7 - Visual regression | PASS | Real Chromium captures created baseline/current/diff. Ratio `0.0114814453125`, SSIM `0.9869284082954217`, bbox `[285,237,567,297]`. |
| 8 - Visual AI | PASS after repair | qwen3-vl:8b returned structured triage identifying the visible button shift, citing image and metric evidence, recommendation `review`. |
| 9 - Operational fault | PASS | Normal payment `0.002638 s`; injected payment latency `0.257617 s`; dependency histogram exposed `payment_provider`. |
| 10 - Prometheus | PASS after repair | `releaseguard` target is `UP`; PromQL returned a real payment-provider count. |
| 11 - Jaeger | PASS after repair | Service `releaseguard`; four traces found; `payment.request` increased from `865 µs` to `253758 µs`; `checkout.create` present. |
| 12 - SRE data clients | PASS | Prometheus wrapper returned one result; Jaeger wrapper returned four traces. |
| 13 - SRE agent | PASS after repair | Agent used real metrics and traces without scenario input, cited the 0.2536 s dependency signal and 253758 µs span, proposed remediation, set `requires_human: true`, and marked an active incident. |
| 14 - Integrated report | PASS | Healthy -> PASS; visual regression -> REVIEW; active incident -> BLOCK. Real current evidence generated BLOCK for the injected incident. |

## Reproduced issues and fixes

1. **Broken bundled virtual environment**
   - Original failure: `complete/.venv` configuration pointed to Python 3.12 while its primary interpreter symlink resolved to Apple Python 3.9. It had no pip or dependencies, and `pytest==9.0.2` could not install on Python 3.9.
   - Fix: rebuilt the generated environment with Python 3.12.13 and installed pinned dependencies plus Playwright Chromium.
   - Retest: imports succeeded and the complete offline validator passed.

2. **Linux-only Chromium path in smoke tests**
   - Original failure: `02_dia2/scripts/smoke_dia2.py` failed with `executable doesn't exist at /usr/bin/chromium` on macOS. The same defect existed in Day 3 and complete.
   - Fix: use Playwright's managed Chromium by default in all three scripts.
   - Retest: all browser smoke tests passed with real FastAPI HTML.

3. **Compose port collisions and host portability**
   - Original failure: unrelated local containers already owned 5678, 4318, and 16686, preventing the ReleaseGuard stack from starting.
   - Fix: parameterized all host ports while preserving documented defaults; added `host.docker.internal:host-gateway` for Prometheus portability.
   - Retest: isolated validation used n8n 5679, Jaeger UI 16687, OTLP HTTP 4319, OTLP gRPC 4320, and Prometheus 9090.

4. **Missing ReleaseGuard Prometheus scrape target**
   - Original failure: the delivered Prometheus configuration scraped only Prometheus itself.
   - Fix: added the `releaseguard` job for `host.docker.internal:8000/metrics`.
   - Retest: target `UP`; PromQL returned live dependency data.

5. **Ollama-incompatible QA JSON Schema**
   - Original failure: Ollama returned 400 because the path regex `^/` was not fully anchored.
   - Fix: changed it to `^/.*$` in all QA-enabled increments.
   - Retest: Ollama accepted the schema and Pydantic validated the response.

6. **QA generation accepted semantically invalid plans**
   - Original failure: a schema-valid result selected the wrong oracle/status and omitted a required body.
   - Fix: documented the real 409 stock response in OpenAPI; included live product context; added deterministic temperature, semantic validation, and bounded correction retries.
   - Retest: generated executable 200/409 plan with concrete real fixture values.

7. **n8n workflow not importable on current n8n**
   - Original failure: `SQLITE_CONSTRAINT: NOT NULL constraint failed: workflow_entity.id`.
   - Fix: added a stable top-level workflow ID to every workflow copy.
   - Retest: import succeeded and the workflow was listed by ID.

8. **n8n parser and plan handoff defects**
   - Original failures: parser inferred a null-only request body; generated plan was wrapped in `output`; HTTP node posted the wrapper and received FastAPI 422; parser auto-fix lacked its model connection.
   - Fix: added a live product fetch, focused contract prompt, compatible schema example, parser repair model connection, deterministic `Validation` node, correct unwrapping, and explicit `Report` node.
   - Retest: complete workflow succeeded and its report passed both HTTP steps.

9. **Incorrect native Ollama vision message format**
   - Original failure: client sent OpenAI-style array content to `/api/chat`; Ollama returned `cannot unmarshal array ... content of type string`.
   - Fix: send native message text plus base64 `images`; bound context/output, suppress thinking, and retry only empty final content.
   - Retest: structured qwen3-vl triage passed with grounded visual evidence.

10. **Missing OpenTelemetry service resource**
    - Original failure: the tracer provider had no `service.name`, and Jaeger returned no identifiable ReleaseGuard service.
    - Fix: configure `Resource.create({'service.name': 'releaseguard'})` in Day 3 and complete.
    - Retest: Jaeger lists `releaseguard` and contains real checkout/payment spans with the injected latency.

11. **SRE agent queried incorrect telemetry and could not finish reliably**
    - Original failures: it assumed logical service `checkout` was the Jaeger service name, invented a metric query, misdiagnosed missing telemetry, exhausted its tool loop, and its result lacked the `active_incident` field required by release policy.
    - Fix: added Jaeger service discovery, concrete ReleaseGuard metric guidance, sanitized health evidence, bounded inference, forced finalization from accumulated evidence, and `active_incident` in the schema.
    - Retest: final result cites live payment metrics and trace duration, uses cautious probable-cause language, proposes rather than executes remediation, and requires human approval.

12. **Real functional artifact was not persisted**
    - Original failure: `qa.run_demo` printed the report but did not create the file consumed by `complete_report`.
    - Fix: persist `artifacts/day1/functional_report.json` in every QA-enabled increment.
    - Retest: integrated report includes the real 200/409 steps.

13. **Complete smoke test overwrote audit evidence**
    - Original failure: `scripts/smoke_complete.py` replaced real artifacts with synthetic fixtures.
    - Fix: added configurable artifact root and run smoke evidence in a temporary directory.
    - Retest: full validator passed without changing the real final audit report.

## Final evidence files

- `complete/artifacts/day1/functional_report.json`
- `complete/artifacts/visual/baseline.png`
- `complete/artifacts/visual/current.png`
- `complete/artifacts/visual/diff.png`
- `complete/artifacts/visual/metrics.json`
- `complete/artifacts/visual/vlm_triage.json`
- `complete/artifacts/sre/investigation_result.json`
- `complete/artifacts/release/release_report.json`
- `complete/artifacts/release/release_report.md`

## Non-blocking notes

- Another local project occupied the runbook's default n8n and Jaeger ports. ReleaseGuard was validated with the new port overrides; documented defaults remain unchanged for clean machines.
- The n8n container warns that Python is absent for its optional internal Python task runner. The workflow uses the registered JavaScript runner, so this did not affect execution.
- The current final release decision is intentionally BLOCK because the real payment-latency fault remains represented in the saved evidence. Resetting the scenario does not invalidate this audit artifact.

## Freeze recommendation

Approved for course-core freeze. All mandatory gates are green after remediation, and the saved BLOCK decision correctly reflects the deliberately injected operational incident.
