# ✅ LangSmith Configurado e Testado

## 📋 Credenciais Carregadas

```
LANGSMITH_TRACING=true ✓
LANGSMITH_ENDPOINT=https://api.smith.langchain.com ✓
LANGSMITH_API_KEY=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 ✓
LANGSMITH_PROJECT=OPSPILOT_SANDBOX_UC08 ✓
```

Estas estão salvas em `.env` (não comitar!)

---

## 🎯 Executar com LangSmith Habilitado

### Opção 1: Teste Rápido (Engine Only)

```bash
cd c:\git\sctec\opspilot_sandbox_base
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve
```

**O que vê:**
- Análise completa no terminal
- No final: URL do LangSmith dashboard

### Opção 2: Script de Teste (Recomendado)

```bash
python test_uc08_langsmith.py
```

Este script:
1. Verifica se LangSmith está habilitado
2. Executa cenário demo
3. Mostra URL do dashboard
4. Aguarda você visualizar

### Opção 3: Múltiplos Cenários

```bash
# Token vazado
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve

# Service account
python -m opspilot.main_uc08 SEC-002 --engine-only --scenario demo-compromised-sa --auto-approve

# Atividade suspeita
python -m opspilot.main_uc08 SEC-003 --engine-only --scenario demo-suspicious --auto-approve
```

---

## 🔍 Visualizar Traces no LangSmith

### Passo 1: Acessar Dashboard

Depois de executar um cenário, você verá algo como:

```
📊 RESULTADO DA AVALIAÇÃO UC08
═════════════════════════════════
🔗 LangSmith Trace: https://smith.langchain.com/projects/OPSPILOT_SANDBOX_UC08/runs
   (procure por run_id: uc08-engine-SEC-001)
```

### Passo 2: Clicar no Link

Acesse: **https://smith.langchain.com/projects/OPSPILOT_SANDBOX_UC08/runs**

Você verá uma lista de todos os runs:

```
Runs
├─ uc08-engine-SEC-001       [agent]  2026-07-21 14:30:45
├─ uc08-engine-SEC-002       [agent]  2026-07-21 14:30:32
└─ uc08-engine-SEC-003       [agent]  2026-07-21 14:30:20
```

### Passo 3: Clicar em um Run

Clique em qualquer run para ver detalhes:

```
Timeline
├─ Start UC08 Decision Engine
│  ├─ get_security_alert(SEC-001)
│  │  ├─ Input: {alert_id: "SEC-001"}
│  │  └─ Output: {severity: "high", ...}
│  ├─ list_open_incidents()
│  │  ├─ Input: {}
│  │  └─ Output: [{incident1}, ...]
│  └─ Evaluate with scoring
│     ├─ Calcular score: 95
│     └─ Propor ações: [revoke_token]
└─ End UC08 (total: 125ms)
```

---

## 📊 O Que Cada Coluna Significa

| Coluna | Significa |
|--------|-----------|
| **Name** | Nome do step (tool call, avaliação) |
| **Type** | Tipo (agent, tool, chain) |
| **Status** | ✓ sucesso, ✗ erro |
| **Time** | Duração em ms |
| **Tokens** | Tokens gastos (se LLM) |

---

## 🎓 Analisar um Trace

### 1. Ver Inputs/Outputs de uma Tool

Clique em uma tool (ex: `get_security_alert`):

```json
{
  "name": "get_security_alert",
  "input": {
    "alert_id": "SEC-001"
  },
  "output": {
    "id": "SEC-001",
    "alert_type": "leaked_token",
    "severity": "high",
    "affected_services": ["payment-api", "billing-service", "user-auth"]
  },
  "duration_ms": 5
}
```

### 2. Ver Raciocínio do Agente

Se usar agente LLM (não apenas engine), vê:

```
Model Input:
  "Processe o alerta SEC-001..."

Model Output:
  "Vou analisar evidências:
   1. Severidade alta
   2. Múltiplos serviços afetados
   3. Incidentes abertos
   
   Conclusão: Revogar token com aprovação"

Tokens: 234 prompt + 89 completion
```

### 3. Comparar Cenários

Abra 2 tabs lado a lado:
- Tab 1: demo-leaked-token (score 100)
- Tab 2: demo-suspicious (score 50)

Veja as diferenças em scoring e ações propostas.

---

## 🔧 Troubleshooting

### Runs não aparecem no dashboard?

**Solução:**
1. Aguarde 2-3 segundos após execução
2. Atualize a página (F5)
3. Verifique se `.env` tem LANGSMITH_TRACING=true

### "Autenticação falhou"?

**Solução:**
1. Verifique se API_KEY está correta (copiar/colar de novo)
2. Verifique se não tem espaços extras
3. Tente gerar nova chave em smith.langchain.com/settings

### Runs aparecem vazios?

**Solução:**
1. Clique em um run
2. Aguarde carregar
3. Se ainda vazio, tente outro run

---

## 💡 Dicas Avançadas

### 1. Usar Tags para Organizar

```python
# Futuro: adicionar tags ao run
with langsmith.Client() as client:
    run = client.create_run(..., tags=["uc08", "demo-leaked-token"])
```

### 2. Compartilhar Trace com Equipe

No dashboard:
1. Abra um run
2. Clique em "Share"
3. Copie link público
4. Compartilhe com colegas

### 3. Exportar Trace

Alguns runs têm opção de "Export":
1. Clique em run
2. Procure botão "Export"
3. Baixa JSON com toda traçabilidade

### 4. Filtrar por Duração

No dashboard:
- Filtro "Duration > 1000ms" mostra runs lentos
- Útil para otimização

---

## 📝 Próximos Passos

### Agora

```bash
# Teste script
python test_uc08_langsmith.py

# Depois vá ao dashboard e veja o run
```

### Hoje

```bash
# Execute os 3 cenários
python -m opspilot.main_uc08 SEC-001 --scenario demo-leaked-token --auto-approve
python -m opspilot.main_uc08 SEC-002 --scenario demo-compromised-sa --auto-approve
python -m opspilot.main_uc08 SEC-003 --scenario demo-suspicious --auto-approve

# Analise as diferenças no dashboard
```

### Esta Semana

```bash
# Teste com agente LLM (se tiver Ollama)
python -m opspilot.main_uc08 SEC-001 --scenario demo-leaked-token

# Veja raciocínio completo no LangSmith
```

---

## 🎯 O Que Avaliar no Trace

Quando apresentar para o professor, aponte:

1. **Timeline visual** - Mostra sequência de execução
2. **Tool inputs/outputs** - Transparência completa
3. **Duração de cada step** - Performance
4. **Request IDs** - Idempotência rastreada
5. **Status final** - Decisão e ações

---

## 📞 Referência

- **Dashboard:** https://smith.langchain.com/projects/OPSPILOT_SANDBOX_UC08/runs
- **Docs:** https://docs.smith.langchain.com
- **Seu projeto:** OPSPILOT_SANDBOX_UC08

---

**Status:** ✅ LangSmith Configurado e Testado  
**Data:** Julho 21, 2026  
**Pronto para:** Testes, análise, apresentação

Acesse o dashboard agora! 🚀
