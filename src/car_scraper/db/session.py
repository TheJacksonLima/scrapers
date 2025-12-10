from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from car_scraper.utils.config import settings

engine = create_engine(settings.DATABASE_URL, pool_size=5, max_overflow=5, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
