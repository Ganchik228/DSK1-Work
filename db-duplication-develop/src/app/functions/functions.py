from sqlalchemy.orm import Session
import json
from config import LogPath, CHAT_ID, bot
from database.database import SessionLocal
import logging
from datetime import datetime


async def loging(data):
    date = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    if isinstance(data, Exception):
        logging.basicConfig(level=logging.ERROR, filename=LogPath, filemode="a+")
        logging.error(f"{date}\n{data}")
        try:
            text = data
            await bot.send_message(chat_id=CHAT_ID, text=text)
        except Exception as e:
            logging.error(f"{date}\n{e}")
    else:
        logging.basicConfig(level=logging.INFO, filename=LogPath, filemode="a+")
        logging.info(f"{date}\n{data}")
        try:
            text = json.dumps(data, indent=4)
            await bot.send_message(
                chat_id=CHAT_ID, text=text.encode("utf-8").decode("unicode_escape")
            )
        except Exception as e:
            logging.error(f"{date}\n{e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_delete(db: Session, rows: list, TableName: str):
    try:
        for row in rows:
            nocodbID = row.get("Id")
            if nocodbID:
                entry = (
                    db.query(TableName).filter(TableName.nocodbid == nocodbID).first()
                )
                if entry:
                    db.delete(entry)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e


#                   #
#   Delivery Funcs  #
#                   #


def insert_delivery_db(db: Session, model, rows: list):
    try:
        for row in rows:
            nocodbID = row.get("Id")

            ex_entry = db.query(model).filter(model.nocodbid == nocodbID).first()
            if ex_entry:
                continue

            new_entry = model(
                date=row.get("Дата"),
                plan_tonn=row.get("План тоннаж"),
                fact_tonn=row.get("Факт тоннаж"),
                nocodbid=nocodbID,
            )
            db.add(new_entry)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise e


def patch_delivery_db(db: Session, model, rows: list):
    try:
        for row in rows:
            nocodbID = row.get("Id")

            for row in rows:
                nocodbID = row.get("Id")
                date = row.get("Дата")
                plann_tonn = row.get("План тоннаж")
                fact_tonn = row.get("Факт тоннаж")

                entry = db.query(model).filter(model.nocodbid == nocodbID).first()
                if entry:
                    entry.date = date
                    entry.plan_tonn = plann_tonn
                    entry.fact_tonn = fact_tonn

                    db.commit()
            db.add(entry)
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise e
