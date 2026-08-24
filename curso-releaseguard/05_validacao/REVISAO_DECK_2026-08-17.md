# Revisão do deck — 17/08/2026

## Escopo

Fonte revisada: `01_apresentacao/fontes/aulas_3_dias_template_SCTEC_CORRIGIDO.pptx`.

Saída: `01_apresentacao/aulas_3_dias_SCTEC_REVISADO.pptx`.

A revisão cruzou:

- guia geral dos três dias;
- guias de implementação ao vivo dos Dias 1, 2 e 3;
- guia n8n;
- guia teórico slide a slide;
- guia teórico de condução do Dia 3;
- exercícios mentorados dos três dias;
- artefatos reais do núcleo congelado.

## Problemas encontrados

1. Referência inexistente na capa: `releaseguard_course_validated_2026-08-17.zip`.
2. Dois números de página sobrepostos em cada slide.
3. Mais de vinte grupos de slides com conteúdo visível idêntico apesar de objetivos pedagógicos diferentes.
4. Slides do Dia 1 citavam “cupom” e “idempotência”, casos ausentes do exercício oficial.
5. Slides de exercício/rubrica dos Dias 2 e 3 repetiam tabelas genéricas ou conteúdo de outro slide.
6. RED/USE, SLI/SLO/error budget, tool calling, HITL e release policy apareciam em slides diferentes com o mesmo bloco, sem desenvolver o conceito do título.
7. As notas do apresentador apenas apontavam para um arquivo e não traziam a condução necessária.

## Correções aplicadas

- Referência da capa corrigida para `nucleo_releaseguard_validado.zip`.
- Numeração duplicada removida nos 81 slides.
- 43 slides reconstruídos com conteúdo específico: ideia central, decisão de engenharia, limite/cuidado e pergunta à turma.
- Casos e rubricas dos exercícios alinhados aos oito grupos reais de cada dia.
- Slides de código, screenshots e evidências reais preservados quando já estavam corretos.
- Todos os 81 slides receberam nas notas o conteúdo completo de sua seção no guia, mais as fontes complementares do respectivo dia.
- Originais preservados em `01_apresentacao/fontes/`.
- Script de geração incluído em `06_ferramentas/revisar_deck.py`.

## Validações executadas

- 81 slides presentes no PPTX final.
- 81 notas do apresentador preenchidas.
- zero referências ao ZIP inexistente.
- zero slides com numeração duplicada.
- integridade ZIP/XML do PPTX aprovada.
- renderização dos 81 slides no Keynote aprovada.
- montagem final gerada em `01_apresentacao/deck_revisado_montage.png` e inspecionada.

## Decisão

Deck revisado apto para uso em aula. O núcleo técnico permaneceu inalterado.
