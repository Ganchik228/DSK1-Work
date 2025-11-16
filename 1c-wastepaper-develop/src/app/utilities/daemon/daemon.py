import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from models.db import get_db, Nomenclature, init_db
from sentence_transformers import SentenceTransformer

import asyncio

from dotenv import load_dotenv
import os

URL_1C = os.getenv("URL_1C")

_model = SentenceTransformer('ai-forever/ru-en-RoSBERTa')

async def send_request():
    try:
        URL = "URL_1C"
        auth = httpx.BasicAuth(username="HttpUser", password="q111111!")
        async with httpx.AsyncClient() as client:
            response = await client.post(url=URL, auth=auth)
        return response.json()
    except Exception as e:
        raise e

async def drop_table(db: AsyncSession, model: Nomenclature): 
    try:
        stmt = delete(model)
        await db.execute(stmt)
        await db.commit()
        return "Все данные успешно удалены"
        
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"Ошибка при удалении данных: {str(e)}") from e
    
async def insert_into_table(db: AsyncSession, model: Nomenclature, data):
    try:
        loop = asyncio.get_event_loop()
        for item in data:
            _name = item.get('NomenclatureName')
            _code = item.get('Code')
            entry = model(
                code = _code,
                name = _name,
                embedding = await loop.run_in_executor(None, _model.encode, _name)
            )
            db.add(entry)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

async def update_nomenclature():
    try:
        await init_db()
        data = await send_request()
        async for db in get_db():
            await drop_table(db=db, model=Nomenclature)
            await insert_into_table(db=db, model=Nomenclature, data=data)
            return "Данные номенклатуры успешно обновлены"
    except Exception as e:
        raise RuntimeError(f"Ошибка при обновлении номенклатуры: {str(e)}") from e
