# Validação de sincronização — ReleaseGuard AI

## Núcleo congelado

Artefato oficial usado como fonte única de verdade:

- `nucleo_releaseguard_validado.zip`
- SHA-256: `abe1690e79c127ac221eb28fb8669f611fcc5cbdcca4c4006caa34e787018f32`

Este SHA coincide com `releaseguard_course_validated_2026-08-17.zip` fornecido pelo usuário.

## Escopo desta sincronização

O núcleo técnico não foi alterado. A sincronização final atualizou a camada pedagógica:

- `aulas_3_dias.pptx`
- guias de setup, live coding, n8n, exercícios mentorados e condução teórica
- pacote final com projeto base/completo derivados do núcleo congelado

## Evidência técnica usada

A validação do núcleo está documentada em:

- `releaseguard_validation_report.md`

O relatório registra todos os gates live aprovados após reparos locais:

- 57 testes offline passando
- FastAPI/UI reais
- n8n importado e executado
- Ollama text live
- Playwright real
- Qwen3-VL live
- Prometheus target `releaseguard` UP
- Jaeger com `service.name=releaseguard`
- SRE Agent sem receber `scenario=payment_latency`
- relatório integrado com `PASS`, `REVIEW` e `BLOCK`

## Validação dos guias contra o núcleo

Checklist estático aplicado:

- [x] Todos os guias esperados estão presentes.
- [x] Guias usam `releaseguard_course_validated_2026-08-17.zip` como núcleo congelado.
- [x] Guias incorporam correções validadas: Chromium gerenciado pelo Playwright, `service.name=releaseguard`, scrape Prometheus `releaseguard`, n8n importável, schema/semantic validation do Ollama.
- [x] Guias não orientam uso de `/usr/bin/chromium` como suposição. As ocorrências existentes aparecem como alerta de não usar esse caminho no macOS.
- [x] Guias de live coding incluem blocos temporizados, comandos, checkpoints, troubleshooting e ganchos.
- [x] Guia n8n documenta o fluxo validado: Basic LLM Chain + Ollama Chat Model + Structured Output Parser + Validation + `/qa/execute-plan`.
- [x] Guias mentorados possuem ponto inicial, arquivos permitidos/proibidos, evidências, comandos, critérios e extensões.

## Validação dos slides contra os guias

- [x] Deck contém 81 slides.
- [x] Os 81 títulos do deck correspondem aos 81 slides descritos em `04_guia_teorico_slide_a_slide.md`.
- [x] Slides referenciam os artefatos reais do núcleo congelado:
  - `functional_report.json`
  - `baseline.png`
  - `current.png`
  - `diff.png`
  - `metrics.json`
  - `vlm_triage.json`
  - `investigation_result.json`
  - `release_report.json`
- [x] Slides incluem evidências validadas:
  - `pixel_change_ratio = 0.0114814453125`
  - `SSIM = 0.9869284082954217`
  - `bbox = [285, 237, 567, 297]`
  - `payment.request = 253758 µs`
  - decisão final `BLOCK`
- [x] Slides foram renderizados localmente para PNG.
- [x] Uma montagem visual foi gerada em `deck_montage.png` para inspeção.
- [x] O gerador de slides foi executado com `warnIfSlideHasOverlaps` e `warnIfSlideElementsOutOfBounds` sem warnings finais.

## Validação visual dos slides

A primeira geração do deck sincronizado identificou problemas de legibilidade em snippets muito densos. A versão final reduziu os snippets para trechos reais menores do núcleo congelado e ampliou a legibilidade visual.

A versão entregue utiliza:

- cards maiores para evidências críticas;
- snippets curtos extraídos do código real;
- screenshots reais de baseline/current/diff;
- tabelas desenhadas manualmente, evitando problemas de renderização;
- tipografia maior nos trechos conceituais;
- código apenas quando necessário para sustentar uma ideia técnica.

## Limitação honesta desta validação

Neste runtime, não há Docker/Ollama ativos para reexecutar os gates live. A validação live considerada é a do relatório enviado no núcleo congelado. A sincronização atual valida aderência de guias e slides a esse núcleo e às evidências registradas.

## Veredito

A camada pedagógica agora está sincronizada com o núcleo congelado e pode ser empacotada como a versão final dos materiais da semana.
