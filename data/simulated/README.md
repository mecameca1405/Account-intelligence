# Simulated Data

This directory contains simulated/synthetic data for testing and development.

## Contents

- `accounts_sample.json` — Sample company accounts for seeding the database
- `signals_sample.json` — Simulated commercial signals
- `scores_sample.json` — Pre-computed propensity scores

## Generating Sample Data

```bash
docker-compose exec backend python -c "
from app.database import SessionLocal, Base, engine
from app import models
from app.api.dependencies import hash_password
from datetime import datetime

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Create admin user
admin = models.User(
    email='admin@hpe.com',
    full_name='Admin HPE',
    role='admin',
    hashed_password=hash_password('Admin123!'),
)
db.add(admin)
db.commit()
print('✅ Admin user created: admin@hpe.com / Admin123!')
db.close()
"
```
