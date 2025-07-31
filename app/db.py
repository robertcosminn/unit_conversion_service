"""Single responsibility: database engine and helper functions."""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import Base, ConversionLog

# SQLite file in project root; swap with PostgreSQL URI in prod
ENGINE = create_engine("sqlite:///conversions.sqlite3", echo=False, future=True)


def init_db() -> None:
    """Create tables if they do not exist."""
    Base.metadata.create_all(ENGINE)


@contextmanager
def get_session() -> Session:
    """Context-manager yields a SQLAlchemy session and commits on exit."""
    session: Session = Session(ENGINE)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def log_conversion(category: str, src_value: float, src_unit: str,
                   dst_unit: str, result: float) -> None:
    """Persist one conversion row."""
    with get_session() as s:
        s.add(
            ConversionLog(
                category=category,
                src_value=src_value,
                src_unit=src_unit,
                dst_unit=dst_unit,
                result=result,
            )
        )
