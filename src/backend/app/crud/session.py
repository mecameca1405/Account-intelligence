from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_session import UserSession


async def revoke_all_user_sessions(
    db: AsyncSession,
    user_id: int
):
    await db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user_id,
            UserSession.revoked == False
        )
        .values(revoked=True)
    )
    await db.commit()