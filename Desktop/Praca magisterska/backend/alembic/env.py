# Model metadata from application code; migration URL from `alembic.ini`
# (synchronous URL in alembic.ini, e.g. postgresql+psycopg - not asyncpg).
# Optional: set ALEMBIC_SYNC_URL to override (e.g. postgresql+psycopg://...@postgres:5432/... in Docker).

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.config import settings
from app.db.base import Base
from app.models import ChatSession, Document, User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    env_url = os.environ.get("ALEMBIC_SYNC_URL", "").strip()
    if env_url:
        return env_url
    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url and ini_url.strip():
        return ini_url.strip()
    return settings.database_url_sync


def run_migrations_offline() -> None:
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {})
    if config.get_main_option("sqlalchemy.url"):
        section = {**section, "sqlalchemy.url": get_sync_url()}
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
