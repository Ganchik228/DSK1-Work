from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, insert_delivery_db, patch_delivery_db, loging
from database.gsmnbTables import Maz370


maz370rout = APIRouter(prefix="/Maz370", tags=["Maz370"])


@maz370rout.post("/Post")
async def maz370post(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            insert_delivery_db(db, Maz370, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@maz370rout.patch("/Patch")
# @maz370rout.patch("/BulkPatch")
async def maz370patch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            patch_delivery_db(db, Maz370, rows)
        return {"status": "ok", "data": data}
    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@maz370rout.delete("/Delete")
@maz370rout.delete("/BulkDelete")
async def maz370delete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, Maz370)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
