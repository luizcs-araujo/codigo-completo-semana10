# 🎯 UC08 - COMECE AQUI

**Você tem 5 minutos?** Siga este guia! ⏱️

---

## 📋 Pré-requisitos (1 minuto)

Execute no PowerShell:

```bash
cd c:\git\sctec\opspilot_sandbox_base
pip install -e .
python -m opspilot.seed
```

---

## 🚀 Teste Rápido (3 minutos)

Execute cada um separadamente:

### Cenário 1
```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token --auto-approve
```

### Cenário 2
```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-002 --engine-only --scenario demo-compromised-sa --auto-approve
```

### Cenário 3
```bash
chcp 65001 | Out-Null; python -m opspilot.main_uc08 SEC-003 --engine-only --scenario demo-suspicious --auto-approve
```

---

## ✅ Você Deve Ver

```
📊 RESULTADO DA AVALIAÇÃO UC08
═══════════════════════════════════════════════════════════

📋 Alerta: SEC-001
Status: completed

📊 Evidências (3): [lista de evidências]
🎯 Ações Propostas (1): [ações propostas com scoring]
```

---

## 📚 Ler Depois

1. `UC08_STARTED.md` - Instruções completas
2. `UC08_FINAL_SUMMARY.md` - Resumo executivo
3. `UC08_RESUMO_PT.md` - Para apresentação

---

## ❓ 5 Perguntas de Apresentação

Responder em `UC08_FINAL_SUMMARY.md`

---

**Tudo OK?** Você está pronto! 🎉

Próxima etapa: Ler documentação e preparar apresentação.
