# Dia 2 — Exercício mentorado

## Objetivo comum

Projetar uma política de regressão visual adequada a um tipo de mudança, usando browser real, artefatos visuais e justificativa técnica.

## Ponto inicial

```text
releaseguard_course/02_dia2
```

ou `complete/`.

## Não modificar

```text
visual/compare.py
visual/vlm_triage.py
app/state/store.py
```

O grupo pode criar scripts próprios em:

```text
student_work/day2/<grupo>/
```

Pode utilizar os cenários existentes e capturar a UI.

---

# Entregas

1. baseline;
2. current;
3. diff;
4. metrics JSON;
5. política proposta;
6. justificativa de false positive/negative;
7. se aplicável, triagem VLM;
8. apresentação de 3 minutos.

---

# Casos

## Grupo A — CTA deslocado

Use:

```text
visual_checkout_shift
```

Questão: uma mudança pequena em pixels pode ser relevante por estar no CTA?

## Grupo B — CTA desaparecido

Use:

```text
visual_missing_cta
```

Questão: como a política deveria tratar pequena área alterada com impacto crítico?

## Grupo C — Conteúdo dinâmico

Use `dynamic_order_timestamp` se o estado visual do núcleo expuser esse conteúdo no fluxo escolhido; caso não apareça na tela utilizada, use o conceito para desenhar uma máscara hipotética sem alterar o núcleo.

Questão: o que deve ser ignorado e o que deve permanecer comparável?

## Grupo D — Mudança de cor

Não altere o núcleo. Crie cópia local de screenshot e aplique alteração de cor apenas no artefato do exercício.

Questão: pixel diff acusa muito; relevância pode ser baixa. Como justificar?

## Grupo E — Viewport diferente

Capture a mesma página em duas dimensões diferentes em script do grupo.

Questão: isso é regressão ou baseline errado?

## Grupo F — Fonte/rasterização

Compare captura local em configuração de browser/scale diferente.

Questão: que controles de ambiente reduzem ruído?

## Grupo G — Região crítica

Use o CTA e proponha uma política regional: threshold global versus região crítica.

Questão: qual informação a bbox oferece para esse design?

## Grupo H — VLM disagreement

Rode o VLM mais de uma vez somente se a configuração de aula permitir e compare a interpretação com a regra determinística.

Questão: o que fazer quando VLM e threshold entram em conflito?

---

# Comandos base

```bash
CHROMIUM=$(python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
)
```

Reset:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

Cenário:

```bash
curl -X POST http://localhost:8000/lab/scenarios/visual_checkout_shift/activate
```

---

# Evidências a apresentar

Tabela mínima:

| Evidência | Resultado |
|---|---|
| pixel ratio | |
| SSIM | |
| bbox | |
| mudança visível | |
| política | accept/review/block |
| justificativa | |

---

# Critérios

| Critério | Peso |
|---|---:|
| Captura reproduzível | 20% |
| Métricas interpretadas corretamente | 20% |
| Política alinhada ao risco | 25% |
| False positive/negative considerados | 15% |
| Evidência visual clara | 10% |
| Explicação técnica | 10% |

---

# Perguntas

1. O score global foi suficiente?
2. Qual região é operacionalmente importante?
3. O que o VLM adiciona que SSIM não adiciona?
4. O que o VLM não deveria decidir?
5. Como evitar baseline pollution no seu caso?

