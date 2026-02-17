# Phase 9.8.2 Schema & Migration Design (V1)
Timestamp: 2026-02-11T23:45:00+09:00 (JST)

## 概要
`ajson` のセキュリティ設定 (Allowlist/Approval) を SQLite で永続化するためのスキーマ設計。
自己完結型 (Zero-config) を目指し、アプリ起動時に自動適用 (`CREATE TABLE IF NOT EXISTS`) される。

## 1. Schema Definitions

### 1-A. `requests` (Approval Requests)
| Column | Type | Nullable | Description |
|---|---|---|---|
| `request_id` | TEXT | PK | UUID v4 |
| `operation` | TEXT | NO | e.g. "connect api.openai.com" |
| `category` | TEXT | NO | e.g. "network" |
| `reason` | TEXT | NO | User provided justification |
| `status` | TEXT | NO | 'pending', 'approved', 'denied' |
| `metadata` | TEXT | NO | JSON (context info) |
| `created_at` | TEXT | NO | ISO8601 (UTC, Timezone-aware) |

### 1-B. `grants` (Approved Permissions)
| Column | Type | Nullable | Description |
|---|---|---|---|
| `grant_id` | TEXT | PK | UUID v4 |
| `request_id` | TEXT | FK | Link to `requests.request_id` |
| `scope` | TEXT | NO | JSON List (e.g. `["api.openai.com"]`) |
| `expires_at` | TEXT | NO | ISO8601 (UTC) |
| `created_at` | TEXT | NO | ISO8601 (UTC) |

### 1-C. `allowlist_rules` (Static Rules Persistence)
| Column | Type | Nullable | Description |
|---|---|---|---|
| `rule_id` | TEXT | PK | UUID v4 |
| `host_pattern`| TEXT | NO | e.g. "*.google.com" |
| `port` | INTEGER | NO | 0 = Any, 443 = HTTPS |
| `reason` | TEXT | NO | Admin note |
| `created_at` | TEXT | NO | ISO8601 (UTC) |

## 2. Migration Strategy
- **Version Control**: なし (MVP)。
- **Strategy**: `CREATE TABLE IF NOT EXISTS`。
- **Rollback**: `rm data/approvals.db` (データ消失許容)。
- **Compatibility**: Pydantic V2/Datetime Deprecation 対応済（UTC aware）。

## 3. Data Location
- Path: `data/approvals.db`
- Backup: 必要に応じてファイルコピー。
- Git: `.gitignore` に追加済み。
