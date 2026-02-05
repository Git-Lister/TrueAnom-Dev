from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.config.settings import settings

engine = create_engine(settings.postgres_dsn, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


print(">> DEBUG POSTGRES_DSN:", settings.postgres_dsn)

engine = create_engine(settings.postgres_dsn, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

