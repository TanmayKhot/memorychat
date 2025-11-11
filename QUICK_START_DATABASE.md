# Quick Start: Database Testing

## Method 1: Interactive Inspector (Easiest)

```bash
cd memorychat
backend/.venv/bin/python scripts/inspect_database.py
```

Then select:
- Option 1: View table schemas
- Option 2: View table data
- Option 3: View record counts
- Option 4: View relationships

## Method 2: SQLite Command Line

```bash
cd memorychat
sqlite3 data/sqlite/memorychat.db
```

Then run:
```sql
-- View all tables
.tables

-- View schema
.schema users

-- Query data
SELECT * FROM users;
SELECT * FROM memory_profiles;
SELECT * FROM chat_sessions;
```

## Method 3: Quick Python Check

```bash
cd memorychat/backend
.venv/bin/python -c "
from database.database import SessionLocal
from services.database_service import DatabaseService

db = SessionLocal()
service = DatabaseService(db)

# Check users
users = db.query(service.db.query(User).all())
print(f'Users: {len(users)}')

# Check demo user
user = service.get_user_by_email('demo@local')
print(f'Demo user: {user.username if user else \"Not found\"}')

db.close()
"
```

## View Complete Guide

See `docs/database_testing_guide.md` for comprehensive instructions.
