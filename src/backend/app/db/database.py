from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from ..core.config import settings

engine = create_async_engine(settings.DATABASE_URL)
sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

import app.models
