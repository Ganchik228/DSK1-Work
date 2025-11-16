from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped
from sqlalchemy.engine import URL, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from pgvector.sqlalchemy import Vector

import asyncio
from sentence_transformers import SentenceTransformer
from pgvector import Vector as PGVector
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

import os
from dotenv import load_dotenv


load_dotenv()

Base = declarative_base()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
DATABASE=os.getenv("DATABASE")


database_url = URL.create(
    "postgresql+asyncpg",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

SCHEMA = "public" #'1c-wastepaper'

engine = create_async_engine(database_url, echo=True)

async_session = sessionmaker(bind=engine, class_=AsyncSession, autocommit=False, autoflush=False)

class Nomenclature(Base):
    __tablename__ = "nomenclature"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String)
    name: Mapped[str] = Column(String)
    embedding: Mapped[list[float]] = Column(Vector(1024))


async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

