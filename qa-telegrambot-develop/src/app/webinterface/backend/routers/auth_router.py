from authx import AuthX, AuthXConfig, RequestToken
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from models.db import AuthUser, get_db
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

config = AuthXConfig()
config.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)


class UserLoginSchema(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    LoginData: UserLoginSchema, response: Response, db: AsyncSession = Depends(get_db)
):
    user = await db.get(AuthUser, LoginData.username)
    if not user:
        raise HTTPException(401, detail={"message": "Invalid credentials"})

    token = security.create_access_token(uid=LoginData.username)

    response.set_cookie(
        key=security.config.JWT_ACCESS_COOKIE_NAME, value=token, secure=True
    )

    if LoginData.username == "xyz" and LoginData.password == "xyz":
        token = security.create_access_token(uid=LoginData.username)
        return {"access_token": token}

    raise HTTPException(401, detail={"message": "Invalid credentials"})


@router.get("/protected", dependencies=[Depends(security.get_token_from_request)])
async def get_protected(token: RequestToken = Depends()):
    try:
        security.verify_token(token=token)
        return {"message": "Hello world !"}
    except Exception as e:
        raise HTTPException(401, detail={"message": str(e)}) from e
