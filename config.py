import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    # DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/postgres"
    # DB_CONFIG = f"postgresql+asyncpg://postgres:0@localhost/postgres"
    # DB_CONFIG = f"sqlite:///db.sqlite"
    DB_CONFIG = "sqlite+aiosqlite:///./db.sqlite"
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"


ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BOT_TOKEN = os.getenv("TOKEN")
# ADMIN_IDS = [123456789, 987654321]
