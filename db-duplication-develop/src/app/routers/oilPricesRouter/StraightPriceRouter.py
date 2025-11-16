from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, db_delete, loging
from database.oilProductsTables import StraightPriceDynamic


straightprout = APIRouter(prefix="/Straight", tags=["StraightPrice"])


@straightprout.post("/Post")
async def straightpost(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            for row in rows:
                nocodbID = row.get("Id")
                startDate = row.get('Дата "с"')
                endDate = row.get('Дата "по"')
                dt = row.get("ДТ")
                ai92 = row.get("АИ92")
                at95 = row.get("АИ95")

                ex_entry = (
                    db.query(StraightPriceDynamic)
                    .filter(StraightPriceDynamic.nocodbid == nocodbID)
                    .first()
                )
                if ex_entry:
                    continue
                new_entry = StraightPriceDynamic(
                    startdate=startDate,
                    enddate=endDate,
                    dt=dt,
                    ai92=ai92,
                    ai95=at95,
                    nocodbid=nocodbID,
                )
                db.add(new_entry)
            db.commit()

            return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@straightprout.patch("/Patch")
# @straightprout.patch("/BulkPatch")
async def straightpatch(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            for row in rows:
                nocodbID = row.get("Id")
                startDate = row.get('Дата "с"')
                endDate = row.get('Дата "по"')
                dt = row.get("ДТ")
                ai92 = row.get("АИ92")
                at95 = row.get("АИ95")

                entry = (
                    db.query(StraightPriceDynamic)
                    .filter(StraightPriceDynamic.nocodbid == nocodbID)
                    .first()
                )
                if entry:
                    entry.startdate = startDate
                    entry.enddate = endDate
                    entry.dt = dt
                    entry.ai92 = ai92
                    entry.ai95 = at95

                    db.commit()

        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@straightprout.delete("/Delete")
@straightprout.delete("/BulkDelete")
async def straightdelete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        rows = data.get("data", {}).get("rows", [])
        if rows:
            db_delete(db, rows, StraightPriceDynamic)
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
