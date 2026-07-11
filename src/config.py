import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# بارگذاری متغیرهای محیطی
load_dotenv()

class Config:
    """کلاس پیکربندی اصلی"""
    
    # اطلاعات برنامه
    APP_NAME = os.getenv("APP_NAME", "نرم‌افزار حسابداری شاکر")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION = "نرم‌افزار حسابداری و مدیریت فروشگاه حرفه‌ای"
    
    # پایگاه داده
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/shakar_db"
    )
    DATABASE_DEBUG = os.getenv("DATABASE_DEBUG", "False").lower() == "true"
    
    # امنیت
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key")
    
    # مسیرها
    BASE_DIR = Path(__file__).parent.parent
    BACKUP_PATH = Path(os.getenv("BACKUP_PATH", BASE_DIR / "backups"))
    LOG_PATH = Path(os.getenv("LOG_PATH", BASE_DIR / "logs"))
    
    # ایجاد دایرکتوری‌های لازم
    BACKUP_PATH.mkdir(exist_ok=True)
    LOG_PATH.mkdir(exist_ok=True)
    
    # نسخه پشتی
    BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", 24))  # ساعت
    BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 30))
    
    # لاگ
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # درگاه پرداخت
    PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "https://api.payment-gateway.com")
    PAYMENT_GATEWAY_KEY = os.getenv("PAYMENT_GATEWAY_KEY", "")
    PAYMENT_GATEWAY_SECRET = os.getenv("PAYMENT_GATEWAY_SECRET", "")
    
    # کارتخوان
    CARD_READER_PORT = os.getenv("CARD_READER_PORT", "/dev/ttyUSB0")
    CARD_READER_BAUDRATE = int(os.getenv("CARD_READER_BAUDRATE", 9600))
    
    # سایت و فروشگاه آنلاین
    WEBSITE_API_URL = os.getenv("WEBSITE_API_URL", "https://api.website.com")
    WEBSITE_API_KEY = os.getenv("WEBSITE_API_KEY", "")
    
    # گاه شماری
    CALENDAR_TYPE = os.getenv("CALENDAR_TYPE", "jalali")  # jalali یا gregorian
    
    # مالیات و عوارض
    TAX_RATE = float(os.getenv("TAX_RATE", 0.09))
    VAT_RATE = float(os.getenv("VAT_RATE", 0.00))
    
    # UI
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 800
    
    # Database SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DATABASE_DEBUG
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }


class DevelopmentConfig(Config):
    """پیکربندی توسعه"""
    DEBUG = True
    DATABASE_DEBUG = True


class ProductionConfig(Config):
    """پیکربندی تولید"""
    DEBUG = False
    DATABASE_DEBUG = False


class TestingConfig(Config):
    """پیکربندی تست"""
    DEBUG = True
    DATABASE_URL = "sqlite:///test.db"
    TESTING = True


def get_config():
    """بازگرداندن پیکربندی مناسب"""
    env = os.getenv("ENV", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


config = get_config()
