from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from ..core.config import settings
from sqlalchemy import create_engine

engine = create_async_engine(settings.DATABASE_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,  # postgresql+psycopg2://
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

import app.models
