from sqlalchemy import Column, UUID, String, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_DATABASE")

SCHEMA = "fd-tgbot"
#SCHENA = "telegram_bot"
database_url = URL.create(
    "postgresql+asyncpg",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

async_engine = create_async_engine(database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine
)


class Reviews(Base):
    __tablename__ = "reviews"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID,primary_key=True)
    comment = Column(String)
    user_id = Column(UUID)
    role_id = Column(UUID)
    date_time = Column(TIMESTAMP)


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID,primary_key=True)
    chat_id = Column(String)
    name = Column(String)
    phone = Column(String)


class Roles(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID, primary_key=True)
    name = Column(String)


class UserAuth(Base):
    __tablename__ = "auth_user"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)


class AuthLogs(Base):
    __tablename__ = "auth_logs"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID, primary_key=True)
    user_auth_id = Column(UUID)
    date = Column(TIMESTAMP)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
