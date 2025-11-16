from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from sqlalchemy.future import select
from sqlalchemy.engine import URL
from app.database.models import Roles, Users, Reviews

import uuid

from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_DATABASE")

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

async def get_roles() -> list:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Roles.name))
            roles = result.scalars().all()
        return roles
    except Exception as e:
        print(f"Error fetching roles: {e}")
        return []


async def set_user(chat_id, name: str | None):
    try:
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(Users).where(Users.chat_id==str(chat_id)))
            if name != None:
                session.add(Users(id=uuid.uuid1(),chat_id=str(chat_id),name=name))
                await session.commit()
            else: 
                return user.name
    except Exception as e:
            print(f"Error fetching roles: {e}")


async def set_review(message_text, chat_id, role_name, date):
    try: 
        async with AsyncSessionLocal() as session:
            role = await session.scalar(select(Roles).where(Roles.name == role_name))
            user = await session.scalar(select(Users).where(Users.chat_id == str(chat_id)))
            session.add(Reviews(id=uuid.uuid1(), comment=message_text, user_id=user.id, role_id=role.id, date_time=date.replace(tzinfo=None)))
            await session.commit()
    except Exception as e:
        print(f"Error fetching roles: {e}")


async def set_contact(chat_id, phone):
    try:
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(Users).where(Users.chat_id == str(chat_id)))
            user.phone = phone
            await session.commit()
    except Exception as e:
        print(f"Error saving contact: {e}")

async def get_contact(chat_id):
    try:
        async with AsyncSessionLocal() as session:
            user = await session.scalar(select(Users).where(Users.chat_id == str(chat_id)))
            return user.phone if user else None
    except Exception as e:
        print(f"Error getting contact: {e}")
        return None
