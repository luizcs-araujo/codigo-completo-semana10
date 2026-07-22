# UC08 - Implementação: Resposta a token vazado e service account perigosa

## 📋 Visão Geral

Este documento descreve a implementação completa do UC08 no OpsPilot Sandbox.

**Objetivo:** Agente que responde automaticamente a alertas de segurança (token vazado, service account comprometida) com decisões estruturadas, dry-run obrigatório e aprovação humana para ações destrutivas.

**Arquivos principais:**
- `src/opspilot/uc08_models.py` - Modelos de dados
- `src/opspilot/uc08_decision_engine.py` - Lógica de decisão
- `src/opspilot/uc08_agent.py` - Agente LangChain
- `src/opspilot/uc08_approvals.py` - Handlers de aprovação
- `src/opspilot/main_uc08.py` - Entry point e exemplos

---

## 🚀 Como Executar

### Setup Inicial

```bash
# 1. Clonar/entrar no repositório
cd c:\git\sctec\opspilot_sandbox_base

# 2. Criar ambiente virtual (se não tiver)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -e ".[dev]"

# 4. Inicializar banco de dados
python -m opspilot.seed
```

### Executar Cenários

#### Cenário 1: Decision Engine (Determinístico, Rápido)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

**O que vê:**
```
🚀 Iniciando UC08 com Decision Engine...

📊 Evidências (2):
   1. [security_alert] Alerta de segurança tipo 'leaked_token'...
   2. [open_incidents] Existem 3 incidentes abertos no sistema

🎯 Ações Propostas (1):
   1. revoke_token
      Razão: Token vazado com alta severidade (score: 100)...
      Risco: high
```

#### Cenário 2: Dry-run Completo

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --dry-run
```

Simula todas as ações sem executar nada realmente. Registra em `audit_log` com status `dry_run`.

#### Cenário 3: Execução com Aprovação Automática

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve
```

Executa ações após dry-run, usando `approval_token=APPROVED-LOCAL-DEMO`.

#### Cenário 4: Aprovação Interativa

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

Pausa e pede aprovação do operador:
```
======================================================================
⚠️  APROVAÇÃO NECESSÁRIA PARA AÇÃO DE SEGURANÇA
======================================================================

📋 Alerta: SEC-001
🔑 Request ID: uc08-abc123def456

🎯 Ação proposta: revoke_token
   Target: token_prod_001
   Razão: Token vazado com alta severidade...
   Risco: HIGH

👤 Aprovar execução? [s/N]: 
```

Digite `s` para aprovar, qualquer outra coisa para rejeitar.

#### Cenário 5: Output JSON (para integração com outros sistemas)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --json
```

Retorna JSON estruturado:
```json
{
  "run_id": "uc08-engine-SEC-001",
  "alert_id": "SEC-001",
  "decision": {
    "status": "completed",
    "summary": "...",
    "evidence": [...],
    "proposed_actions": [...]
  }
}
```

---

## 🧠 Lógica de Decisão

### Decision Engine

Arquivo: `src/opspilot/uc08_decision_engine.py`

O engine avalia alertas de segurança usando uma **scoring baseado em evidências**.

#### Fluxo

```
1. Carregar alerta
2. Avaliar severidade → score (0-100)
3. Buscar incidentes abertos
4. Coletar evidências
5. Propor ações baseado em tipo e score
6. Retornar UC08Decision estruturado
```

#### Tipos de Alerta

**1. Leaked Token (token_id vazado)**

| Condição | Ação | Aprovação? |
|----------|------|-----------|
| score >= 80 + incidentes abertos | `revoke_token` | ✓ Sim |
| score >= 80 sem incidentes | `escalate_incident` | ✗ Não |
| 50 <= score < 80 | `escalate_incident` | ✗ Não |
| score < 50 | `none` | ✗ Não |

**2. Compromised Service Account (CRÍTICO)**

| Condição | Ação | Aprovação? |
|----------|------|-----------|
| score >= 90 + múltiplos incidentes | `disable_service_account` | ✓ Sim |
| score >= 80 | `escalate_incident` | ✗ Não |

> **Princípio:** Service accounts são muito perigosas. Requerem múltiplas evidências antes de desabilitar.

**3. Suspicious Activity (atividade suspeita)**

Sempre `escalate_incident` com requer investigação manual.

#### Scoring

```python
base_score = {
    "critical": 100,
    "high": 75,
    "medium": 50,
    "low": 25,
}

# Aumenta se exposição foi longa
if exposure_minutes > 120:
    score += 20  # máx 100

# Aumenta se múltiplos serviços afetados
if len(affected_services) > 2:
    score += 20  # máx 100
```

### Exemplo de Decisão

**Entrada:**
```python
alert = {
    "id": "SEC-001",
    "alert_type": "leaked_token",
    "severity": "high",
    "token_id": "token_prod_001",
    "affected_services": ["payment-api", "billing-service", "user-auth"],
    "exposure_window_minutes": 45,
}
open_incidents = [  # 3 incidentes abertos
    {"id": "INC-001", ...},
    {"id": "INC-002", ...},
    {"id": "INC-003", ...},
]
```

**Cálculo:**
```
score = 75 (high) + 20 (3 serviços) = 95
score >= 80 + len(incidents) > 0 → REVOKE_TOKEN
```

**Saída:**
```python
UC08Decision(
    alert_id="SEC-001",
    status="completed",
    summary="Alerta de segurança tipo 'leaked_token'...",
    evidence=[
        Evidence(claim="Alerta com severidade 'high'", ...),
        Evidence(claim="Existem 3 incidentes abertos", ...),
        Evidence(claim="Token foi detectado em 3 serviços", ...),
    ],
    proposed_actions=[
        ProposedAction(
            action_type="revoke_token",
            target_id="token_prod_001",
            reason="Token vazado com alta severidade (score: 95) e incidentes abertos",
            risk_level="high",
            requires_approval=True,
        )
    ],
    requires_human=True,  # porque requires_approval=True
)
```

---

## 🔐 Fluxo de Aprovação e Execução

Arquivo: `src/opspilot/uc08_approvals.py`

### ApprovalManager

Gerencia todo o fluxo de aprovação:

1. **request_approval()** - Pede aprovação ao humano
   - Mostra ação, evidências, riscos
   - Pede sim/não no terminal
   - Retorna bool

2. **execute_action()** - Executa ação proposta
   - Passo 1: Dry-run (simula)
   - Passo 2: Execução real (com approval_token)
   - Retorna ActionResult

3. **prompt_approval()** - Interface com middleware HITL
   - Compatível com LangChain HumanInTheLoopMiddleware

### Fluxo Completo

```
┌─ Agente recebe alert_id
│
├─ Decision Engine avalia
│  └─ Retorna UC08Decision com ações propostas
│
├─ Para cada ação proposta:
│  │
│  ├─ Se requires_approval=True:
│  │  │
│  │  ├─ approval_manager.request_approval()
│  │  │  ├─ Mostra ação e evidências
│  │  │  ├─ Pede aprovação
│  │  │  └─ Retorna True/False
│  │  │
│  │  ├─ Se aprovado:
│  │  │  │
│  │  │  ├─ approval_manager.execute_action()
│  │  │  │  ├─ Dry-run (dry_run=True)
│  │  │  │  │  └─ Registra em audit_log com status="dry_run"
│  │  │  │  ├─ Execução real (dry_run=False, approval_token=...)
│  │  │  │  │  └─ Registra em audit_log com status="executed"
│  │  │  │  └─ Retorna ActionResult
│  │  │  │
│  │  │  └─ Log: action_executed
│  │  │
│  │  └─ Se rejeitado:
│  │     └─ Log: approval_decision (rejected)
│  │
│  └─ Se requires_approval=False:
│     └─ Executa diretamente (ex: escalate_incident)
│
└─ Retorna UC08RunSummary
```

### Idempotência

**request_id** garante que ações não são duplicadas:

```python
# Primeira execução
revoke_token(
    token_id="token_001",
    request_id="uc08-abc123",
    reason="...",
    dry_run=False,
    approval_token="APPROVED-LOCAL-DEMO"
)
# Registra em audit_log com status="executed"

# Segunda execução com MESMO request_id
revoke_token(
    token_id="token_001",
    request_id="uc08-abc123",  # ← MESMO!
    reason="...",
    dry_run=False,
    approval_token="APPROVED-LOCAL-DEMO"
)
# Retorna ActionResult com status="duplicate"
# Não executa novamente!
```

---

## 📊 Estrutura de Dados

### UC08Decision

```python
@dataclass
class UC08Decision:
    alert_id: str                          # ID do alerta
    status: Literal[...]                   # "completed", "needs_human", "blocked", "error"
    summary: str                           # Resumo executivo
    evidence: list[Evidence]               # Evidências coletadas
    proposed_actions: list[ProposedAction] # Ações propostas
    action_executed: ProposedAction | None # Ação que foi realmente executada
    request_id: str                        # ID idempotente
    audit_ids: list[int]                   # IDs no audit_log
    requires_human: bool                   # Se precisa humano
    error_message: str | None              # Se houver erro
    limitations: list[str]                 # Limitações conhecidas
```

### Evidence

```python
@dataclass
class Evidence:
    claim: str                    # "Token foi usado em 3 serviços"
    source: str                   # "security_alert" | "open_incidents" | "policy" | "manual_review"
    confidence: str               # "low" | "medium" | "high"
    excerpt: str | None           # Trecho dos dados
```

### ProposedAction

```python
@dataclass
class ProposedAction:
    action_type: str              # "revoke_token" | "disable_service_account" | "escalate_incident" | "none"
    target_id: str | None         # ID do recurso a atuar (token_id, service_account_id, etc)
    reason: str                   # Por que propõe isso
    risk_level: str               # "low" | "medium" | "high" | "critical"
    requires_approval: bool       # Se precisa aprovação humana
    dry_run_result: dict | None   # Resultado de simulação
```

---

## 🔧 Integrações

### Com Tools do OpsPilot

O UC08 usa as seguintes tools:

| Tool | Tipo | Descrição |
|------|------|-----------|
| `get_security_alert` | Leitura | Carrega dados do alerta |
| `list_open_incidents` | Leitura | Lista incidentes abertos |
| `revoke_token` | Escrita (destrutiva) | Revoga token vazado |
| `disable_service_account` | Escrita (destrutiva) | Desabilita service account |
| `escalate_incident` | Escrita (administrativa) | Cria incidente escalado |

### Com Auditoria

Cada ação registra em `audit_log`:

```sql
INSERT INTO audit_log(
    request_id,           -- "uc08-abc123" (idempotência)
    actor,                -- "agent-or-human-operator"
    action,               -- "revoke_token"
    target,               -- "token_prod_001"
    dry_run,              -- 0 (false) ou 1 (true)
    status,               -- "executed", "dry_run", "duplicate", "blocked"
    details               -- JSON com motivo, resultado, etc
)
```

### Com LangSmith

Quando configurado, todos os passos são tracejados:

- Cada chamada de tool
- Raciocínio do agente
- Tempos e tokens
- Decisões e aprovações

Acesse: `https://smith.langchain.com/projects/opspilot-uc08-runs`

---

## ❓ Perguntas de Apresentação

### 1. Qual evidência autorizou a ação proposta?

**Resposta:**

O UC08 coleta evidências de múltiplas fontes:

```
Exemplo: Revogar token "token_prod_001"

Evidências coletadas:
1. [security_alert] Alerta de severidade 'high'
   → score base: 75
   
2. [security_alert] Token usado em 3 serviços diferentes
   → score +20 = 95
   
3. [open_incidents] Existem 3 incidentes abertos
   → qualifica para action

Critério ativado: score >= 80 AND len(incidents) > 0
                  95     >= 80    AND        3      > 0  ✓ SIM

Ação autorizada: REVOKE_TOKEN
```

Nunca há ação destrutiva sem evidência de pelo menos 2 fontes.

### 2. Qual seria o impacto de uma ação errada?

**Resposta:**

Cenário: Revogar token errado

| Impacto | Severidade | Mitigação |
|---------|-----------|-----------|
| Aplicações legítimas perdem autenticação | CRÍTICA | Dry-run revela impacto; aprovação humana valida |
| Serviço cai para usuários | ALTA | Auditoria rastreia quem aprovou |
| Dados inacessíveis temporariamente | MÉDIA | Request_id permite replay; reversão rápida |

**Proteções:**
- ✓ Dry-run simula sem alterar estado
- ✓ Aprovação humana revisa antes de executar
- ✓ audit_log registra tudo com actor, timestamp, details
- ✓ request_id permite reverter/diagnosticar

### 3. A idempotência foi garantida onde?

**Resposta:**

Idempotência é garantida via `request_id` em:

1. **Decision Engine** → gera `request_id=uc08-{uuid}`

2. **Dry-run** → registra com `dry_run=True`
   ```python
   audit_log: (request_id, action, dry_run=1, status="dry_run")
   ```

3. **Execução Real** → unique index previne duplicação
   ```sql
   CREATE UNIQUE INDEX idx_audit_request_action 
   ON audit_log(request_id, action) 
   WHERE dry_run = 0;
   ```

   Tentativa de executar 2× com mesmo request_id:
   ```python
   revoke_token(..., request_id="uc08-abc123", dry_run=False)
   # 1ª execução: sucesso, registra audit_log
   # 2ª execução: retorna ActionResult(status="duplicate")
   ```

### 4. O que aparece no trace e no audit log?

**Resposta:**

#### Audit Log (Banco de Dados)

```sql
SELECT * FROM audit_log WHERE action IN ('revoke_token', 'disable_service_account');

id | request_id    | actor  | action        | target         | dry_run | status   | details
---|---------------|--------|---------------|----------------|---------|----------|------------------------------------------
1  | uc08-abc123   | agent  | revoke_token  | token_prod_001 | 1       | dry_run  | {"reason": "..."}
2  | uc08-abc123   | agent  | revoke_token  | token_prod_001 | 0       | executed | {"reason": "...", "audit_id": 2}
```

#### LangSmith Trace

Estrutura hierárquica:

```
UC08 Run (opspilot_uc08)
├─ get_security_alert(SEC-001)
│  └─ Output: {alert_data}
├─ list_open_incidents()
│  └─ Output: [{incident1}, ...]
├─ Decision Engine Evaluation
│  ├─ Evidence: [Evidence(...), ...]
│  └─ Proposed Actions: [ProposedAction(...)]
├─ Approval Request
│  └─ Operator approved
└─ revoke_token(dry_run=True, approval_token=...)
   ├─ Input: {token_id, request_id, reason, ...}
   └─ Output: ActionResult(status="executed", audit_id=2)
```

### 5. Em que situação o agente deveria parar e pedir humano?

**Resposta:**

O agente **sempre** para e pede humano quando:

| Situação | Por quê | Exemplo |
|----------|---------|---------|
| `requires_approval=True` | Ação destrutiva | revoke_token, disable_service_account |
| Sem evidência suficiente | Falta de dados | Token com score < 50 |
| Type de alerta desconhecido | Incerteza | alert_type="novo_tipo_desconhecido" |
| Erro durante avaliação | Exceção | Exception durante scoring |
| Service account comprometida | Muito perigoso | Sempre escalate, nunca desabilita automático |

**Exemplo de bloqueio:**

```python
# Tentativa sem aprovação
result = revoke_token(
    token_id="token_001",
    request_id="uc08-abc",
    reason="...",
    dry_run=False,
    approval_token=None  # ← Falta!
)
# PermissionError: revoke_token exige approval_token válido para execução real
```

---

## ⚠️ Limitações Conhecidas

### 1. Decisão Determinística (sem LLM)

**Limitação:**
- Decision Engine usa lógica de regras, não LLM
- Não consegue raciocinar sobre casos complexos

**Mitigação:**
- Use `run_agent_uc08()` com LLM para raciocínio mais sofisticado
- Engine é mais rápido e previsível para casos simples

**Quando usar cada um:**
- **Engine:** Prototipagem rápida, testes, casos claros
- **Agent:** Produção, casos ambígos, raciocínio complexo

### 2. Sem Consultoria com Histórico

**Limitação:**
- Agente não consulta `audit_log` para histórico
- Não sabe se revogou este token antes

**Mitigação:**
- `request_id` idempotente previne duplicação
- Auditoria está lá para investigação posterior

**Como melhorar:**
```python
# Futuro: consultar audit recente
recent_actions = repo.get_audit_events("token_prod_001", limit=5)
if recent_actions:
    # Se já revogou nas últimas 24h, pular
```

### 3. Sem Alertas de Contexto Externo

**Limitação:**
- Decision Engine só vê dados do OpsPilot
- Não integra com sistemas externos (SIEM, email, etc)

**Por quê:**
- UC08 propositalmente evita integrações complexas
- Foco em governança local

**Como estender:**
```python
# Futuro: buscar eventos de SIEM
siem_events = fetch_from_siem(token_id)
for event in siem_events:
    engine.add_evidence(...)
```

### 4. Sem Rollback Automático

**Limitação:**
- Se revogou token errado, precisa fazer manualmente
- Sem função de "desfazer"

**Mitigação:**
- Aprovação humana valida antes
- Audit trail permite diagnosticar
- Dry-run simula sem risco

**Como melhorar:**
```python
# Futuro: reissue_token(request_id) para desfazer
def reissue_token(original_request_id):
    # Busca ação original
    # Cria novo token com mesmas permissões
```

### 5. Sem Notificação Automática

**Limitação:**
- Agente não envia email/Slack ao revogar
- Só registra em audit_log

**Por quê:**
- UC08 foca em core logic
- Notificações variam por org

**Como adicionar:**
```python
# Futuro: depois de execução
ExecutionLogger.log_action_executed(action, result)
# Trigger webhook/email notificando equipe de segurança
```

### 6. Score Simples (sem ML)

**Limitação:**
- Scoring usa regras hardcoded
- Sem aprendizado com histórico

**Trade-off:**
- Simples = previsível
- ML = complexo, difícil debugar

**Quando usar ML:**
- Se tiver 1000+ alertas históricos
- Se padrões são não-óbvios

### 7. Token de Demo Hardcoded

**Limitação:**
```python
approval_token = "APPROVED-LOCAL-DEMO"  # ← Hardcoded!
```

**Por quê:**
- UC08 é exercício educacional
- Em produção, seria OAuth + assinatura

**Em produção:**
```python
approval_token = request.headers.get("X-Approval-Token")
# Validar contra OPA ou policy engine
```

---

## 📚 Arquivos de Referência

| Arquivo | Descrição |
|---------|-----------|
| `uc08_models.py` | Modelos Pydantic (UC08Decision, Evidence, etc) |
| `uc08_decision_engine.py` | Lógica de scoring e decisão |
| `uc08_agent.py` | Agente LangChain com middleware HITL |
| `uc08_approvals.py` | ApprovalManager e ExecutionLogger |
| `main_uc08.py` | Entry point com CLI |
| `uc08_langsmith_config.py` | Integração com LangSmith |
| `UC08_LANGSMITH_SETUP.md` | Guia de setup de tracing |

---

## 🧪 Testes Sugeridos

### 1. Teste de Bloqueio

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
# Responda "N" quando pedir aprovação
# Resultado: ação não executada, UC08Decision.requires_human=True
```

### 2. Teste de Idempotência

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-compromised-sa --auto-approve
# Executará
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-compromised-sa --auto-approve
# Segunda vez: ActionResult(status="duplicate")
```

### 3. Teste de Auditoria

```bash
python -m opspilot.cli audit | jq '.[] | select(.action | contains("revoke"))'
# Mostra todos os revokes no audit_log
```

### 4. Teste com LangSmith

```bash
# Depois de configurar LangSmith (ver UC08_LANGSMITH_SETUP.md)
python -m opspilot.main_uc08 SEC-001 --scenario demo-leaked-token --auto-approve
# Veja em https://smith.langchain.com/projects/opspilot-uc08-runs
```

---

## 🔗 Referências

- **UC08 Requirements:** `use_cases/UC08_security_token_response.md`
- **OpsPilot Architecture:** `docs/ARCHITECTURE.md`
- **Policies & Governance:** `docs/SAFETY_MODEL.md`
- **LangChain Docs:** https://docs.langchain.com
- **LangSmith Docs:** https://docs.smith.langchain.com

---

**Última atualização:** Julho 2026  
**Status:** Implementação completa com todos os requisitos atendidos
