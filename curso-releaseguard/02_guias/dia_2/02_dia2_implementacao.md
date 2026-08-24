# Dia 2 — Guia de implementação ao vivo

## Tema

**Regressão visual real + métricas perceptuais + triagem multimodal**

## Resultado após 40 minutos

```text
checkout real
→ baseline
→ fault injection
→ current
→ pixel diff
→ bounding box
→ SSIM
→ diff.png
→ qwen3-vl
→ VisualTriage
```

---

# Preparação

FastAPI rodando em `8000`.

Descubra Chromium antes da aula:

```bash
CHROMIUM=$(python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium.executable_path)
PY
)
echo "$CHROMIUM"
```

Abra:

```text
http://localhost:8000/store/checkout
```

Reset:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

---

# 0–5 min — Mostrar que a UI é real

## Problema

Queremos detectar mudança visual sem desenhar imagens sintéticas.

## Arquivo

```text
app/web/templates/checkout.html
```

## Código a apontar

```html
<a class="cta" href="#pay">Finalizar compra</a>
```

E o cenário:

```html
{% if scenario=='visual_checkout_shift' %}margin-left:120px;{% endif %}
```

## O que explicar

- O browser renderiza HTML real da aplicação.
- O cenário muda CSS de produção simulada.
- A mudança não está embutida no algoritmo de comparação.

## Demonstração

Com cenário normal, abra `/store/checkout`.

Depois, sem ainda medir:

```bash
curl -X POST http://localhost:8000/lab/scenarios/visual_checkout_shift/activate
```

Atualize o navegador.

Volte ao normal:

```bash
curl -X POST http://localhost:8000/lab/scenarios/reset
```

## Checkpoint

A turma viu o botão realmente se deslocar.

## Gancho

> “Se conseguimos enxergar a mudança, podemos tentar automatizar a comparação. O primeiro problema é garantir que baseline e current sejam capturados de forma reproduzível.”

---

# 5–10 min — Playwright como câmera reproduzível

## Arquivo

```text
visual/capture.py
```

## Código exato

```python
def capture(url:str, output:Path, executable_path:str|None=None)->Path:
    output.parent.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=executable_path)
        page=browser.new_page(viewport={'width':1280,'height':800},device_scale_factor=1)
        page.goto(url,wait_until='networkidle')
        page.screenshot(path=str(output),full_page=True)
        browser.close()
    return output
```

## O que explicar

A comparação visual só faz sentido se controlarmos pelo menos:

- browser engine;
- viewport;
- device scale;
- estado da página;
- momento da captura.

Aqui a captura usa `1280×800`, `device_scale_factor=1`, `networkidle`.

## Demonstração

Mostre o path do Chromium:

```bash
echo "$CHROMIUM"
```

Não use `/usr/bin/chromium` como suposição.

## Gancho

> “Agora vamos transformar o estado saudável em um artefato chamado baseline.”

---

# 10–15 min — Capturar baseline e current

## Arquivo

```text
visual/guided_demo.py
```

## Fluxo existente

```python
httpx.post(args.base_url+'/lab/scenarios/reset').raise_for_status()
capture(args.base_url+'/store/checkout',out/'baseline.png',args.chromium)
httpx.post(args.base_url+'/lab/scenarios/visual_checkout_shift/activate').raise_for_status()
capture(args.base_url+'/store/checkout',out/'current.png',args.chromium)
```

## Comando

```bash
python -m visual.guided_demo \
  --base-url http://127.0.0.1:8000 \
  --chromium "$CHROMIUM"
```

## Demonstração

Abra os arquivos:

```text
artifacts/visual/baseline.png
artifacts/visual/current.png
```

No macOS:

```bash
open artifacts/visual/baseline.png
open artifacts/visual/current.png
```

## Checkpoint

Baseline com CTA na posição original; current com CTA deslocado.

## Caso não funcione

- confira Chromium path;
- confira `/store/checkout`;
- confira se o cenário reset funciona;
- confira permissão de escrita em `artifacts/visual`.

## Gancho

> “Agora temos duas imagens. A pergunta mais ingênua é: quantos pixels mudaram?”

---

# 15–20 min — Pixel diff e bounding box

## Arquivo

```text
visual/compare.py
```

## Código

```python
aa=np.asarray(a)
bb=np.asarray(b)
changed=np.any(aa!=bb,axis=2)
pixel_ratio=float(changed.mean())
...
diff=ImageChops.difference(a,b)
bbox=diff.getbbox()
```

## O que explicar

### Pixel ratio

```text
número de pixels alterados / total de pixels
```

Ele mede extensão, não importância.

### Bounding box

`getbbox()` retorna o retângulo mínimo contendo todas as diferenças.

Isso localiza a mudança, mas não sabe o que existe naquela região.

## Output validado

```text
pixel_change_ratio = 0.0114814453125
bbox = [285, 237, 567, 297]
```

Interprete em voz alta:

- cerca de 1,15% dos pixels mudaram;
- mudança concentrada em uma região específica.

## Checkpoint

`bbox` não nula e `pixel_change_ratio > 0`.

## Gancho

> “Pixel diff é muito sensível. Uma pequena mudança de renderização pode contar milhares de pixels. Precisamos de uma medida que considere estrutura.”

---

# 20–25 min — SSIM

## Arquivo

```text
visual/compare.py
```

## Código real

```python
gray_a=np.asarray(a.convert('L'))
gray_b=np.asarray(b.convert('L'))
score, ssim_map=structural_similarity(
    gray_a,gray_b,data_range=255,full=True
)
```

## O que explicar

SSIM compara janelas locais e combina três ideias:

- luminância;
- contraste;
- estrutura.

Forma canônica intuitiva:

```text
SSIM(x,y) = l(x,y) · c(x,y) · s(x,y)
```

Uma forma comum combina médias, variâncias e covariância com constantes de estabilização `C1` e `C2`.

Ponto didático: o score é agregado sobre a imagem; ele não é “probabilidade de bug”.

## Valor validado

```text
SSIM = 0.9869284082954217
```

Pergunte:

> “98,69% de similaridade deveria passar?”

Não responda imediatamente.

## Checkpoint

Turma percebe que score alto e bbox localizada coexistem.

## Gancho

> “É por isso que uma política visual não pode depender de um único número global. Vamos transformar a diferença em um artefato inspecionável.”

---

# 25–30 min — Diff como evidência visual

## Código

```python
diff=ImageChops.difference(a,b)
ImageEnhance.Contrast(diff).enhance(4).save(diff_path)
```

## Demonstração

```bash
open artifacts/visual/diff.png
```

Mostre as três imagens lado a lado, se possível.

## O que explicar

`diff.png` não é apenas input para algoritmo. É artefato de comunicação entre QA, dev e designer.

Ele ajuda a responder:

```text
onde mudou?
quanto mudou?
parece intencional?
```

Mas ainda não responde:

```text
isso quebra o negócio?
```

## Gancho

> “Até aqui tudo foi determinístico. Agora podemos usar um VLM para interpretar a região sem dar a ele autoridade para decidir sozinho o release.”

---

# 30–35 min — Chamar o Qwen3-VL

## Arquivo

```text
visual/vlm_triage.py
```

## Schema

```python
class VisualTriage(BaseModel):
    change_type: str
    severity: Literal['low','medium','high']
    affected_region: str
    evidence: list[str]
    recommendation: Literal['accept','review','block']
```

## Prompt real

```python
prompt='/no_think\nCompare images in order: baseline, current, diff. Return JSON. Evidence must cite the visible button shift and the metrics. Do not infer functional correctness. Metrics: '+json.dumps(metrics)
```

## O que explicar

- As três imagens são enviadas em base64 no formato nativo do Ollama.
- `format` recebe o JSON Schema.
- `temperature=0` reduz variação.
- O prompt proíbe inferir correção funcional.
- `recommendation` é triagem, não release gate final.

## Comando live

```bash
python - <<'PY'
import json
from pathlib import Path
from visual.vlm_triage import triage
r=Path('artifacts/visual')
m=json.loads((r/'metrics.json').read_text())
result=triage(r/'baseline.png',r/'current.png',r/'diff.png',m)
print(result.model_dump_json(indent=2))
(r/'vlm_triage.json').write_text(result.model_dump_json(indent=2))
PY
```

## Checkpoint

Structured output válido.

## Caso não funcione

- `ollama list`;
- `qwen3-vl:8b` presente;
- não tente converter payload para formato OpenAI; o núcleo usa `content` string + `images`.

## Gancho

> “Agora temos uma interpretação semântica. Vamos confrontá-la com as métricas e decidir qual responsabilidade permanece humana/política.”

---

# 35–40 min — Comparar evidências e fechar a arquitetura

## Artefato validado

```text
artifacts/visual/vlm_triage.json
```

Referência:

```json
{
  "change_type": "button_shift",
  "severity": "low",
  "affected_region": "[285, 237, 567, 297]",
  "recommendation": "review"
}
```

## O que explicar

Construa no quadro:

```text
pixel ratio → extensão
bbox        → localização
SSIM        → similaridade estrutural global
VLM         → interpretação semântica
policy      → decisão operacional
```

A recomendação `review` é interessante porque o modelo reconheceu pequena mudança visual, mas não concluiu “bug funcional”.

## Checkpoint final

O aluno consegue explicar por que:

```text
SSIM alto ≠ página correta
VLM viu mudança ≠ release deve bloquear
```

## Gancho para teoria

> “Agora vamos formalizar visual regression, baseline management, false positives, baseline pollution e políticas por região.”

