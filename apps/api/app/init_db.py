import asyncio
from sqlalchemy import text
from .db import engine, Base
from .models import *

async def main():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        await conn.run_sync(Base.metadata.create_all)
        # Hypertables are optional because the schema must also work on ordinary PostgreSQL.
        for table in ("rank_measurements", "cwv_measurements", "gsc_measurements"):
            try:
                await conn.execute(text(
                    f"SELECT create_hypertable('{table}', 'observed_at', if_not_exists => TRUE)"
                ))
            except Exception:
                pass
asyncio.run(main())
