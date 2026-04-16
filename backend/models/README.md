# ORM Models - Message Reminder System

This directory contains SQLAlchemy ORM models for the Message Reminder System.

## Models

### Message Model (`message.py`)

The Message model maps to the `message_table` database table and represents notification messages in the system.

#### Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| id | BigInteger | No | Primary key, auto-increment |
| rule_code | String(50) | No | Rule code (e.g., CHK_TRD_004) |
| title | String(200) | No | Notification title |
| count | Integer | No | Number of pending items |
| last_updated | TIMESTAMP | No | Last update time |
| status | String(20) | No | Scan status (success/timeout/error) |
| priority | String(20) | No | Priority (normal/high/critical) |
| target_roles | JSON | No | Target recipient roles (JSON array) |
| metadata_ | JSON | Yes | Extended metadata (JSON object) |
| created_at | TIMESTAMP | No | Creation time (auto-generated) |
| updated_at | TIMESTAMP | No | Update time (auto-updated) |

#### Indexes

- `idx_rule_code`: Index on rule_code for fast rule-based queries
- `idx_last_updated`: Index on last_updated for time-based sorting
- `idx_status`: Index on status for status filtering

#### Methods

- `to_dict()`: Converts the model instance to a dictionary
- `__repr__()`: String representation of the model

#### Usage Example

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.message import Message, Base

# Create engine and session
engine = create_engine('postgresql://user:password@localhost/dbname')
Session = sessionmaker(bind=engine)
session = Session()

# Create a new message
message = Message(
    rule_code='CHK_TRD_004',
    title='当日交易未复核',
    count=15,
    last_updated=datetime.now(),
    status='success',
    priority='normal',
    target_roles=['BO_Operator', 'BO_Supervisor'],
    metadata_={'additional_info': 'test'}
)

session.add(message)
session.commit()

# Query messages
messages = session.query(Message).filter_by(status='success').all()

# Convert to dict
message_dict = message.to_dict()
```

#### Notes

- The `metadata_` field is mapped to the database column `metadata` to avoid conflicts with SQLAlchemy's reserved `metadata` attribute
- The model uses `BigInteger` for PostgreSQL but falls back to `Integer` for SQLite compatibility in tests
- JSON fields (`target_roles` and `metadata_`) automatically serialize/deserialize Python objects

## Testing

Run unit tests for the Message model:

```bash
cd backend
python -m pytest tests/test_message_model.py -v --cov=models
```

Current test coverage: **100%**

## Dependencies

- SQLAlchemy 2.0+
- PostgreSQL 14+ (production)
- SQLite (testing)

## Future Models

The following models will be added in subsequent tasks:

- `RuleConfig`: Rule configuration model
- `TaskExecutionLog`: Task execution log model
- `AuditLog`: Audit log model
