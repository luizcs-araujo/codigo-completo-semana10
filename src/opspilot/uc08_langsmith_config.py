"""
Configuração de LangSmith para UC08.

LangSmith é um sistema de observabilidade para LLM applications.
Fornece tracing, debugging e monitoramento de agentes.

Setup:
1. Criar conta em https://smith.langchain.com
2. Obter API_KEY do dashboard
3. Configurar variáveis de ambiente
4. Executar agente com tracing habilitado

Variáveis de ambiente necessárias:
    LANGSMITH_API_KEY: sua chave de API (obtida em smith.langchain.com)
    LANGSMITH_PROJECT: nome do projeto (ex: opspilot-uc08-runs)
    LANGSMITH_TRACING: true para ativar
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any

from .config import get_settings


def setup_langsmith() -> bool:
    """
    Configura LangSmith baseado em variáveis de ambiente.

    Returns:
        True se configurado com sucesso, False caso contrário
    """
    settings = get_settings()

    if not settings.langsmith_tracing:
        return False

    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print(
            "⚠️  LANGSMITH_API_KEY não configurada. "
            "Tracing desativado.",
            file=sys.stderr,
        )
        return False

    # LangSmith será automaticamente ativado quando as variáveis
    # de ambiente estiverem presentes
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

    print(
        f"✓ LangSmith configurado para projeto: {settings.langsmith_project}",
        file=sys.stderr,
    )
    return True


def print_setup_instructions() -> None:
    """Imprime instruções de setup do LangSmith."""
    instructions = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    CONFIGURAÇÃO LANGSMITH PARA UC08                        ║
╚════════════════════════════════════════════════════════════════════════════╝

LangSmith é um dashboard de observabilidade para agentes LLM.

PASSO 1: Criar Conta
   • Acesse https://smith.langchain.com
   • Clique em "Sign up"
   • Complete o cadastro

PASSO 2: Obter API Key
   • No dashboard, clique no ícone de configurações (engrenagem)
   • Selecione "API Keys"
   • Clique em "+ Create API Key"
   • Copie a chave gerada

PASSO 3: Configurar Variáveis de Ambiente
   Adicione ao seu .env local (não comite!):

   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=sk_...  # Cole aqui a chave copiada
   LANGSMITH_PROJECT=opspilot-uc08-runs

PASSO 4: Executar Agente
   Com .env configurado, rode:

   python -m opspilot.main_uc08 SEC-001

   O trace aparecerá automaticamente no dashboard!

PASSO 5: Ver Resultados
   • Acesse https://smith.langchain.com/projects/opspilot-uc08-runs
   • Veja cada chamada de tool, tempo, tokens gastos
   • Analise decisões do agente em detalhes

═══════════════════════════════════════════════════════════════════════════════

DICAS:
  • Cada run é salvo e pode ser revisado depois
  • Use tags para filtrar e organizar runs
  • Compartilhe traces com a equipe via links públicos
  • LangSmith é opcional - funciona sem ele

═══════════════════════════════════════════════════════════════════════════════
"""
    print(instructions)


def trace_metadata() -> dict[str, Any]:
    """Retorna metadata para adicionar ao trace."""
    return {
        "use_case": "UC08",
        "scenario": "security_token_response",
        "version": "1.0",
    }


class LangSmithConfig:
    """Classe para gerenciar configuração de LangSmith."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.settings = get_settings()
        self.is_enabled = setup_langsmith()
        self._initialized = True

    def get_project_name(self) -> str:
        """Retorna nome do projeto LangSmith."""
        return self.settings.langsmith_project

    def is_tracing_enabled(self) -> bool:
        """Verifica se tracing está habilitado."""
        return self.is_enabled and self.settings.langsmith_tracing

    def get_trace_url_template(self) -> str:
        """Retorna template de URL para acessar trace no dashboard."""
        project = self.settings.langsmith_project
        return f"https://smith.langchain.com/projects/{project}/runs"
