from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config.settings import settings

engine = create_engine(settings.postgres_dsn, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
