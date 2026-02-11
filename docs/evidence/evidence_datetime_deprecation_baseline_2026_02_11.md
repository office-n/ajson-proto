# Evidence: Datetime Deprecation Baseline
Timestamp: 2026-02-11T19:35:00+09:00

## 1. Environment
- **Python Version**: 3.12.8
- **Commit SHA**: 9d98e598ebb7a4c9b6a98e1dd7671567bab8ea25

## 2. Current Warnings (pytest -q)
```
summary ===============================
ajson/models.py:45
  .ajson/models.py:45: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/
    class Mission(BaseModel):

(Other Pydantic warnings omitted)

tests/test_approval_sqlite.py::test_create_and_get_pending
  .ajson/hands/approval_sqlite.py:110: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    created_at=datetime.utcnow().isoformat()

tests/test_approval_sqlite.py::test_approve_request_creates_grant
  .ajson/hands/approval_sqlite.py:162: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat(),

tests/test_audit_logger.py::test_log_request_created
  .ajson/hands/audit_logger.py:56: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    "timestamp": datetime.utcnow().isoformat(),
```

## 3. Hit List (grep "utcnow\(|utcfromtimestamp\(")
```
./ajson/hands/audit_logger.py:56:            "timestamp": datetime.utcnow().isoformat(),
./ajson/hands/approval_sqlite.py:110:            created_at=datetime.utcnow().isoformat()
./ajson/hands/approval_sqlite.py:162:            expires_at=(datetime.utcnow() + timedelta(hours=1)).isoformat(),
./ajson/hands/approval_sqlite.py:163:            created_at=datetime.utcnow().isoformat()
./ajson/hands/approval_sqlite.py:214:        if datetime.utcnow() > expires_at:
./ajson/hands/approval_sqlite.py:225:        now = datetime.utcnow().isoformat()
```
