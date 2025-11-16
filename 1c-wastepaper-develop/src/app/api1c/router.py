from fastapi import APIRouter, Depends, HTTPException

from openai import OpenAI, AsyncOpenAI

from pydantic import BaseModel

from fuzzywuzzy import fuzz, process
import asyncio

import json

from sqlalchemy import cast, select, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.db import Nomenclature, get_db

from sentence_transformers import SentenceTransformer

from pgvector.sqlalchemy import Vector

from dotenv import load_dotenv
import os


load_dotenv()

API_KEY=os.getenv("API_KEY")

class NomenclatureSearch(BaseModel):
    search_query: str

class NomenclatureAnswer(BaseModel):
    code: str
    name: str
    score: int


client = AsyncOpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

router = APIRouter(prefix="/1c", tags=["1c"])

model = SentenceTransformer('ai-forever/ru-en-RoSBERTa')

async def send_depseek_req(search_query: str, items_chunk: list[dict], client):
    system_prompt = """Ты - ИИ-ассистент для поиска товаров в номенклатуре. 
    Тебе будет предоставлен запрос пользователя и список товаров.
    Найди наиболее подходящие товары из списка и верни их в формате JSON, старайся найти наибольшее совпадение:
    {
        "results": [
            {"code": "код товара", "name": "название", "score": 0-100}
        ]
    }"""

    user_prompt = f"""Запрос: {search_query}
    Список товаров: {json.dumps(items_chunk, ensure_ascii=False)}"""
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    try:
        json_result = response.choices[0].message.content
        return json.loads(json_result).get("results", [])
    except Exception as e:
        print(f"Ошибка при парсинге ответа: {e}")
        return []


@router.post("/embeddings")
async def post_embedding(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Nomenclature).where(Nomenclature.embedding.is_(None)))
    rows: list[Nomenclature] = result.scalars().all()
    #print(model.encode("проверка").shape)
    loop = asyncio.get_event_loop()

    for row in rows:
        embedding = await loop.run_in_executor(None, model.encode, row.name)
        row.embedding = embedding.tolist()
    
     
    await db.commit()

    return {"status": "ok", "updated": len(rows)}

@router.delete("/embeddings")
async def delete_embeddings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Nomenclature).where(Nomenclature.embedding.isnot(None)))
    rows: list[Nomenclature] = result.scalars().all()
    
    loop = asyncio.get_event_loop()

    for row in rows:
        row.embedding = None
        
        await db.commit()
    
    return {"status": "ok", "deleted": len(rows)}

@router.post("/search")
async def search_nomenclature(payload: NomenclatureSearch, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Nomenclature))
        items = result.scalars().all()
        names = [item.name for item in items]

        matches = process.extract(
            payload.search_query, 
            names, 
            limit=10,
            scorer=fuzz.token_set_ratio
        )
        print(matches)
        filtered = [match for match in matches if match[1] >= 70]

        results = []
        for name, score in filtered:
            item = next(i for i in items if i.name == name)
            results.append(NomenclatureAnswer(
                code=item.code,
                name=item.name,
                score=score
            ))

        results.sort(key=lambda x: x.score, reverse=True)

        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {e}"
        )


@router.post("/search/ai")
async def search_with_ai(payload: NomenclatureSearch, db: AsyncSession = Depends(get_db)):
    try:
        CHUNK_SIZE = 2000
        result = await db.execute(select(Nomenclature))
        items = result.scalars().all()
        items_data = [{"code": item.code, "name": item.name} for item in items]

        chunks = [items_data[i:i+CHUNK_SIZE] for i in range(0, len(items_data), CHUNK_SIZE)]

        tasks = [send_depseek_req(payload.search_query, chunk, client) for chunk in chunks]
        all_results = await asyncio.gather(*tasks)

        combined_results = [item for sublist in all_results for item in sublist]

        sorted_results = sorted(combined_results, key=lambda x: x.get("score", 0), reverse=True)
        return {"results": sorted_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")


@router.post("/search/vector")
async def search_embeddings(
    payload: NomenclatureSearch,
    db: AsyncSession = Depends(get_db),
    k: int = 5
):
    try:
        loop = asyncio.get_event_loop()
        query_embedding = await loop.run_in_executor(None, model.encode, payload.search_query)
        query_vec = query_embedding.tolist()

        try:
            check_query = text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            ext_result = await db.execute(check_query)
            if not ext_result.fetchone():
                raise HTTPException(
                    status_code=500,
                    detail="pgvector extension not installed. Run: CREATE EXTENSION vector;"
                )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="pgvector extension not available"
            )

        vector_str = '[' + ','.join(map(str, query_vec)) + ']'
        raw_query = text(f"""
            SELECT id, code, name, embedding,
                   embedding <=> '{vector_str}'::vector AS distance
            FROM public.nomenclature
            WHERE embedding IS NOT NULL
            ORDER BY distance
            LIMIT {k}
        """)
        
        result = await db.execute(raw_query)
        rows = result.fetchall()

        answers = []
        for row in rows:
            distance = row.distance
            score = max(0, int((1 - distance) * 100))
            
            answers.append(NomenclatureAnswer(
                code=row.code,
                name=row.name,
                score=score
            ))

        return answers

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка векторного поиска: {e}")