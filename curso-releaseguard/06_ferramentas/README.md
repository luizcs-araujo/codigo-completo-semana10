# Ferramentas

O script [`revisar_deck.py`](revisar_deck.py) reproduz a versão revisada do PPTX a partir da fonte preservada e do guia slide a slide.

```bash
python3 06_ferramentas/revisar_deck.py \
  01_apresentacao/fontes/aulas_3_dias_template_SCTEC_CORRIGIDO.pptx \
  02_guias/apoio/04_guia_teorico_slide_a_slide.md \
  01_apresentacao/aulas_3_dias_SCTEC_REVISADO.pptx
```

Requisito: `python-pptx`.

## Atividade avaliativa

O script [`padronizar_atividade.py`](padronizar_atividade.py) separa o enunciado de cada questão em **Contextualização:** e **Comando:**, preservando alternativas, gabaritos, feedbacks e o restante do template.

```bash
python3 06_ferramentas/padronizar_atividade.py \
  03_atividades/fontes/atividades_avaliativas_original.docx \
  03_atividades/atividades_avaliativas.docx
```

Requisito: `lxml`.
