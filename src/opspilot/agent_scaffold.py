"""Esqueleto opcional para os trios criarem seus agentes.

Este arquivo NÃO resolve nenhum use case. Ele apenas mostra onde plugar modelo, tools e structured output.
"""
from __future__ import annotations
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from .config import get_settings
from .models import AgentRunSummary
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """
Você é um agente operacional integrado ao OpsPilot Sandbox.
Use tools de leitura para reunir evidências.
Antes de qualquer ação de escrita sensível, faça dry_run e peça aprovação humana.
Não use RAG neste exercício.
Responda com saída estruturada.
"""

def build_agent(selected_tools=None):
    settings = get_settings()
    model = ChatOllama(model=settings.ollama_model, temperature=0)
    return create_agent(
        model=model,
        tools=selected_tools or ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        response_format=AgentRunSummary,
    )
