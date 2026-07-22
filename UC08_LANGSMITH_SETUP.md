# Configuração LangSmith para UC08

## O que é LangSmith?

LangSmith é uma plataforma de observabilidade para aplicações LLM. Permite:
- Ver todos os traços de execução do agente
- Debugar decisões passo-a-passo
- Monitorar uso de tokens e latência
- Compartilhar runs com a equipe

## Setup Rápido (5 minutos)

### 1. Criar conta no LangSmith

Acesse: https://smith.langchain.com

Clique em **"Sign up"** e complete o cadastro com email/senha.

### 2. Gerar API Key

- No dashboard, clique no ícone de **configurações** (engrenagem) no canto superior direito
- Selecione **"API Keys"**
- Clique em **"+ Create API Key"**
- Copie a chave gerada (começa com `sk_...`)

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` no diretório raiz do projeto (ou edite se já existe):

```bash
# .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=sk_...  # Cole sua chave aqui
LANGSMITH_PROJECT=opspilot-uc08-runs
OPSPILOT_DB_PATH=.opspilot/opspilot.sqlite3
OLLAMA_MODEL=qwen3:4b
```

⚠️ **NÃO COMITE o .env com sua chave!** Adicione ao `.gitignore`:

```
.env
.env.local
```

### 4. Inicializar banco de dados

```bash
python -m opspilot.seed
```

### 5. Executar agente com tracing

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only
```

Você verá:
```
✓ LangSmith configurado para projeto: opspilot-uc08-runs
🚀 Iniciando UC08 com Decision Engine...
```

### 6. Ver o trace

Acesse: https://smith.langchain.com/projects/opspilot-uc08-runs

Você verá cada run em lista. Clique em um para ver detalhes.

## Exemplos de Uso

### Scenario 1: Demo com Decision Engine (determinístico)

```bash
python -m opspilot.main_uc08 SEC-001 --engine-only --scenario demo-leaked-token
```

**O que vê no LangSmith:**
- Nenhuma chamada ao modelo (engine é determinístico)
- Decisões lógicas armazenadas
- Audit trail completo

### Scenario 2: Com Agente LLM (requer Ollama)

```bash
python -m opspilot.main_uc08 SEC-001 --auto-approve
```

**O que vé no LangSmith:**
- Chamadas ao modelo Ollama
- Argumentos e respostas de cada tool
- Raciocínio do agente
- Tempo de cada operação

### Scenario 3: Com Aprovação Interativa

```bash
python -m opspilot.main_uc08 SEC-001
```

Quando pedir aprovação, digite `s` e aperte Enter. LangSmith capture todo o fluxo incluindo a pausa para aprovação.

### Scenario 4: Output JSON (para integração)

```bash
python -m opspilot.main_uc08 SEC-001 --json
```

Retorna resultado estruturado que pode ser parseado por outros sistemas.

## Visualizar Setup Instructions

Se esqueceu da configuração, execute:

```bash
python -m opspilot.main_uc08 --setup-langsmith
```

Mostrará instruções completas novamente.

## Estrutura do Trace

Quando executa um run, LangSmith captura:

```
├─ Run Principal (opspilot_uc08)
│  ├─ get_security_alert (tool call)
│  │  ├─ Input: alert_id=SEC-001
│  │  └─ Output: {alert_data}
│  ├─ list_open_incidents (tool call)
│  │  ├─ Input: (no params)
│  │  └─ Output: [{incident1}, {incident2}]
│  ├─ Decision Engine Evaluation
│  │  ├─ Evidence Collected (5 items)
│  │  └─ Actions Proposed
│  └─ revoke_token (dry_run=True)
│     ├─ request_id: uc08-xxxxx
│     └─ audit_log entry created
```

## Troubleshooting

### "LANGSMITH_API_KEY não configurada"

Verifique:
- [ ] .env existe no diretório raiz
- [ ] LANGSMITH_API_KEY está no .env
- [ ] Não há espaços extras ao redor da chave

### "Runs não aparecem no dashboard"

Verifique:
- [ ] LANGSMITH_TRACING=true no .env
- [ ] LANGSMITH_PROJECT correto
- [ ] Aguarde 2-3 segundos após execução

### "Erro de autenticação"

- [ ] Chave de API está correta?
- [ ] Tente gerar uma nova chave no dashboard
- [ ] Verifique se a conta está ativa

## Dados Capturados no Trace

Cada run captura automaticamente:

| Dados | Descrição |
|-------|-----------|
| Run ID | Identificador único |
| Timestamp | Quando executou |
| Duração | Tempo total |
| Tools Usadas | Quais tools foram chamadas |
| Inputs/Outputs | Dados de entrada e saída |
| Erros | Se houver exceções |
| Request IDs | Para idempotência e auditoria |
| Audit Log | Mudanças de estado |

## Limpando Runs (Opcional)

Se fez muitos testes, pode limpar:

1. No dashboard, abra o projeto
2. Selecione múltiplos runs (checkbox)
3. Clique em "Delete"

Ou deixe tudo - LangSmith mantém histórico ilimitado na maioria dos planos.

## Próximos Passos

Agora que tem tracing:

1. Execute todos os cenários e analise os traces
2. Compare tempo e tokens entre eles
3. Identifique gargalos (se houver)
4. Use traces para debugging de decisões

## Referências

- **LangSmith Docs:** https://docs.smith.langchain.com
- **LangChain Docs:** https://docs.langchain.com
- **UC08 Guide:** Veja UC08_IMPLEMENTATION.md

---

**Dúvidas?** Execute `python -m opspilot.main_uc08 --setup-langsmith` novamente.
