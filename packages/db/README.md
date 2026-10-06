# DB package

The database schema is owned by `apps/api/app/models.py` for this starter.
Run `apps/api/app/init_db.py` after PostgreSQL/TimescaleDB is available.

For a larger deployment, move these definitions into Alembic migrations and add Timescale hypertables:
- rank_measurements
- cwv_measurements
- page_audit_results
- site_events
