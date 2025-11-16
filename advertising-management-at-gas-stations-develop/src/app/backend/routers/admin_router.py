from fastapi import APIRouter, Depends
from database import TvTable, get_db
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from .auth_router import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin","Commands"])


@router.patch("/tvs/{tv_id}/ip/{ip_address}")
async def patch_ip(tv_id: int, ip_address: str, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    tv.address = ip_address
    await db.add(tv)
    await db.commit()
    return JSONResponse(status_code=200, content={"message": "IP address updated successfully"})

@router.patch("/tvs/{tv_id}/name/{new_name}")
async def patch_name(tv_id: int, new_name: str, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    tv.machine_name = new_name
    await db.add(tv)
    await db.commit()
    return JSONResponse(status_code=200, content={"message": "TV name updated successfully"})

@router.patch("/tvs/{tv_id}/password/{new_password}")
async def patch_password(tv_id: int, new_password: str, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    tv.password = new_password
    await db.add(tv)
    await db.commit()
    return JSONResponse(status_code=200, content={"message": "TV password updated successfully"})

@router.patch("/tvs/{tv_id}/username/{new_username}")
async def patch_username(tv_id: int, new_username: str , db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    tv.user_name = new_username
    await db.add(tv)
    await db.commit()
    return JSONResponse(status_code=200, content={"message": "TV username updated successfully"})

@router.patch("/tvs/{tv_id}/status/{new_status}")
async def patch_status(tv_id: int, new_status: str, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    tv.status = new_status
    await db.add(tv)
    await db.commit()
    return JSONResponse(status_code=200, content={"message": "TV status updated successfully"})

@router.get("/tvs/{tv_id}/data")
async def get_tv_data(tv_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    return JSONResponse(status_code=200, content={
        "id": tv.id,
        "machine_name": tv.machine_name,
        "address": tv.address,
        "videos": tv.videos,
        "user_name": tv.user_name,
        "password": tv.password,
        "status": tv.status,
        "category_id": tv.category_id
    })

@router.delete("/tvs/{tv_id}/delete")
async def delete_tv(tv_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    tv = await db.get(TvTable, tv_id)
    if not tv:
        return HTTPException(status_code=404, detail="TV not found")
    await db.delete(tv)
    await db.commit()
    return JSONResponse(status_code=200, content={"message": "TV deleted successfully"})