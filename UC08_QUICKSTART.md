# UC08 Quick Start

## 30 segundos

```bash
cd c:\git\sctec\opspilot_sandbox_base
python -m opspilot.seed
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

Você verá:

```
🚀 Iniciando UC08 com Decision Engine...

📊 RESULTADO DA AVALIAÇÃO UC08
==============================================================================
📋 Alerta: SEC-001
Status: completed
Resumo: Alerta de segurança tipo 'leaked_token'...

📊 Evidências (3):
   1. [security_alert] Alerta de segurança tipo 'leaked_token'...
   2. [open_incidents] Existem 3 incidentes abertos...
   3. [security_alert] Token foi detectado em 3 serviços...

🎯 Ações Propostas (1):
   1. revoke_token
      Razão: Token vazado com alta severidade (score: 100)...
      Risco: high
      Requer aprovação: True
      Dry-run: ✓
```

---

## 5 Cenários

```bash
# 1. Decision Engine (rápido, determinístico)
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token

# 2. Apenas simulação
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --dry-run

# 3. Aprovação automática
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve

# 4. Aprovação interativa (pede "s" ou "n")
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token

# 5. Output JSON (para integração)
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --json
```

### Cenários de Demo

```bash
# Token vazado (alta severidade)
python -m opspilot.main_uc08 X --engine-only --scenario demo-leaked-token

# Service account comprometida (CRÍTICO)
python -m opspilot.main_uc08 X --engine-only --scenario demo-compromised-sa

# Atividade suspeita (média severidade)
python -m opspilot.main_uc08 X --engine-only --scenario demo-suspicious
```

---

## 3 Caminhos de Implementação

### Path 1: Decision Engine (Rápido)

```python
from opspilot.uc08_decision_engine import UC08DecisionEngine
from opspilot.repository import Repository

repo = Repository()
alert = repo.get_security_alert("SEC-001")

engine = UC08DecisionEngine(repo=repo)
decision = engine.evaluate("SEC-001", alert)

print(decision.proposed_actions)  # [ProposedAction(...), ...]
```

**Pros:** Rápido, determinístico, sem LLM  
**Cons:** Sem raciocínio complexo

### Path 2: Agente LangChain (Inteligente)

```python
from opspilot.uc08_agent import run_agent_uc08

summary = run_agent_uc08(
    alert_id="SEC-001",
    model=None,  # usa Ollama default
    approval_handler=None,  # pede no terminal
)

print(summary.decision.proposed_actions)
```

**Pros:** Raciocínio tipo LLM, flexível  
**Cons:** Lento, requer Ollama/Claude

### Path 3: ApprovalManager (Controlador)

```python
from opspilot.uc08_approvals import ApprovalManager

approval_mgr = ApprovalManager(auto_approve=False)

# Pede ao humano
approved = approval_mgr.request_approval(
    action=proposed_action,
    evidence=evidence_list,
    alert_id="SEC-001",
    request_id="uc08-xxx",
)

if approved:
    result, success = approval_mgr.execute_action(action, ...)
    print(f"Executado: {result.status}")
```

**Pros:** Controle fino, aprovação explícita  
**Cons:** Manual, para integração personalizada

---

## Responder Perguntas de Apresentação

### P1: Qual evidência autorizou a ação?

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
# Veja a seção "📊 Evidências" no output
# Cada evidência tem source e confidence
```

### P2: Qual seria o impacto de uma ação errada?

Ver `UC08_IMPLEMENTATION.md`, seção "Qual seria o impacto...?"

Resumo:
- ✓ Dry-run simula sem alterar
- ✓ Aprovação humana valida
- ✓ Audit log rastreia

### P3: A idempotência foi garantida onde?

```bash
# Primeira execução
python -m opspilot.main_uc08 SEC-001 --engine-only --auto-approve
# Executa e registra em audit_log

# Segunda com MESMO request_id
# → status="duplicate", não executa de novo
```

### P4: O que aparece no trace/audit_log?

```bash
# Ver audit_log
python -m opspilot.cli audit | grep revoke_token

# Ver trace do LangSmith (depois de configurar)
# https://smith.langchain.com/projects/opspilot-uc08-runs
```

### P5: Quando deveria parar e pedir humano?

Ver `UC08_IMPLEMENTATION.md`, seção "Em que situação...?"

Resumo:
- Ação destrutiva (revoke_token, disable_service_account)
- Sem evidência suficiente
- Type de alerta desconhecido
- Service account comprometida (sempre escalate)

---

## Arquivos Importantes

```
UC08_QUICKSTART.md              ← Você está aqui
UC08_IMPLEMENTATION.md          ← Guia técnico completo
UC08_LANGSMITH_SETUP.md         ← Setup de observabilidade
src/opspilot/
  ├── uc08_models.py            ← Estruturas de dados
  ├── uc08_decision_engine.py    ← Lógica de decisão
  ├── uc08_agent.py              ← Agente LangChain
  ├── uc08_approvals.py          ← Handlers de aprovação
  ├── uc08_langsmith_config.py   ← Tracing
  └── main_uc08.py               ← CLI entry point
```

---

## Checklist de Apresentação

- [ ] Executei os 5 cenários
- [ ] Verifiquei que dry-run não executa
- [ ] Testei aprovação automática
- [ ] Testei rejeição (respondendo "N")
- [ ] Vi audit_log com `python -m opspilot.cli audit`
- [ ] Entendi a lógica de scoring (ver IMPLEMENTATION.md)
- [ ] Expliquei as 5 perguntas de apresentação
- [ ] Configurei LangSmith e vi um trace
- [ ] Identifiquei as 7 limitações conhecidas

---

## Próximos Passos

1. **Integrar com seu sistema**
   ```python
   from opspilot.main_uc08 import run
   run(alert_id="...", engine_only=True, json_output=True)
   ```

2. **Estender Decision Engine**
   - Adicionar novos tipos de alerta
   - Ajustar scoring
   - Integrar com SIEM externo

3. **Produção**
   - Remover DEMO_APPROVAL_TOKEN
   - Usar OAuth/assinatura real
   - Adicionar notificações (Slack, email)
   - Integrar com sua plataforma de alertas

---

**Tudo pronto! Execute e explore.** 🚀
