from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, insert_delivery_db, patch_delivery_db, loging
from database.gsmnbCTXTables import Sitrak107


sitrak107rout = APIRouter(prefix="/Sitrak107", tags=["Sitrak107"])


@sitrak107rout.post("/Post")
async def sitrak107post(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            insert_delivery_db(db, Sitrak107, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@sitrak107rout.patch("/Patch")
# @sitrak107rout.patch("/BulkPatch")
async def sitrak107patch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            patch_delivery_db(db, Sitrak107, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@sitrak107rout.delete("/Delete")
@sitrak107rout.delete("/BulkDelete")
async def sitrak107delete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, Sitrak107)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
