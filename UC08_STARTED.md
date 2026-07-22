# ✅ UC08 - Pronto para Usar!

**Status:** ✅ Testado e Funcionando  
**Data:** Julho 21, 2026

---

## 🚀 Setup Inicial (1 minuto)

### 1. Instalar dependências

```bash
cd c:\git\sctec\opspilot_sandbox_base
pip install -e .
```

**Esperado:** `Successfully installed opspilot-sandbox`

### 2. Inicializar banco de dados

```bash
python -m opspilot.seed
```

**Esperado:** `Banco inicializado em .opspilot\opspilot.sqlite3`

### 3. IMPORTANTE: Configure o PowerShell para UTF-8

```bash
chcp 65001
```

Isso permite que o Python exiba emojis corretamente no Windows.

---

## 🎯 Executar Agora (30 segundos)

### Cenário 1: Token Vazado (Alta Severidade)

```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve
```

**O que vê:**
- Score: 75-100
- Ação: Pode ser revoke_token (com aprovação) ou escalate
- Evidências: 3+ coletadas

### Cenário 2: Service Account Comprometida (CRÍTICO)

```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-002 --engine-only --scenario demo-compromised-sa --auto-approve
```

**O que vê:**
- Score: 100 (crítico)
- Ação: disable_service_account (requer aprovação)
- Aviso: REQUER REVISÃO HUMANA
- Dry-run: Simulado antes de execução

### Cenário 3: Atividade Suspeita (Média)

```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-003 --engine-only --scenario demo-suspicious --auto-approve
```

**O que vê:**
- Score: 50 (médio)
- Ação: escalate_incident
- Evidências: Requer investigação manual

---

## 🔍 Analisar Resultado

Cada execução mostra:

```
📊 RESULTADO DA AVALIAÇÃO UC08
═══════════════════════════════════════════════════════════

📋 Alerta: SEC-001
Status: completed

📊 Evidências (3):
   1. [security_alert] Alerta com severidade...
   2. [open_incidents] Existem 2 incidentes...
   3. [policy] Critério de decisão aplicado

🎯 Ações Propostas (1):
   1. revoke_token
      Razão: Score 100 + incidentes
      Risco: high
      Requer aprovação: True
```

---

## 📝 Testar Bloqueio (sem aprovação)

```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
# Responda "N" quando pedir aprovação
```

**Resultado:**
- Ação NÃO executada
- `requires_human: True`
- UC08Decision retorna bloqueado

---

## 📊 Ver Audit Log

```bash
python -m opspilot.cli audit
```

Mostra todas as ações registradas no banco.

---

## 🎁 Bônus: JSON Output

```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --json
```

Retorna JSON estruturado para integração com outros sistemas.

---

## ⚠️ Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'opspilot'"

**Solução:** Execute `pip install -e .`

### Erro: "no such table: security_alerts"

**Solução:** Execute `python -m opspilot.seed`

### Emojis não aparecem no Windows

**Solução:** Execute `chcp 65001` antes de rodar

### LangSmith: "Unrecognized run_type"

**Solução:** Já corrigido! Execute `pip install -e . --force-reinstall`

---

## 🎯 Próximos Passos

1. ✅ Execute os 3 cenários acima
2. ✅ Entenda os scores (75, 100, 50)
3. ✅ Teste bloqueio (responder "N")
4. ✅ Leia `UC08_FINAL_SUMMARY.md`
5. ✅ Prepare apresentação

---

## 📚 Documentação

| Arquivo | Quando |
|---------|--------|
| UC08_FINAL_SUMMARY.md | Antes de apresentar |
| UC08_RESUMO_PT.md | Para entender em PT |
| UC08_IMPLEMENTATION.md | Para detalhes técnicos |

---

## ✅ Checklist

- [ ] `pip install -e .` executado
- [ ] `python -m opspilot.seed` executado
- [ ] Cenário 1 rodou com sucesso
- [ ] Cenário 2 rodou com sucesso
- [ ] Cenário 3 rodou com sucesso
- [ ] Testei bloqueio (responder "N")
- [ ] Entendi o scoring
- [ ] Li a documentação

---

**Status:** ✅ Pronto para apresentar!

Execute agora e boa sorte! 🚀
