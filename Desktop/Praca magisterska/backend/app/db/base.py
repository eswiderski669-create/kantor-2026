# Single DeclarativeBase holds metadata for all tables — the same object Alembic uses for autogenerate.

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
