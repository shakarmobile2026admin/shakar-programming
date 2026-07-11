from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging
from typing import Generator

from src.config import config

logger = logging.getLogger(__name__)

# ایجاد موتور
engine = create_engine(
    config.DATABASE_URL,
    poolclass=QueuePool,
    **config.SQLALCHEMY_ENGINE_OPTIONS
)

# ایجاد Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_session() -> Session:
    """بازگرداندن جلسه دیتابیس"""
    return SessionLocal()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager برای جلسات دیتابیس"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"خطا در دیتابیس: {str(e)}")
        raise
    finally:
        db.close()


def init_db():
    """ایجاد تمام جداول"""
    from src.database.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("جداول دیتابیس با موفقیت ایجاد شدند")


def drop_all_tables():
    """حذف تمام جداول (فقط برای توسعه)"""
    from src.database.models import Base
    Base.metadata.drop_all(bind=engine)
    logger.warning("تمام جداول دیتابیس حذف شدند")


def test_connection() -> bool:
    """تست اتصال به دیتابیس"""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        logger.info("اتصال به دیتابیس موفق بود")
        return True
    except Exception as e:
        logger.error(f"خطا در اتصال به دیتابیس: {str(e)}")
        return False
