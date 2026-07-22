# UC08 - Resumo Executivo em Português

## 🎯 O que foi implementado?

Agente de IA que responde automaticamente a alertas de segurança:
- **Token vazado** → Analisa e propõe revogar
- **Service account comprometida** → Escala para humano (muito arriscado)
- **Atividade suspeita** → Investigação manual

## 📊 Como funciona?

1. **Recebe alerta** com ID (ex: SEC-001)
2. **Coleta evidências** de múltiplas fontes
3. **Calcula risco** com scoring (0-100)
4. **Propõe ações** baseado em regras de segurança
5. **Simula tudo** com dry-run antes de fazer real
6. **Pede aprovação** do humano para ações perigosas
7. **Registra auditoria** de cada passo

## 🚀 Começar

```bash
cd c:\git\sctec\opspilot_sandbox_base
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

Verá uma análise estruturada com evidências e ações propostas.

## 🧠 Lógica de Decisão Simplificada

### Token Vazado

```
Severidade ALTA + Usado em múltiplos serviços + Incidentes abertos
                         ↓
Score = 95 (máx 100)
                         ↓
REVOKE_TOKEN (com aprovação humana)
```

### Service Account Comprometida

```
MUITO PERIGOSO → sempre escalate para humano
                         ↓
Nunca deabilita automático sem aprovação
```

### Atividade Suspeita

```
Requer investigação manual
                         ↓
ESCALATE_INCIDENT
```

## 📋 Arquivos Criados

```
src/opspilot/
├── uc08_models.py                    Estruturas de dados
├── uc08_decision_engine.py           Lógica de decisão (scoring)
├── uc08_agent.py                     Agente LangChain com HITL
├── uc08_approvals.py                 Aprovação + Auditoria
├── uc08_langsmith_config.py          Integração com tracing
└── main_uc08.py                      CLI

UC08_QUICKSTART.md                    Guia 5 min
UC08_IMPLEMENTATION.md                Guia técnico completo
UC08_ARCHITECTURE.md                  Diagramas e fluxos
UC08_LANGSMITH_SETUP.md               Setup de observabilidade
UC08_RESUMO_PT.md                     Este arquivo
```

## 5️⃣ Exemplos de Uso

### 1️⃣ Teste Rápido (Decision Engine)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

Resultado: Análise completa em 100ms

### 2️⃣ Apenas Simulação (Dry-run)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --dry-run
```

Resultado: Simula ações sem executar

### 3️⃣ Aprovação Automática (Testes)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve
```

Resultado: Executa depois do dry-run

### 4️⃣ Aprovação Interativa (Interativo)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

Resultado:
```
Aprovação necessária para: revoke_token
Target: token_prod_001

👤 Aprovar execução? [s/N]: s
✅ Aprovado
```

### 5️⃣ Output JSON (Integração)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --json
```

Resultado: JSON estruturado para processar em outro sistema

## 🔒 Segurança

### ✓ Nunca executa sem aprovação

```python
if action.requires_approval:
    approved = ask_human()
    if not approved:
        return "bloqueado"
```

### ✓ Sempre testa antes (dry-run)

```python
1. Simula: dry_run=True
2. Mostra resultado
3. Pede aprovação
4. Executa: dry_run=False
```

### ✓ Idempotência: mesma ação 2x não acontece

```python
request_id = "uc08-abc123"

# 1ª vez: executa
revoke_token(..., request_id="uc08-abc123")
# Status: "executed"

# 2ª vez com MESMO ID: não executa
revoke_token(..., request_id="uc08-abc123")
# Status: "duplicate"
```

### ✓ Auditoria completa

Cada ação fica registrada no banco:

```
ID | request_id  | action       | target          | dry_run | status   | timestamp
---|-------------|--------------|-----------------|---------|----------|------------------
1  | uc08-abc123 | revoke_token | token_prod_001  | 1       | dry_run  | 2026-07-21...
2  | uc08-abc123 | revoke_token | token_prod_001  | 0       | executed | 2026-07-21...
```

## 🎓 Padrões Demonstrados

### 1. Decision Engine Determinístico

✓ Regras claras  
✓ Previsível  
✗ Sem raciocínio complexo  

```python
if score >= 80 and len(incidents) > 0:
    propose("revoke_token")
else:
    propose("escalate_incident")
```

### 2. Human-In-The-Loop (HITL)

Agente pausa e pede humano para decisões críticas:

```python
if action.requires_approval:
    middleware.interrupt_on("revoke_token")
    # Agente pausa
    # Pede aprovação do operador
    # Continua se aprovado
```

### 3. Dry-Run Obrigatório

Nunca muda estado sem antes simular:

```python
# Passo 1: Simulação
result_dry = revoke_token(..., dry_run=True)
# Passo 2: Execução real
result_real = revoke_token(..., dry_run=False, approval_token="...")
```

### 4. Auditoria por Request ID

Garante que mesma ação não executa 2x:

```python
# Unique index previne duplicação
CREATE UNIQUE INDEX idx_audit_request_action 
ON audit_log(request_id, action) 
WHERE dry_run = 0;
```

### 5. Observabilidade com LangSmith

Todos os passos são rastreados:

```
get_security_alert(SEC-001)
  → Input: {alert_id: "SEC-001"}
  → Output: {severity: "high", ...}
  
list_open_incidents()
  → Input: {}
  → Output: [{incident1}, ...]
  
revoke_token(dry_run=True)
  → Input: {token_id, request_id, ...}
  → Output: ActionResult(status="dry_run")
```

## ❓ Perguntas de Apresentação Respondidas

### P1: Qual evidência autorizou a ação?

Múltiplas evidências são coletadas:

```
1. [security_alert] Severidade "high" → score: 75
2. [security_alert] 3 serviços afetados → score: +20 = 95
3. [open_incidents] 3 incidentes abertos → qualifica

Score >= 80 + incidentes = REVOGAR TOKEN
```

### P2: Qual o impacto de uma ação errada?

**Proteções:**
- Dry-run simula sem alterar
- Aprovação humana valida
- Audit trail rastreia tudo
- Request_id permite diagnosticar

### P3: A idempotência foi garantida onde?

**Unique index no banco:**

```sql
CREATE UNIQUE INDEX idx_audit_request_action 
ON audit_log(request_id, action) 
WHERE dry_run = 0;
```

Mesma ação 2x com mesmo `request_id` retorna "duplicate".

### P4: O que aparece no trace/audit_log?

**Audit Log (DB):**
```
request_id | action | target | dry_run | status | details
```

**LangSmith (Dashboard):**
```
https://smith.langchain.com/projects/opspilot-uc08-runs
← Lista cada run com timeline completo
```

### P5: Quando deveria parar e pedir humano?

```
✓ Ação destrutiva (revoke_token, disable_service_account)
✓ Sem evidência suficiente (score < 50)
✓ Tipo de alerta desconhecido
✓ Service account comprometida (sempre escalate)
✓ Erro durante avaliação
```

## ⚠️ Limitações Conhecidas

| Limitação | Por quê | Mitigação |
|-----------|--------|-----------|
| Decision Engine é determinístico (sem LLM) | Simples, previsível | Use agente LLM para complexo |
| Sem histórico de ações prévias | Evita acoplamento | request_id + audit_log |
| Sem integração com SIEM externo | Foco local | Extensível via repository |
| Sem rollback automático | Ação irreversível | Auditoria permite diagnosticar |
| Sem notificações automáticas (email/Slack) | Fora do escopo | Extensível após execução |
| Scoring simples (sem ML) | Determinístico | Regras bem documentadas |
| Approval token hardcoded (DEMO) | Educacional | Usar OAuth em produção |

## 📈 Próximos Passos

### Curto Prazo (hoje)
```bash
# Execute os 5 cenários
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-compromised-sa
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-suspicious

# Teste dry-run
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --dry-run

# Veja audit_log
python -m opspilot.cli audit
```

### Médio Prazo (integração)
```python
from opspilot.main_uc08 import run

# Sua aplicação
alert = receive_alert_from_siem()
run(
    alert_id=alert['id'],
    engine_only=True,
    json_output=True
)
```

### Longo Prazo (produção)
- Remover DEMO_APPROVAL_TOKEN
- Usar OAuth/assinatura real
- Integrar com SIEM (Splunk, ELK, etc)
- Notificações (Slack, email, PagerDuty)
- ML para scoring dinâmico
- Webhook outbound para sistemas correlatos

## 🔗 Documentação

| Documento | Para quem | Conteúdo |
|-----------|-----------|----------|
| UC08_QUICKSTART.md | Rápido | 5 exemplos, checklist |
| UC08_IMPLEMENTATION.md | Técnico | Detalhes, Q&A, limitações |
| UC08_ARCHITECTURE.md | Design | Diagramas, fluxos, componentes |
| UC08_LANGSMITH_SETUP.md | Observabilidade | Setup de tracing em 5 min |

## 📞 Suporte

Para dúvidas:

1. Veja `UC08_QUICKSTART.md` (rápido)
2. Veja `UC08_IMPLEMENTATION.md` (técnico)
3. Execute: `python -m opspilot.main_uc08 --setup-langsmith`

---

**Status:** ✅ Completo e pronto para uso  
**Última atualização:** Julho 2026  
**Autor:** UC08 Implementation Team
