from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Integer, String, ARRAY, URL, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy import URL, ForeignKey
from sqlalchemy import String, Integer, ARRAY, TIMESTAMP, Boolean

from datetime import datetime

from dotenv import load_dotenv
import os


Base = declarative_base()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
DATABASE=os.getenv("DATABASE")

DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False)

async def get_db():
    async with async_session() as session:
        yield session

class Categories(Base): 
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)


class TvTable(Base):
    __tablename__ = "rasppi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    machine_name: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    videos: Mapped[list[str]] = mapped_column(ARRAY(String))
    user_name: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))


class UserAuth(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

class AuthLogs(Base):
    __tablename__ = "auth_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_auth_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.id"),autoincrement=True)
    date: Mapped[datetime] = mapped_column(TIMESTAMP)
