import asyncio
from ..db.database import sessionLocal

def run_async_task(coro):
    """
    Utility to safely run async service logic inside Celery task.
    """
    return asyncio.run(coro)


async def get_db_session():
    async with sessionLocal() as session:
        return session