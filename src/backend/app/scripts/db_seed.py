from ..core.config import settings
print("DATABASE_URL:", settings.DATABASE_URL)

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import sessionLocal
from ..models.user_role import UserRole
from ..models.region import Region




async def seed():
    async with sessionLocal() as db:
        db.add_all([
            UserRole(name="admin", description="System administrator"),
            UserRole(name="manager", description="Regional manager"),
            UserRole(name="user", description="Standard user"),
        ])

        db.add_all([
            Region(name="North America"),
            Region(name="Latin America"),
            Region(name="Europe"),
            Region(name="Asia Pacific"),
        ])

        await db.commit()


if __name__ == "__main__":
    print("DATABASE_URL:", settings.DATABASE_URL)
    asyncio.run(seed())