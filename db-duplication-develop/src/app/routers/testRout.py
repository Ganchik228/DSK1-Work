from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from functions import get_db, loging

router = APIRouter(prefix="/test", tags=["test"])


@router.post("/insert")
async def webhook_insert(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)
        # rows = data.get("data", {}).get("rows",[])
        # if rows:
        #    for row in rows:
        #        print(row)
        #        nocodbID = row.get("Id")
        #        title = row.get("Заголовок")
        #        description = row.get("Description")
        #        print(f"{nocodbID},{title},{description}")
        #        ex_entry = db.query(YourTable).filter(YourTable.nocodbid == nocodbID).first()
        #        if ex_entry:
        #            continue
        #        new_entry = YourTable(title=title, description=description, nocodbid=nocodbID)
        #        db.add(new_entry)
        #    db.commit()
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@router.patch("/update")
async def webhook_update(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        # rows = data.get("data", {}).get("rows", [])
        # if rows:
        #    for row in rows:
        #        nocodbID = row.get("Id")
        #        title = row.get("Title")
        #        description = row.get("Description")
        #
        #        entry = db.query(YourTable).filter(YourTable.nocodbid == nocodbID).first()
        #        if entry:
        #            entry.title = title
        #            entry.description = description
        #            db.commit()

        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}


@router.delete("/delete")
async def webhook_delete(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        await loging(data)

        # rows = data.get("data",{}).get("rows", [])
        # if rows:
        #    for row in rows:
        #        nocodbID = row.get("Id")
        #
        #        entry = db.query(YourTable).filter(YourTable.nocodbid == nocodbID).first()
        #        if entry:
        #            db.delete(entry)
        #            db.commit()
        return {"status": "ok", "data": data}

    except Exception as e:
        await loging(e)

        return {"status": "error", "message": str(e)}
