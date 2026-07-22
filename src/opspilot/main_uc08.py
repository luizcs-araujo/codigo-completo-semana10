#!/usr/bin/env python
"""
Entry point para UC08: Resposta a token vazado e service account perigosa.

Uso:
    python -m opspilot.main_uc08 <alert_id> [--dry-run] [--auto-approve] [--engine-only] [--json]

Exemplos:
    # Avaliar com Decision Engine (determinístico, rápido)
    python -m opspilot.main_uc08 SEC-001 --engine-only

    # Avaliar com agente LLM (requer Ollama)
    python -m opspilot.main_uc08 SEC-001 --auto-approve

    # Apenas simulação (dry_run)
    python -m opspilot.main_uc08 SEC-001 --dry-run

    # Output JSON
    python -m opspilot.main_uc08 SEC-001 --json

Cenários:
    SEC-001: Token de API vazado com alta severidade
    SEC-002: Service account comprometida
    SEC-003: Atividade suspeita detectada
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from typing import Any

from .repository import Repository
from .uc08_agent import (
    run_agent_uc08,
    evaluate_alert_with_engine,
)
from .uc08_approvals import ApprovalManager, ExecutionLogger, make_approval_handler
from .uc08_decision_engine import UC08DecisionEngine
from .uc08_models import UC08RunSummary
from .uc08_langsmith_config import (
    setup_langsmith,
    print_setup_instructions,
    LangSmithConfig,
)


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        prog="opspilot-uc08",
        description="Agente de resposta a token vazado e service account perigosa",
    )

    parser.add_argument(
        "alert_id",
        help="ID do alerta de segurança (ex: SEC-001)",
    )

    parser.add_argument(
        "--engine-only",
        action="store_true",
        help="Usar apenas Decision Engine (sem LLM)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas simular, não executar",
    )

    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Aprovar automaticamente (para testes)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output em JSON puro",
    )

    parser.add_argument(
        "--scenario",
        choices=["demo-leaked-token", "demo-compromised-sa", "demo-suspicious"],
        help="Se alert_id não existe, criar cenário de demo",
    )

    parser.add_argument(
        "--setup-langsmith",
        action="store_true",
        help="Mostrar instruções de setup do LangSmith",
    )

    args = parser.parse_args()

    # Se pediu setup, mostrar instruções e sair
    if args.setup_langsmith:
        print_setup_instructions()
        sys.exit(0)

    try:
        # Configurar LangSmith (se habilitado)
        setup_langsmith()

        run(
            alert_id=args.alert_id,
            engine_only=args.engine_only,
            dry_run=args.dry_run,
            auto_approve=args.auto_approve,
            json_output=args.json,
            scenario=args.scenario,
        )
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        else:
            print(f"❌ Erro: {str(e)}", file=sys.stderr)
        sys.exit(1)


def run(
    alert_id: str,
    engine_only: bool = False,
    dry_run: bool = False,
    auto_approve: bool = False,
    json_output: bool = False,
    scenario: str | None = None,
) -> None:
    """
    Executa UC08 com configurações especificadas.

    Args:
        alert_id: ID do alerta
        engine_only: Usar Decision Engine
        dry_run: Apenas simulação
        auto_approve: Aprovar automaticamente
        json_output: Output JSON
        scenario: Cenário de demo
    """
    repo = Repository()
    logger = ExecutionLogger()

    # Carregar alerta
    alert_data = repo.get_security_alert(alert_id)

    if not alert_data and scenario:
        # Criar alerta de demo
        alert_data = _create_demo_alert(scenario)
        if not json_output:
            print(f"📝 Alerta de demo criado: {scenario}\n")

    if not alert_data:
        raise ValueError(f"Alerta {alert_id} não encontrado")

    # Escolher caminho
    if engine_only:
        summary = _run_with_engine(
            alert_id, alert_data, dry_run, logger, json_output
        )
    else:
        summary = _run_with_agent(
            alert_id, alert_data, dry_run, auto_approve, logger, json_output
        )

    # Output
    if json_output:
        print(json.dumps(summary.model_dump(), indent=2, ensure_ascii=False))
    else:
        _render_summary(summary)


def _run_with_engine(
    alert_id: str,
    alert_data: dict,
    dry_run: bool,
    logger: ExecutionLogger,
    json_output: bool,
) -> UC08RunSummary:
    """Executa via Decision Engine (determinístico)."""
    repo = Repository()

    if not json_output:
        print("🚀 Iniciando UC08 com Decision Engine...\n")

    engine = UC08DecisionEngine(repo=repo)
    decision = engine.evaluate(alert_id, alert_data)

    # Processar ações propostas
    if not dry_run and decision.proposed_actions:
        approval_mgr = ApprovalManager(repo=repo, auto_approve=True)

        for action in decision.proposed_actions:
            if action.requires_approval:
                if not json_output:
                    print(
                        f"\n💾 Executando dry-run de {action.action_type}..."
                    )

                # Dry-run
                dry_result = approval_mgr._call_action_tool(
                    action, decision.request_id, dry_run=True
                )
                action.dry_run_result = dry_result.data

                if not json_output:
                    print(f"   ✓ Simulação concluída")

    # Montar resumo
    run_id = f"uc08-engine-{alert_id}"
    summary = UC08RunSummary(
        run_id=run_id,
        alert_id=alert_id,
        decision=decision,
        tools_called=[],
        model_calls=0,
        timestamp=datetime.now().isoformat(),
    )

    return summary


def _run_with_agent(
    alert_id: str,
    alert_data: dict,
    dry_run: bool,
    auto_approve: bool,
    logger: ExecutionLogger,
    json_output: bool,
) -> UC08RunSummary:
    """Executa via agente LangChain."""
    if not json_output:
        print("🤖 Iniciando UC08 com agente LangChain...\n")

    repo = Repository()
    approval_mgr = ApprovalManager(repo=repo, auto_approve=auto_approve)

    handler = None
    if not dry_run and not auto_approve:
        handler = make_approval_handler(approval_mgr, logger)

    try:
        summary = run_agent_uc08(
            alert_id=alert_id,
            model=None,  # Usa modelo default (Ollama)
            approval_handler=handler,
            repo=repo,
        )
        return summary

    except Exception as e:
        if not json_output:
            print(f"⚠️  Falha ao executar agente: {str(e)}")

        # Fallback para Decision Engine
        decision = UC08DecisionEngine(repo=repo).evaluate(alert_id, alert_data)
        return UC08RunSummary(
            run_id=f"uc08-agent-fallback-{alert_id}",
            alert_id=alert_id,
            decision=decision,
            tools_called=[],
            timestamp=datetime.now().isoformat(),
        )


def _render_summary(summary: UC08RunSummary) -> None:
    """Renderiza resumo em formato legível."""
    print("\n" + "=" * 80)
    print("📊 RESULTADO DA AVALIAÇÃO UC08")
    print("=" * 80)

    print(f"\n🔑 Run ID: {summary.run_id}")
    print(f"⏱️  Timestamp: {summary.timestamp}")
    if summary.duration_seconds:
        print(f"⏱️  Duração: {summary.duration_seconds:.2f}s")

    # Mostrar URL do LangSmith se disponível
    ls_config = LangSmithConfig()
    if ls_config.is_tracing_enabled():
        print(f"🔗 LangSmith Trace: {ls_config.get_trace_url_template()}")
        print(f"   (procure por run_id: {summary.run_id})")

    decision = summary.decision

    print(f"\n📋 Alerta: {decision.alert_id}")
    print(f"Status: {decision.status}")
    print(f"Resumo: {decision.summary}")

    if decision.evidence:
        print(f"\n📊 Evidências ({len(decision.evidence)}):")
        for i, ev in enumerate(decision.evidence, 1):
            print(f"   {i}. [{ev.source}] {ev.claim}")
            print(f"      Confiança: {ev.confidence}")
            if ev.excerpt:
                print(f"      → {ev.excerpt[:70]}")

    if decision.proposed_actions:
        print(f"\n🎯 Ações Propostas ({len(decision.proposed_actions)}):")
        for i, action in enumerate(decision.proposed_actions, 1):
            print(f"   {i}. {action.action_type}")
            print(f"      Razão: {action.reason}")
            print(f"      Risco: {action.risk_level}")
            print(f"      Requer aprovação: {action.requires_approval}")
            if action.dry_run_result:
                print(f"      Dry-run: ✓")

    if decision.action_executed:
        action = decision.action_executed
        print(f"\n✅ Ação Executada:")
        print(f"   {action.action_type}")
        print(f"   Target: {action.target_id}")

    if decision.limitations:
        print(f"\n⚠️  Limitações ({len(decision.limitations)}):")
        for lim in decision.limitations:
            print(f"   • {lim}")

    if decision.requires_human:
        print(f"\n👤 ⚠️  REQUER REVISÃO HUMANA")

    if summary.tools_called:
        print(f"\n🔧 Tools chamadas ({len(summary.tools_called)}):")
        for tool in summary.tools_called:
            print(f"   • {tool}")

    print("\n" + "=" * 80 + "\n")


def _create_demo_alert(scenario: str) -> dict:
    """Cria alerta de demo para testes."""
    demos = {
        "demo-leaked-token": {
            "id": "SEC-DEMO-001",
            "alert_type": "leaked_token",
            "subject": "api_token_prod_001",
            "severity": "high",
            "status": "active",
            "token_id": "token_prod_001",
            "service_account_id": None,
            "details": json.dumps(
                {
                    "exposure_window_minutes": 45,
                    "affected_services": ["payment-api", "billing-service", "user-auth"],
                    "discovered_at": "2024-07-21T10:30:00Z",
                }
            ),
        },
        "demo-compromised-sa": {
            "id": "SEC-DEMO-002",
            "alert_type": "compromised_service_account",
            "subject": "backup_automation_sa",
            "severity": "critical",
            "status": "active",
            "token_id": None,
            "service_account_id": "sa_backup_automation",
            "details": json.dumps(
                {
                    "exposure_window_minutes": 120,
                    "affected_services": ["s3-backup", "database-export", "archive-pipeline"],
                    "suspicious_activity": "Acesso incomum a dados de produção",
                }
            ),
        },
        "demo-suspicious": {
            "id": "SEC-DEMO-003",
            "alert_type": "suspicious_activity",
            "subject": "unusual_api_calls",
            "severity": "medium",
            "status": "active",
            "token_id": None,
            "service_account_id": None,
            "details": json.dumps(
                {
                    "detected_at": "2024-07-21T11:00:00Z",
                    "pattern": "Múltiplas tentativas de acesso a endpoint privado",
                }
            ),
        },
    }

    return demos.get(scenario, {})


if __name__ == "__main__":
    main()
