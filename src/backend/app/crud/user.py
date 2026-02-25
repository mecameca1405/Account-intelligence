from ..models.user import User
from .base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CRUDUser(CRUDBase[User]):

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


user_crud = CRUDUser(User)

