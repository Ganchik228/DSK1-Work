import httpx
from sqlalchemy.orm import Session

def send_request(**kwargs):
    try:
        URL = "http://192.168.5.11/to_exp/hs/info/NomenclatureDiadoc"
        auth = httpx.BasicAuth(username="HttpUser", password="q111111!")
        client = httpx.Client(auth=auth)
        response = client.get(url=URL)
        response = response.json()
        ti = kwargs['ti']
        ti.xcom_push(key='response', value = response)
        return response
    except Exception as e:
        raise e

def drop_table(**kwargs):
    db: Session = kwargs['db']
    model = kwargs['model']
    try:
        db.query(model).delete()
        db.commit()
        return "Данные удалены"
    except Exception as e:
        db.rollback()
        raise e
    
def insert_into_table(**kwargs):
    db: Session = kwargs['db']
    model = kwargs['model']
    data = kwargs['ti'].xcom_pull(task_ids="fetch_1c",key="response")
    try:
        for item in data:
            entry = model(
                code = item.get('Code'),
                name = item.get('NomenclatureName')
            )
            db.add(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    