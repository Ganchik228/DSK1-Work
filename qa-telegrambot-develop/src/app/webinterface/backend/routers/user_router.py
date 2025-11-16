from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from models.db import Users, get_db
from pydantic import BaseModel


class UserData(BaseModel):
    user_id: str
    user_name: str


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/all")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users))
    users = result.scalars().all()
    return {"users": [{"id": user.id, "name": user.name} for user in users]}


@router.get("/{id}")
async def get_user_by_id(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).filter(Users.id == id))
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "message": "User not found"}

    return {
        "status": "success",
        "user": {"id": user.id, "name": user.name, "is_activated": user.is_activated},
    }


@router.post("/")
async def create_user(
    user_data: UserData = Body(...), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Users).filter(Users.id == user_data.user_id))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        existing_user.name = user_data.user_name
        await db.commit()
        await db.refresh(existing_user)
        return {
            "status": "updated",
            "user": {
                "id": existing_user.id,
                "name": existing_user.name,
                "is_activated": existing_user.is_activated,
                "phone_number": existing_user.phone_number,
            },
        }
    else:
        new_user = Users(id=user_data.user_id, name=user_data.user_name)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {
            "status": "created",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "is_activated": new_user.is_activated,
            },
        }


@router.delete("/{id}")
async def delete_user(id: str, db: AsyncSession = Depends(get_db)):
    us = await db.execute(select(Users).filter(Users.id == id))
    user = us.scalar_one_or_none()
    result = await db.execute(delete(Users).filter(Users.id == id))
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "name": user.name,
        },
    }


@router.patch("/activate/{id}")
async def activate_user(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).filter(Users.id == id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await db.execute(update(Users).where(Users.id == id).values(is_activated=True))
    await db.commit()

    return {
        "status": "success",
        "message": f"Пользователь {user.name} успешно активирован",
        "user": {
            "id": user.id,
            "name": user.name,
            "is_activated": True,
        },
    }


@router.patch("/{id}/phone/{phone_number}")
async def update_user_phone(
    id: str, phone_number: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Users).filter(Users.id == id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await db.execute(
        update(Users).where(Users.id == id).values(phone_number=phone_number)
    )
    await db.commit()

    return {
        "status": "success",
        "message": f"Телефон пользователя {user.name} успешно обновлен",
        "user": {
            "id": user.id,
            "name": user.name,
            "phone_number": phone_number,
        },
    }


@router.get("/user/status/{user_id}")
async def user_status(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users).filter(Users.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        return {"activated": False}
    return {"activated": bool(user.is_activated)}
