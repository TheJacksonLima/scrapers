import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# alembic/env.py
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool, engine_from_config

# --- torne o pacote car_scraper importável ---
import sys, pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]  # .../car_scraper
sys.path.insert(0, str(BASE_DIR))

# --- imports do seu projeto ---
from car_scraper.db.models.base import Base
from car_scraper.db.session import engine              # seu engine SQLAlchemy
from car_scraper.db.models import *                    # garante que todos os modelos carreguem

# Config Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = str(engine.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": str(engine.url)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
