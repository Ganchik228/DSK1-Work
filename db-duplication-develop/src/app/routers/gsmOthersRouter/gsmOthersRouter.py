from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, insert_delivery_db, patch_delivery_db, loging
from database.gsmOthers import AllTransp


AllTransprout = APIRouter(prefix="/AllTransp", tags=["AllTransp"])


@AllTransprout.post("/Post")
async def AllTransppost(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            insert_delivery_db(db, AllTransp, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@AllTransprout.patch("/Patch")
# @AllTransprout.patch("/BulkPatch")
async def AllTransppatch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            patch_delivery_db(db, AllTransp, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@AllTransprout.delete("/Delete")
@AllTransprout.delete("/BulkDelete")
async def AllTranspdelete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, AllTransp)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
