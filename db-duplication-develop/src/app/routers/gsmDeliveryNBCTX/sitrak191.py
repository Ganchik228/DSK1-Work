from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, insert_delivery_db, patch_delivery_db, loging
from database.gsmnbCTXTables import Sitrak191


sitrak191rout = APIRouter(prefix="/Sitrak191", tags=["Sitrak191"])


@sitrak191rout.post("/Post")
async def sitrak191post(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            insert_delivery_db(db, Sitrak191, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@sitrak191rout.patch("/Patch")
# @sitrak191rout.patch("/BulkPatch")
async def sitrak191patch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            patch_delivery_db(db, Sitrak191, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@sitrak191rout.delete("/Delete")
@sitrak191rout.delete("/BulkDelete")
async def sitrak142delete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, Sitrak191)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
