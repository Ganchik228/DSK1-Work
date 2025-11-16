from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, loging
from database.oilProductsTables import GeneralPriceDynamic


generalprout = APIRouter(prefix="/General", tags=["GeneralPrice"])


@generalprout.post("/Post")
async def generalpost(request: Request, db: Session = Depends(get_db)):
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
                gaz = row.get("ГАЗ")
                ai100 = row.get("АИ100")
                ex_entry = (
                    db.query(GeneralPriceDynamic)
                    .filter(GeneralPriceDynamic.nocodbid == nocodbID)
                    .first()
                )
                if ex_entry:
                    continue
                new_entry = GeneralPriceDynamic(
                    date=date,
                    dt=dt,
                    ai92=ai92,
                    ai95=at95,
                    gaz=gaz,
                    ai100=ai100,
                    nocodbid=nocodbID,
                )
                db.add(new_entry)
            db.commit()

            return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@generalprout.patch("/Patch")
# @generalprout.patch("/BulkPatch")
async def generalpatch(request: Request, db: Session = Depends(get_db)):
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
                gaz = row.get("ГАЗ")
                ai100 = row.get("АИ100")

                entry = (
                    db.query(GeneralPriceDynamic)
                    .filter(GeneralPriceDynamic.nocodbid == nocodbID)
                    .first()
                )
                if entry:
                    entry.date = date
                    entry.dt = dt
                    entry.ai92 = ai92
                    entry.ai95 = at95
                    entry.gaz = gaz
                    entry.ai100 = ai100

                    db.commit()

        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@generalprout.delete("/Delete")
@generalprout.delete("/BulkDelete")
async def generaldelete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, GeneralPriceDynamic)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
