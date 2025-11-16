import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import URL, Integer, String, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.sql import func

from datetime import datetime

from dotenv import load_dotenv
import os

Base = declarative_base()

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SCHEME = "tg_api"
DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DB_NAME,
)


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    async with async_session() as session:
        yield session


class Contexts(Base):
    __tablename__ = "contexts"
    __table_args__ = {"schema": SCHEME}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    data: Mapped[str] = mapped_column(String)


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": SCHEME}

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    is_activated: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_number: Mapped[str] = mapped_column(String)
    messages: Mapped[list["Messages"]] = relationship("Messages", back_populates="user")


class Messages(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": SCHEME}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey(f"{SCHEME}.users.id"))
    request: Mapped[String] = mapped_column(String)
    response: Mapped[String] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    checked: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("Users", back_populates="messages")


class AuthUser(Base):
    __tablename__ = "authuser"
    __table_args__ = {"schema": SCHEME}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
