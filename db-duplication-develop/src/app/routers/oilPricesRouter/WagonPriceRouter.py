from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, loging
from database.oilProductsTables import WagonPriceDynamic


wagonprout = APIRouter(prefix="/Wagon", tags=["WagonPrice"])


@wagonprout.post("/Post")
async def wagonpost(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            for row in rows:
                nocodbID = row.get("Id")
                date = row.get("Дата")
                dt = row.get("ДТ")
                ai92 = row.get("АИ92")
                at95 = row.get("АИ95")

                ex_entry = (
                    db.query(WagonPriceDynamic)
                    .filter(WagonPriceDynamic.nocodbid == nocodbID)
                    .first()
                )
                if ex_entry:
                    continue
                new_entry = WagonPriceDynamic(
                    date=date, dt=dt, ai92=ai92, ai95=at95, nocodbid=nocodbID
                )
                db.add(new_entry)
            db.commit()

            return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@wagonprout.patch("/Patch")
# @wagonprout.patch("/BulkPatch")
async def wagonpatch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            for row in rows:
                nocodbID = row.get("Id")
                date = row.get("Дата")
                dt = row.get("ДТ")
                ai92 = row.get("АИ92")
                at95 = row.get("АИ95")

                entry = (
                    db.query(WagonPriceDynamic)
                    .filter(WagonPriceDynamic.nocodbid == nocodbID)
                    .first()
                )
                if entry:
                    entry.date = date
                    entry.dt = dt
                    entry.ai92 = ai92
                    entry.ai95 = at95

                    db.commit()

        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@wagonprout.delete("/Delete")
@wagonprout.delete("/BulkDelete")
async def wagondelete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, WagonPriceDynamic)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
