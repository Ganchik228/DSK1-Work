from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, insert_delivery_db, patch_delivery_db, loging
from database.gsmnbTables import Sitrak142


sitrak142rout = APIRouter(prefix="/Sitrak142", tags=["Sitrak142"])


@sitrak142rout.post("/Post")
async def sitrak142post(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            insert_delivery_db(db, Sitrak142, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@sitrak142rout.patch("/Patch")
# @sitrak142rout.patch("/BulkPatch")
async def sitrak142patch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            patch_delivery_db(db, Sitrak142, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@sitrak142rout.delete("/Delete")
@sitrak142rout.delete("/BulkDelete")
async def sitrak142delete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, Sitrak142)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
