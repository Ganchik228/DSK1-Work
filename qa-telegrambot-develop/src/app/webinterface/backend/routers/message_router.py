from fastapi import APIRouter, Depends, Body
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.db import Messages, get_db, Users
from pydantic import BaseModel

from datetime import datetime

router = APIRouter(prefix="/message", tags=["message"])


class MessageData(BaseModel):
    user_id: str
    request: str
    response: str
    date: datetime


@router.post("/")
async def create_message(
    message_data: MessageData = Body(...), db: AsyncSession = Depends(get_db)
):

    print(message_data)
    if isinstance(message_data.date, str):
        date = datetime.fromisoformat(message_data.date)
    else:
        date = message_data.date
    
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)

    new_message = Messages(
        user_id=message_data.user_id,
        request=message_data.request,
        response=message_data.response,
        date=date,
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return {
        "status": "success",
        "message": {
            "user_id": new_message.user_id,
            "request": new_message.request,
            "response": new_message.response,
            "date": new_message.date,
        },
    }


@router.get("/all")
async def get_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Messages).options(joinedload(Messages.user)))
    messages = result.scalars().all()
    return {
        "messages": [
            {
                "id": message.id,
                "phone_number": message.user.phone_number,
                "user_id": message.user_id,
                "request": message.request,
                "response": message.response,
                "date": message.date,
                "checked": message.checked,
            }
            for message in messages
        ]
    }


@router.get("/user/{user_id}")
async def get_messages_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Messages).filter(Messages.user_id == user_id))
    messages = result.scalars().all()
    return {
        "messages": [
            {
                "id": message.id,
                "user_id": message.user_id,
                "request": message.request,
                "response": message.response,
                "date": message.date,
            }
            for message in messages
        ]
    }


@router.patch("/status/{message_id}")
async def checked_message_status(message_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Messages).where(Messages.id == message_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        if message.checked == True:
            message.checked = False
            await db.commit()
            await db.refresh(message)
            return {"status": "success", "message": "Message marked as unchecked"}
        elif message.checked == False:
            message.checked = True
            await db.commit()
            await db.refresh(message)
            return {"status": "success", "message": "Message marked as checked"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


