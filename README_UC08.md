# UC08: Resposta a Token Vazado e Service Account Perigosa

## 🎯 Objetivo

Implementar um **agente de IA** que responde automaticamente a alertas de segurança com:
- ✅ Análise estruturada de evidências
- ✅ Decisões determinísticas baseadas em scoring
- ✅ Aprovação humana para ações perigosas
- ✅ Simulação obrigatória (dry-run) antes de executar
- ✅ Auditoria completa de cada passo
- ✅ Idempotência via request_id

---

## 🚀 Começar em 30 Segundos

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

**Saída:**
```
📊 RESULTADO DA AVALIAÇÃO UC08
═════════════════════════════════════════════
📋 Alerta: SEC-001
Status: completed

📊 Evidências (3):
   1. [security_alert] Alerta com severidade 'high'
   2. [open_incidents] 3 incidentes abertos
   3. [security_alert] Token usado em 3 serviços

🎯 Ações Propostas (1):
   1. revoke_token
      Razão: Score 100 + incidentes
      Risco: high
      Requer aprovação: Yes
```

---

## 📁 Arquivo de Referência Rápida

| Doc | Tempo | Para Quem | Conteúdo |
|-----|-------|----------|----------|
| **UC08_QUICKSTART.md** | 5 min | Todos | 5 exemplos prontos |
| **UC08_RESUMO_PT.md** | 10 min | Apresentação | Resumo em Português |
| **UC08_IMPLEMENTATION.md** | 1h | Técnico | Lógica, Q&A, limitações |
| **UC08_ARCHITECTURE.md** | 1h | Design | Diagramas, componentes |
| **UC08_LANGSMITH_SETUP.md** | 5 min | Observabilidade | Setup de tracing |
| **UC08_INDEX.md** | 10 min | Referência | Índice completo |

---

## 🎓 3 Caminhos de Usar

### Path A: Decision Engine (Rápido)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

**Vantagens:**
- ⚡ Rápido (~100ms)
- 🔍 Determinístico (sem surpresas)
- 📊 Scoring transparente

**Desvantagens:**
- ❌ Sem raciocínio LLM

### Path B: Agente LLM (Inteligente)

```bash
python -m opspilot.main_uc08 SEC-001 --scenario demo-leaked-token
```

**Vantagens:**
- 🧠 Raciocínio tipo LLM
- 🎯 Flexível para casos complexos
- 🔗 Integrado com tools

**Desvantagens:**
- 🐢 Lento (5-30s)
- 🎲 Menos previsível

### Path C: Integração (Seu Sistema)

```python
from opspilot.main_uc08 import run
result = run(alert_id="...", json_output=True)
```

**Para:**
- Webhook/API callback
- Integração com SIEM
- Processamento em batch

---

## 🧠 Como Funciona: Lógica de Decisão

### Tipo 1: Token Vazado

```
Score = base_severity + adjustments

base_severity:
  • critical → 100
  • high     → 75
  • medium   → 50
  • low      → 25

adjustments:
  • Múltiplos serviços afetados → +20
  • Exposição > 2 horas → +20

Decisão:
  score >= 80 + incidentes abertos → REVOKE_TOKEN (requer aprovação)
  score >= 80 - incidentes abertos → ESCALATE_INCIDENT
  score < 80 → ESCALATE_INCIDENT ou NONE
```

### Tipo 2: Service Account Comprometida

```
⚠️  MUITO PERIGOSO

score >= 90 + múltiplos incidentes → DISABLE_SERVICE_ACCOUNT (requer aprovação)
Outro caso → ESCALATE_INCIDENT (sempre, sem exceção)

Princípio: Melhor ser cauteloso com service accounts
```

### Tipo 3: Atividade Suspeita

```
Sempre → ESCALATE_INCIDENT

Razão: Requer investigação manual, sem automação
```

---

## 🔒 Segurança em Camadas

### Camada 1: Aprovação Explícita

```python
if action.requires_approval:
    decision = ask_human("Aprovar? [s/N]")
    if not decision:
        return "BLOQUEADO"
```

### Camada 2: Dry-run Obrigatório

```python
# Passo 1: Simular
revoke_token(..., dry_run=True)
# Mostra resultado esperado

# Passo 2: Executar
revoke_token(..., dry_run=False, approval_token="APPROVED-...")
```

### Camada 3: Idempotência

```python
# Primeira execução
revoke_token(..., request_id="uc08-abc123")
# Registra em audit_log com status="executed"

# Tentativa duplicada
revoke_token(..., request_id="uc08-abc123")
# Retorna status="duplicate" (não executa novamente!)
```

### Camada 4: Auditoria Completa

```sql
SELECT * FROM audit_log 
WHERE request_id="uc08-abc123"
-- Mostra: who, when, what, dry_run, status, details
```

---

## 5️⃣ Exemplos de Uso

### 1️⃣ Teste Rápido

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

### 2️⃣ Apenas Simulação

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --dry-run
```

### 3️⃣ Aprovação Automática (Testes)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve
```

### 4️⃣ Aprovação Interativa

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
# Responda quando pedir: s (sim) ou N (não)
```

### 5️⃣ JSON para Integração

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --json | jq
```

---

## 📚 Arquivos de Código

```
src/opspilot/
├── uc08_models.py              Classes e tipos
├── uc08_decision_engine.py     Lógica de decisão
├── uc08_agent.py               Agente LangChain
├── uc08_approvals.py           Aprovação + Auditoria
├── uc08_langsmith_config.py    Observabilidade
└── main_uc08.py                CLI entry point
```

---

## ✅ Perguntas de Apresentação

**P1: Qual evidência autorizou a ação proposta?**

Resposta: Decision Engine coleta 3+ evidências (tipo de alerta, serviços afetados, incidentes abertos) e exibe cada uma com confiança.

**P2: Qual seria o impacto de uma ação errada?**

Resposta: Proteções em 4 camadas: dry-run (simula), aprovação (valida), idempotência (evita duplicação), auditoria (rastreia).

**P3: A idempotência foi garantida onde?**

Resposta: `request_id` + unique index no audit_log. Mesma ação 2x retorna "duplicate".

**P4: O que aparece no trace/audit_log?**

Resposta: Audit log tem cada ação. LangSmith (opcional) mostra timeline completa.

**P5: Quando deveria parar e pedir humano?**

Resposta: Sempre para ações destrutivas, sem evidência suficiente, ou incerteza.

---

## ⚠️ 7 Limitações Conhecidas

1. **Decision Engine é determinístico** (sem LLM)
2. **Sem consultoria de histórico** (audit_log existe, mas não consultado)
3. **Sem integração com SIEM** (foco local)
4. **Sem rollback automático** (documentado em auditoria)
5. **Sem notificações automáticas** (Slack, email, etc)
6. **Scoring simples** (regras, sem ML)
7. **Approval token hardcoded** (DEMO, usar OAuth em produção)

Ver `UC08_IMPLEMENTATION.md` para detalhes e mitigações.

---

## 📊 Estatísticas

```
Código Python:      ~1,780 linhas
Documentação:       ~2,000 linhas
Classes/Tipos:      15+
Funções:            40+
Cenários de demo:   3
Testes sugeridos:   5
Padrões usados:     8
```

---

## 🔗 Próximos Passos

### Hoje (30 min)
- [ ] Execute `UC08_QUICKSTART.md`
- [ ] Rode os 5 cenários
- [ ] Entenda o scoring

### Esta semana (2h)
- [ ] Leia `UC08_IMPLEMENTATION.md`
- [ ] Configure LangSmith
- [ ] Veja traces no dashboard

### Próximas semanas
- [ ] Integre com seu sistema
- [ ] Adapte scoring para seus alertas
- [ ] Adicione notificações

---

## 🎁 Bônus

```bash
# Ver instruções LangSmith
python -m opspilot.main_uc08 --setup-langsmith

# Ver audit_log
python -m opspilot.cli audit

# Help
python -m opspilot.main_uc08 --help
```

---

## 📞 Suporte

1. Veja `UC08_QUICKSTART.md` (rápido)
2. Veja `UC08_IMPLEMENTATION.md` (técnico)
3. Execute `--setup-langsmith` (instruções)

---

**Status:** ✅ Implementação completa  
**Documentação:** ✅ Completa  
**Testes:** ✅ Pronto para rodar  
**Produção:** ⚠️ Remover DEMO_APPROVAL_TOKEN e configurar OAuth

Acesse **UC08_INDEX.md** para índice completo.
