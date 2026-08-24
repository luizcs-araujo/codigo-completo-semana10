#!/usr/bin/env python3
"""Padroniza os enunciados da atividade avaliativa sem alterar alternativas.

Cada questão passa a usar:

Contextualização: ...

Comando: ...
"""

from __future__ import annotations

import argparse
import copy
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
Q = etree.QName


QUESTIONS = {
    1: (
        "Uma equipe deseja usar IA para gerar testes de API a partir de descrições em linguagem natural. "
        "O primeiro teste criado valida que um produto sem estoque não pode ser adicionado ao carrinho. "
        "O time quer evitar que o modelo invente endpoints ou resultados esperados.",
        "Assinale a alternativa que apresenta a melhor estratégia para implementar esse fluxo.",
    ),
    2: (
        "Durante a construção de um workflow low-code para QA, um agente gera steps HTTP em JSON. "
        "A equipe percebe que o modelo às vezes sugere caminhos administrativos que não fazem parte do escopo do teste.",
        "Assinale a alternativa que apresenta a ação mais adequada para limitar a execução ao escopo autorizado.",
    ),
    3: (
        "Uma regressão visual apresenta SSIM alto e baixa porcentagem de pixels alterados, mas a região alterada contém o botão principal de finalizar compra.",
        "Assinale a alternativa que apresenta a decisão tecnicamente mais adequada para esse resultado.",
    ),
    4: (
        "Um time usa Visual AI para classificar diffs de interface. O modelo recebe baseline, imagem atual, diff e métricas.",
        "Assinale a alternativa que descreve o papel mais adequado desse modelo para reduzir o risco operacional.",
    ),
    5: (
        "Uma equipe precisa testar uma tela com datas, IDs de pedido e uma lista de produtos que muda com frequência.",
        "Assinale a alternativa que apresenta a melhor abordagem para configurar a regressão visual dessa tela.",
    ),
    6: (
        "Um alerta indica aumento de latência no checkout. Um assistente SRE recebe apenas o sintoma e pode consultar métricas, traces e logs.",
        "Assinale a alternativa que apresenta a melhor primeira linha de investigação.",
    ),
    7: (
        "Durante uma investigação, métricas mostram que checkout e payment estão lentos no mesmo intervalo. "
        "Um trace de requisição lenta mostra que o span de payment consome quase todo o tempo total.",
        "Assinale a alternativa que apresenta a conclusão mais apropriada para as evidências disponíveis.",
    ),
    8: (
        "Um assistente SRE propõe reiniciar um serviço de pagamento em produção após detectar alta latência.",
        "Assinale a alternativa que apresenta a política de autonomia mais adequada para essa ação.",
    ),
    9: (
        "Ao avaliar um assistente SRE, a equipe quer ir além de verificar se a resposta final parece convincente.",
        "Assinale a alternativa que apresenta o conjunto de métricas mais adequado para essa avaliação.",
    ),
    10: (
        "Uma equipe precisa integrar evidências de QA funcional, regressão visual e investigação SRE em uma decisão de release.",
        "Assinale a alternativa que apresenta a melhor síntese arquitetural para essa integração.",
    ),
}


def paragraph_text(paragraph) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS)).strip()


def base_run_properties(paragraph):
    run = paragraph.find("w:r", namespaces=NS)
    if run is None:
        return None
    props = run.find("w:rPr", namespaces=NS)
    return copy.deepcopy(props) if props is not None else None


def make_run(text: str, run_props, *, bold: bool = False):
    run = etree.Element(Q(W_NS, "r"))
    props = copy.deepcopy(run_props) if run_props is not None else etree.Element(Q(W_NS, "rPr"))
    if bold and props.find("w:b", namespaces=NS) is None:
        props.append(etree.Element(Q(W_NS, "b")))
    run.append(props)
    node = etree.SubElement(run, Q(W_NS, "t"))
    node.set(Q("http://www.w3.org/XML/1998/namespace", "space"), "preserve")
    node.text = text
    return run


def make_paragraph(source, label: Optional[str] = None, text: Optional[str] = None):
    paragraph = etree.Element(Q(W_NS, "p"), nsmap=source.nsmap)
    props = source.find("w:pPr", namespaces=NS)
    if props is not None:
        paragraph.append(copy.deepcopy(props))
    if label is not None and text is not None:
        run_props = base_run_properties(source)
        paragraph.append(make_run(label, run_props, bold=True))
        paragraph.append(make_run(" " + text, run_props))
    return paragraph


def rewrite_document(xml: bytes) -> bytes:
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(xml, parser)
    # Inclui parágrafos dentro das tabelas usadas pelo template da atividade.
    paragraphs = root.xpath("//w:body//w:p", namespaces=NS)
    headings = {paragraph_text(p): p for p in paragraphs}

    for number, (context, command) in QUESTIONS.items():
        heading = headings.get(f"2.{number}. PERGUNTA {number}")
        if heading is None:
            raise ValueError(f"Título da pergunta {number} não encontrado")
        heading_index = paragraphs.index(heading)
        candidate = None
        for following in paragraphs[heading_index + 1:]:
            text = paragraph_text(following)
            if not text:
                continue
            if text == "Alternativas":
                break
            candidate = following
            break
        if candidate is None:
            raise ValueError(f"Enunciado da pergunta {number} não encontrado")
        old_text = paragraph_text(candidate)
        if old_text.startswith("Contextualização:"):
            raise ValueError(f"Pergunta {number} já parece padronizada")

        parent = candidate.getparent()
        index = parent.index(candidate)
        parent.remove(candidate)
        parent.insert(index, make_paragraph(candidate, "Contextualização:", context))
        parent.insert(index + 1, make_paragraph(candidate))
        parent.insert(index + 2, make_paragraph(candidate, "Comando:", command))

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with zipfile.ZipFile(args.source, "r") as archive:
        names = archive.namelist()
        document_xml = archive.read("word/document.xml")
        rewritten = rewrite_document(document_xml)
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=args.output.parent) as handle:
            temporary = Path(handle.name)
        try:
            with zipfile.ZipFile(temporary, "w") as output:
                for name in names:
                    info = archive.getinfo(name)
                    payload = rewritten if name == "word/document.xml" else archive.read(name)
                    output.writestr(info, payload)
            temporary.replace(args.output)
        finally:
            if temporary.exists():
                temporary.unlink()

    print(f"Atividade padronizada: {args.output} ({len(QUESTIONS)} perguntas)")


if __name__ == "__main__":
    main()
