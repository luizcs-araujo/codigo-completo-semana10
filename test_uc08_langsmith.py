#!/usr/bin/env python
"""
Script de teste para UC08 com LangSmith.

Executa um cenário de demo e mostra informações de LangSmith.
"""
from __future__ import annotations
import os
import sys
import json
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar variáveis de ambiente (ler do .env)
from dotenv import load_dotenv
load_dotenv()

# Imports
from opspilot.uc08_langsmith_config import LangSmithConfig, setup_langsmith
from opspilot.main_uc08 import run

def main():
    print("=" * 80)
    print("🧪 UC08 - Teste com LangSmith")
    print("=" * 80)
    
    # 1. Verificar setup de LangSmith
    print("\n1️⃣  Verificando LangSmith...\n")
    
    ls_config = LangSmithConfig()
    if ls_config.is_tracing_enabled():
        print("✅ LangSmith HABILITADO")
        print(f"   Projeto: {ls_config.get_project_name()}")
        print(f"   Dashboard: {ls_config.get_trace_url_template()}")
    else:
        print("⚠️  LangSmith DESABILITADO")
        print("   Verifique .env com LANGSMITH_TRACING=true")
        return
    
    # 2. Executar cenário
    print("\n2️⃣  Executando cenário demo-leaked-token com LangSmith tracing...\n")
    
    try:
        run(
            alert_id="SEC-DEMO-001",
            engine_only=True,
            dry_run=False,
            auto_approve=True,
            json_output=False,
            scenario="demo-leaked-token",
        )
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Resultado
    print("\n3️⃣  LangSmith Trace Enviado!\n")
    
    print("=" * 80)
    print("📊 Resultado do Teste")
    print("=" * 80)
    
    print(f"""
✅ Teste Concluído!

📍 Dashboard LangSmith:
   {ls_config.get_trace_url_template()}

🔍 Como visualizar:
   1. Acesse o link acima
   2. Procure por runs recentes (SEC-DEMO-001)
   3. Clique para ver a timeline completa
   4. Analise cada tool call, inputs e outputs

⏱️  Nota: LangSmith pode levar 2-3 segundos para processar

📝 O que você verá no trace:
   • Decision Engine evaluation
   • Tool calls (get_security_alert, list_open_incidents)
   • Scoring e análise
   • Ações propostas
   • Tempo total e tokens (se aplicável)

🎯 Próximo passo:
   Execute com diferentes cenários:
   - python -m opspilot.main_uc08 SEC-001 --scenario demo-compromised-sa --auto-approve
   - python -m opspilot.main_uc08 SEC-001 --scenario demo-suspicious --auto-approve

💡 Tips:
   • Use --json para integração com outros sistemas
   • Use --dry-run para simular sem executar
   • Use sem --auto-approve para aprovação interativa
""")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
