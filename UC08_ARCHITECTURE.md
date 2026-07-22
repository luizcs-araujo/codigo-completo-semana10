# UC08 - Arquitetura

## Diagrama de Fluxo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ENTRADA: alert_id                             │
│                       (SEC-001, SEC-002, ...)                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Repository.get_        │
                    │   security_alert()       │
                    └──────────────┬───────────┘
                                   │
                    ┌──────────────────────────────────┐
                    │     Carregar dados do alerta:    │
                    │  • alert_type                    │
                    │  • severity                      │
                    │  • token_id / service_account_id │
                    │  • affected_services             │
                    │  • exposure_window_minutes       │
                    └──────────────┬────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │  Decision Engine         │
                    │  evaluate()              │
                    └──────────────┬───────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
    ┌────────┐           ┌──────────────────┐      ┌────────────────┐
    │ Coletar│           │ Coletar          │      │ Aplicar        │
    │ Dados  │           │ Incidentes       │      │ Política de    │
    │ Alerta │           │ Abertos          │      │ Decisão        │
    └────┬───┘           └────────┬─────────┘      └────────┬───────┘
         │                        │                         │
         └────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                      ┌─────────────────────────┐
                      │ Calcular Score (0-100)  │
                      │                         │
                      │ Severidade: +[25-100]   │
                      │ Múltiplos serviços: +20 │
                      │ Exposição longa: +20    │
                      └────────────┬────────────┘
                                   │
                 ┌─────────────────┴────────────────┐
                 │                                  │
       ┌─────────▼──────────┐         ┌────────────▼────────┐
       │ Score Analysis     │         │ Action Selection    │
       │                    │         │                     │
       │ score >= 80 +      │  →      │ revoke_token        │
       │ incidents          │         │ disable_sa          │
       │                    │         │ escalate_incident   │
       │ score >= 80 -      │  →      │ escalate_incident   │
       │ incidents          │         │                     │
       │                    │         │ none                │
       │ score < 80         │  →      │ escalate/none       │
       └────────────────────┘         └────────────┬────────┘
                                                    │
                                                    ▼
                          ┌─────────────────────────────────────┐
                          │      UC08Decision Estruturado       │
                          │                                     │
                          │ • evidence: [Evidence(...), ...]    │
                          │ • proposed_actions: [Action(...)]   │
                          │ • requires_human: bool              │
                          │ • request_id: str (idempotente)     │
                          └─────────────────────────┬───────────┘
                                                    │
                        ┌───────────────────────────┴────────────────────┐
                        │                                                │
                        ▼                                                ▼
            ┌─────────────────────────┐                   ┌──────────────────────┐
            │ action.requires_        │                   │ action.requires_     │
            │ approval = False        │                   │ approval = True      │
            └──────────┬──────────────┘                   └──────────┬───────────┘
                       │                                            │
                       ▼                                            ▼
            ┌─────────────────────────┐              ┌─────────────────────────┐
            │ Executar Direto         │              │ ApprovalManager         │
            │ (ex: escalate)          │              │ request_approval()      │
            │                         │              │                         │
            │ escalate_incident()     │              │ Mostra:                 │
            └──────────┬──────────────┘              │ • Ação                  │
                       │                            │ • Evidências            │
                       │                            │ • Riscos                │
                       │                            │                         │
                       │                            │ Pede humano:            │
                       │                            │ "Aprovar? [s/N]"        │
                       │                            └──────┬──────────────────┘
                       │                                   │
                       │                   ┌───────────────┴──────────────┐
                       │                   │                              │
                       │              Sim (s)                        Não (N)
                       │                   │                              │
                       │                   ▼                              ▼
                       │         ┌─────────────────────┐    ┌────────────────────┐
                       │         │ execute_action()    │    │ Bloqueado          │
                       │         │                     │    │ Ação rejeitada     │
                       │         │ 1. Dry-run          │    │ Registra auditoria │
                       │         │ (simula)            │    │ Retorna com        │
                       │         │                     │    │ requires_human=True│
                       │         │ 2. Execução Real    │    └────────────────────┘
                       │         │ (com approval_token)│
                       │         └────────┬────────────┘
                       │                  │
                       │                  ▼
                       │    ┌──────────────────────────────┐
                       │    │ Registrar em audit_log:      │
                       │    │ • request_id (idempotência)  │
                       │    │ • action                     │
                       │    │ • target                     │
                       │    │ • dry_run flag               │
                       │    │ • status: "executed"         │
                       │    │ • details (JSON)             │
                       │    └────────────┬─────────────────┘
                       │                 │
                       └─────────────────┼──────────────────┐
                                         │                  │
                                         ▼                  ▼
                               ┌──────────────────┐  ┌──────────────┐
                               │ UC08RunSummary   │  │ LangSmith    │
                               │                  │  │ Trace        │
                               │ • decision       │  │ (opcional)   │
                               │ • tools_called   │  │              │
                               │ • duration       │  │ • cada tool  │
                               │ • trace_url      │  │ • raciocínio │
                               │ • timestamp      │  │ • tokens     │
                               └──────────────────┘  └──────────────┘
                                         │
                                         ▼
                            ┌────────────────────────┐
                            │ Output (3 formatos)    │
                            │                        │
                            │ 1. Renderizado (human) │
                            │ 2. JSON (integração)   │
                            │ 3. LangSmith dashboard │
                            └────────────────────────┘
```

---

## Componentes

### 1. Decision Engine

```
uc08_decision_engine.py
├── UC08DecisionEngine(repo)
│   ├── evaluate(alert_id, alert_data)
│   │   ├── _evaluate_alert_severity() → (severity, score)
│   │   ├── _evaluate_leaked_token() → ProposedAction[]
│   │   ├── _evaluate_compromised_service_account() → ProposedAction[]
│   │   ├── _evaluate_suspicious_activity() → ProposedAction[]
│   │   └── return UC08Decision
│   └── propose_dry_run(action) → ActionResult
```

**Responsabilidades:**
- Avaliar severidade do alerta
- Buscar incidentes correlatos
- Coletar evidências
- Propor ações baseado em regras
- Retornar decision estruturada

---

### 2. Approval Manager

```
uc08_approvals.py
├── ApprovalManager(repo, auto_approve)
│   ├── request_approval(action, evidence, ...) → bool
│   │   ├── _assess_risk(action) → str
│   │   └── Mostra para humano e pede sim/não
│   ├── execute_action(action, alert_id, ...) → (ActionResult, bool)
│   │   ├── _call_action_tool(revoke_token|disable_sa|escalate)
│   │   └── Registra em audit_log
│   └── prompt_approval(action_dict) → bool (HITL middleware)
└── ExecutionLogger(output_file)
    ├── log_approval_requested()
    ├── log_approval_decision()
    └── log_action_executed()
```

**Responsabilidades:**
- Pedir aprovação ao humano
- Executar com dry-run primeiro
- Chamar tool apropriada
- Registrar auditoria
- Gerenciar logging

---

### 3. Agente LangChain

```
uc08_agent.py
├── build_agent_uc08(model, middleware) → LangGraph
│   ├── Tools: [get_security_alert, list_open_incidents, 
│   │           revoke_token, disable_service_account, 
│   │           escalate_incident]
│   ├── Middleware: [HumanInTheLoopMiddleware, 
│   │                ModelCallLimitMiddleware,
│   │                ToolCallLimitMiddleware]
│   └── Response format: UC08Decision
├── run_agent_uc08(alert_id, model, approval_handler) → UC08RunSummary
│   ├── graph.invoke() com alert_id
│   ├── _resume_after_human_review() para HITL
│   └── Capturar e formatar resultado
└── evaluate_alert_with_engine() (fast path sem LLM)
```

**Responsabilidades:**
- Construir agente com LangChain
- Suportar middleware HITL
- Executar com ou sem LLM
- Capturar traces
- Retornar sumário estruturado

---

### 4. CLI Entry Point

```
main_uc08.py
├── main() → argparse
│   ├── --engine-only (Decision Engine vs LLM)
│   ├── --dry-run (apenas simulação)
│   ├── --auto-approve (auto vs interativo)
│   ├── --json (output estruturado)
│   ├── --scenario (demo alertas)
│   └── --setup-langsmith (instruções)
├── run(alert_id, ...) → None
│   ├── Carregar alerta
│   ├── _run_with_engine() ou _run_with_agent()
│   └── Output (renderizado ou JSON)
└── Funções auxiliares
    ├── _render_summary() (human-readable)
    ├── _create_demo_alert() (scenarios)
    └── print_setup_instructions() (LangSmith)
```

**Responsabilidades:**
- Parsing de argumentos CLI
- Routing para engine ou agent
- Formatação de output
- Instruções de setup

---

### 5. Data Models

```
uc08_models.py
├── SecurityAlertData          ← Dados brutos do alerta
├── Evidence                   ← Uma prova coletada
├── ProposedAction             ← Uma ação que pode tomar
├── UC08Decision               ← Decisão completa
├── UC08RunSummary             ← Resultado de execução
└── ApprovalRequest            ← Requisição para humano
```

---

## Fluxos Alternativos

### Fluxo A: Engine-Only (Rápido)

```
alert_id
   ↓
Repository.get_security_alert()
   ↓
UC08DecisionEngine.evaluate()
   ↓
UC08Decision (com ou sem execução)
   ↓
Renderizar
```

**Tempo:** ~100ms  
**Usa LLM:** Não  
**Aprovação:** Interativa (humano no terminal)

---

### Fluxo B: Agente + LLM (Inteligente)

```
alert_id
   ↓
build_agent_uc08()
   ↓
graph.invoke() com "Processe o alerta..."
   ↓
Chamadas a tools automaticamente
   ├─ get_security_alert
   ├─ list_open_incidents
   └─ Eventualmente: revoke_token (pausa para HITL)
   ↓
_resume_after_human_review() (se houver interrupt)
   ↓
UC08Decision
   ↓
UC08RunSummary com trace
```

**Tempo:** ~5-30s (depende do modelo)  
**Usa LLM:** Sim (Ollama/Claude)  
**Aprovação:** Middleware HITL

---

### Fluxo C: Integração com Sistema Externo

```python
# Seu sistema
alert = fetch_from_siem()
result = run(alert_id=alert['id'], json_output=True)
parsed = json.loads(result)

# Processar resultado
if parsed['decision']['requires_human']:
    send_to_queue("approval_needed", parsed)
else:
    log_execution(parsed)
```

---

## Pontos de Integração

### 1. Com OpsPilot Repository

```python
repo.get_security_alert(alert_id)      # Leitura
repo.list_open_incidents()             # Leitura
repo.revoke_token(...)                 # Escrita + auditoria
repo.disable_service_account(...)      # Escrita + auditoria
repo.escalate_incident(...)            # Escrita + auditoria
```

### 2. Com LangChain

```python
# Middleware HITL
HumanInTheLoopMiddleware(interrupt_on={"revoke_token": {...}})

# Tools
@tool
def get_security_alert(alert_id: str) -> dict
```

### 3. Com LangSmith

```python
@traced(name="uc08_evaluate_alert", run_type="tool")
def evaluate_alert_with_engine(alert_id, repo):
    ...
```

---

## Garantias de Segurança

| Garantia | Como? |
|----------|-------|
| **Sem execução sem aprovação** | `approval_token` validado em repository |
| **Sem duplicação de ações** | `request_id` unique index em audit_log |
| **Auditoria completa** | Cada passo em audit_log com timestamp |
| **Dry-run obrigatório** | ApprovalManager.execute_action() roda dry_run antes |
| **Decisão justificada** | Evidence[] lista todas as provas |
| **Human-in-the-loop** | Aprovação interativa ou HITL middleware |

---

## Performance

| Operação | Tempo | Notas |
|----------|-------|-------|
| Carregar alerta | ~5ms | DB local |
| Decision Engine | ~50ms | Scoring + query |
| Dry-run | ~100ms | Simula escrita |
| Execução real | ~200ms | Com auditoria |
| Agente LLM | ~5-30s | Depende do modelo |
| LangSmith trace | ~500ms | Assíncrono |

---

## Escalabilidade

**Estado:** Atual = 1 alerta por execução

**Para múltiplos alertas:**

```python
alerts = repo.list_security_alerts(status="active")
for alert in alerts:
    decision = engine.evaluate(alert['id'], alert)
    # Processar...
```

**Batch:**

```python
async def process_batch(alert_ids):
    tasks = [
        evaluate_alert_with_engine(aid) 
        for aid in alert_ids
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Observabilidade

### Logs do Terminal

```
🚀 Iniciando UC08...
📋 Alerta: SEC-001
📊 Evidências (3): ...
🎯 Ações Propostas: ...
⚠️  Aprovação necessária...
✅ Aprovado
⚡ Executando revoke_token...
```

### Audit Log (Banco de Dados)

```sql
SELECT * FROM audit_log 
WHERE action IN ('revoke_token', 'escalate_incident')
ORDER BY created_at DESC;
```

### LangSmith Dashboard

```
https://smith.langchain.com/projects/opspilot-uc08-runs
```

Mostra:
- Cada run e seus resultados
- Chamadas a tools com inputs/outputs
- Tempo de cada operação
- Tokens gastos
- Erros/exceções

---

**Última atualização:** Julho 2026
