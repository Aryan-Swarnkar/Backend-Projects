from sqlalchemy import create_engine
from app.config import settings
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
  bind=engine,
  autoflush=False,
  autocommit=False
)

class Base(DeclarativeBase):
  pass

def get_db():
  session = SessionLocal()
  try:
    yield session
  finally:
    session.close()