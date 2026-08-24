# API do sistema

Rodar:

```bash
uvicorn opspilot.api:app --reload --port 8088
```

Abrir:

```text
http://localhost:8088/docs
```

## Endpoints principais

### Leitura

- `GET /api/tickets/{ticket_id}`
- `GET /api/services/{service_id}/health`
- `GET /api/services/{service_id}/deploys`
- `GET /api/feature-flags/{flag_key}`
- `GET /api/users/{user_id}/permissions`
- `GET /api/pipelines/{run_id}`
- `GET /api/billing/{account_id}`
- `GET /api/data-pipelines/{pipeline_id}`
- `GET /api/security-alerts/{alert_id}`
- `GET /api/incidents?service_id=...`
- `GET /api/audit`

### Escrita controlada

- `POST /api/services/{service_id}/restart`
- `POST /api/services/{service_id}/scale`
- `POST /api/feature-flags/{flag_key}/rollout`
- `POST /api/users/{user_id}/invalidate-cache`
- `POST /api/users/{user_id}/sync-role`
- `POST /api/pipelines/{run_id}/rerun`
- `POST /api/pipelines/{run_id}/quarantine-test`
- `POST /api/billing/{account_id}/credit-memo`
- `POST /api/data-pipelines/{pipeline_id}/reprocess`
- `POST /api/data-pipelines/{pipeline_id}/watermark`
- `POST /api/security/tokens/{token_id}/revoke`
- `POST /api/security/service-accounts/{service_account_id}/disable`
- `POST /api/incidents/{incident_id}/escalate`

### Webhook genérico

- `POST /webhooks/events`

## Corpo comum para escrita

```json
{
  "request_id": "uc04-001",
  "reason": "motivo operacional",
  "dry_run": true,
  "approval_token": null
}
```
