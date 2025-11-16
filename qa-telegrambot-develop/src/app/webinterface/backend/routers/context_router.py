from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.db import Contexts, get_db
from pydantic import BaseModel


class ContextData(BaseModel):
    name: str
    data: str


router = APIRouter(prefix="/context", tags=["context"])


@router.get("/all")
async def get_context(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contexts))
    contexts = result.scalars().all()
    return {
        "contexts": [
            {"id": context.id, "name": context.name, "data": context.data}
            for context in contexts
        ]
    }


@router.get("/{id}")
async def get_context_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contexts).filter(Contexts.id == id))
    context = result.scalar_one_or_none()
    return {
        "context_data": {
            "contextId": context.id,
            "contextName": context.name,
            "contextData": context.data,
        }
    }


@router.post("/")
async def post_context(
    context_data: ContextData = Body(...), db: AsyncSession = Depends(get_db)
):
    new_context = Contexts(name=context_data.name, data=context_data.data)
    db.add(new_context)
    await db.commit()
    await db.refresh(new_context)
    return {
        "status": "success",
        "context": {
            "id": new_context.id,
            "name": new_context.name,
            "data": new_context.data,
        },
    }


@router.put("/{id}")
async def update_context(
    id: int, context_data: ContextData = Body(...), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Contexts).filter(Contexts.id == id))
    context = result.scalar_one_or_none()
    if not context:
        return {"status": "error", "message": "Context not found"}

    context.name = context_data.name
    context.data = context_data.data
    await db.commit()
    await db.refresh(context)
    return {
        "status": "success",
        "context": {"id": context.id, "name": context.name, "data": context.data},
    }


@router.delete("/{id}")
async def delete_context(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contexts).filter(Contexts.id == id))
    context = result.scalar_one_or_none()
    if not context:
        return {"status": "error", "message": "Context not found"}

    await db.execute(delete(Contexts).filter(Contexts.id == id))
    await db.commit()
    return {"status": "success", "message": "Context deleted"}
