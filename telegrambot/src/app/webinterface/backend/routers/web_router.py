from fastapi import APIRouter, HTTPException, Depends, Body, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_model import Users, Reviews, Roles, get_db
import uuid

from .auth_router import get_current_user

router = APIRouter(prefix="/api")

@router.get("/users")
async def get_users(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Users))
    users = result.scalars().all()
    return users

@router.get("/users/{user_id}")
async def get_user(user_id: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await db.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/{user_id}/reviews")
async def get_user_reviews(user_id: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(
        Reviews.id,
        Reviews.comment,
        Reviews.date_time,
        Users.name.label("user_name"),
        Users.phone.label("user_phone"),
        Roles.name.label("role_name")).join(Users, Reviews.user_id == Users.id).join(Roles, Reviews.role_id == Roles.id).where(Reviews.user_id == user_id)
    result = await db.execute(stmt)
    reviews = result.mappings().all()
    return reviews

@router.get("/reviews")
async def get_reviews(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(
        Reviews.id,
        Reviews.comment,
        Reviews.date_time,
        Users.name.label("user_name"),
        Users.phone.label("user_phone"),
        Roles.name.label("role_name")).join(Users, Reviews.user_id == Users.id).join(Roles, Reviews.role_id == Roles.id)
    result = await db.execute(stmt)
    reviews = result.mappings().all()
    print(reviews)
    return reviews

@router.get("/reviews/{review_id}")
async def get_review(review_id: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(
        Reviews.id,
        Reviews.comment,
        Reviews.date_time,
        Users.name.label("user_name"),
        Users.phone.label("user_phone"),
        Roles.name.label("role_name")).join(Users, Reviews.user_id == Users.id).join(Roles, Reviews.role_id == Roles.id).where(Reviews.id == review_id)
    result = await db.execute(stmt)
    review = result.mappings().first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.get("/roles")
async def get_roles(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Roles))
    roles = result.scalars().all()
    return roles

@router.get("/roles/{role_id}")
async def get_role(role_id: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = await db.get(Roles, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("/roles")
async def create_role(body = Body(...), current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    name = body.get("name")
    role = Roles(id=uuid.uuid1(), name=name)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role

@router.put("/roles/{role_id}")
async def update_role(role_id: str, name: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = await db.get(Roles, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role.name = name
    await db.commit()
    await db.refresh(role)
    return role

@router.delete("/roles/{role_id}")
async def delete_role(role_id: str, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    role = await db.get(Roles, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await db.delete(role)
    await db.commit()
    return {"message": "Role deleted successfully"}
