from __future__ import annotations
from pathlib import Path
import sqlite3
from .config import get_settings

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS tickets(
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  service_id TEXT NOT NULL,
  user_id TEXT,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  description TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS services(
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  environment TEXT NOT NULL,
  status TEXT NOT NULL,
  error_rate REAL NOT NULL,
  latency_ms INTEGER NOT NULL,
  replicas INTEGER NOT NULL,
  last_deploy_id TEXT
);
CREATE TABLE IF NOT EXISTS users(
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  permissions TEXT NOT NULL,
  permission_cache_state TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feature_flags(
  key TEXT PRIMARY KEY,
  service_id TEXT NOT NULL,
  percentage INTEGER NOT NULL,
  owner TEXT NOT NULL,
  last_changed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS deployments(
  id TEXT PRIMARY KEY,
  service_id TEXT NOT NULL,
  version TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  commit_sha TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pipeline_runs(
  id TEXT PRIMARY KEY,
  repo TEXT NOT NULL,
  branch TEXT NOT NULL,
  status TEXT NOT NULL,
  failed_job TEXT,
  failed_tests TEXT NOT NULL,
  duration_sec INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS billing_accounts(
  id TEXT PRIMARY KEY,
  customer TEXT NOT NULL,
  balance_cents INTEGER NOT NULL,
  duplicate_charge_cents INTEGER NOT NULL,
  dispute_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS data_pipelines(
  id TEXT PRIMARY KEY,
  dataset TEXT NOT NULL,
  status TEXT NOT NULL,
  failed_partition TEXT,
  watermark TEXT NOT NULL,
  last_error TEXT
);
CREATE TABLE IF NOT EXISTS security_alerts(
  id TEXT PRIMARY KEY,
  alert_type TEXT NOT NULL,
  subject TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  token_id TEXT,
  service_account_id TEXT,
  details TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS incidents(
  id TEXT PRIMARY KEY,
  service_id TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  summary TEXT NOT NULL,
  owner TEXT
);
CREATE TABLE IF NOT EXISTS audit_log(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  dry_run INTEGER NOT NULL,
  status TEXT NOT NULL,
  details TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_request_action ON audit_log(request_id, action) WHERE request_id IS NOT NULL AND dry_run = 0;
CREATE TABLE IF NOT EXISTS events(
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  source TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or get_settings().db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db(db_path: Path | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
