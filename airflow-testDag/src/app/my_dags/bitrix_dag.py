from datetime import timedelta
import time
import httpx
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, relationship
from sqlalchemy.engine import URL, create_engine
from sqlalchemy import ARRAY, Integer, String, DateTime, ForeignKey, Column
from typing import List, Optional
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()

URL_1C = os.getenv("URL_1C")


#               #
#   Database    #
#               #


Base = declarative_base()

DATABASE_URL = URL.create(
    "postgresql",
    username='airflow',
    password="airflow",
    host="176.109.102.60",
    port=5432,
    database="airflow"
)


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)

class refDepartments(Base):
    __tablename__ = "departments"
    __table_args__ = {"schema": "bitrix_to_postgres"}

    id: Mapped[int] = Column(Integer,primary_key=True)
    name: Mapped[str] = Column(String)
    parent_id: Mapped[Optional[int]] = Column(Integer,nullable=True)
    uf_head: Mapped[Optional[int]] = Column(Integer,nullable=True)

class refUsers(Base):   
    __tablename__ = "users"
    __table_args__ = {"schema": "bitrix_to_postgres"}

    id: Mapped[int] = Column(Integer,primary_key=True)
    name: Mapped[str] = Column(String)
    department_id: Mapped[Optional[List[int]]] = Column(ARRAY(Integer), nullable=True)
    id_1c: Mapped[str] = Column(String)

class Data(Base):
    __tablename__ = "data"
    __table_args__ = {"schema": "bitrix_to_postgres"}
    
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("bitrix_to_postgres.users.id", ondelete="NO ACTION"))
    department_id: Mapped[int] = Column(Integer, ForeignKey("bitrix_to_postgres.departments.id", ondelete="NO ACTION"), nullable=True)
    supervisor_id: Mapped[int] = Column(Integer, nullable=True)
    tasks: Mapped[int] = Column(Integer)
    overdue_tasks: Mapped[int] = Column(Integer)
    tasks_1c: Mapped[int] = Column(Integer)
    overdue_tasks_1c: Mapped[int] = Column(Integer)
    date: Mapped[datetime] = Column(DateTime)
    
    user = relationship("refUsers", backref="data")
    department = relationship("refDepartments", backref="data")

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
    print("Created tables:", list(Base.metadata.tables.keys()))


#               #
#   Functions   #
#               #


def fetch_users(**kwargs):
    url = "https://my.dsk1.one/rest/229/6diawmufs2r6ubwp/user.get"
    body = {"ACTIVE": "true", "USER_TYPE": "employee"}
    start = 0
    results = []
    try:
        while True:
            params = {"start": start}
            response = httpx.post(url, params=params, json=body)
            data = response.json()
            results += data.get("result", [])
            if not data.get("next"):
                break
            start += 50
        return results
    except Exception as e:
        raise e

def insert_users_task(**kwargs):
    ti = kwargs["ti"]
    data_1c = ti.xcom_pull(task_ids="fetch_1c")
    users = ti.xcom_pull(task_ids="fetch_users")
    with SessionLocal() as db:
        try:
            api_user_ids = {user.get("ID") for user in users}
            
            db_users = db.query(refUsers).all()
            
            for db_user in db_users:
                if db_user.id not in api_user_ids:
                    db.delete(db_user)
            
            for user in users:
                user_id = user.get("ID")
                name = f'{user.get("LAST_NAME")} {user.get("NAME")} {user.get("SECOND_NAME")}'
                department_id = user.get("UF_DEPARTMENT")
                
                id_1c = None
                for employee in data_1c:
                    if employee.get("Employee") == name:
                        id_1c = employee.get("Code")
                        break
                
                existed = db.query(refUsers).filter(refUsers.id == user_id).first()
                if existed:
                    existed.name = name
                    existed.department_id = department_id
                    if id_1c:
                        existed.id_1c = id_1c
                    db.add(existed)
                else:
                    db.add(refUsers(id=user_id, name=name, department_id=department_id, id_1c=id_1c))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

def fetch_departments(**kwargs):
    url = "https://my.dsk1.one/rest/229/g8m8ffdjhlwmnj5m/department.get"
    start = 0
    results = []
    try:
        while True:
            params = {"start": start}
            response = httpx.post(url, params=params)
            data = response.json()
            results += data.get("result", [])
            if not data.get("next"):
                break
            start += 50
        return results
    except Exception as e:
        raise e

def resolve_uf_head(dept: dict, departments: list):
    uf = dept.get("UF_HEAD")
    if uf and uf != "0":
        return uf
    parent_id = dept.get("PARENT")
    if parent_id:
        parent = next((d for d in departments if d.get("ID") == parent_id), None)
        if parent:
            return resolve_uf_head(parent, departments)
    return None

def insert_departments_task(**kwargs):
    ti = kwargs["ti"]
    departments = ti.xcom_pull(task_ids="fetch_departments")
    with SessionLocal() as db:
        try:
            api_dept_ids = {dept.get("ID") for dept in departments}
            
            db_depts = db.query(refDepartments).all()
            
            for db_dept in db_depts:
                if db_dept.id not in api_dept_ids:
                    db.delete(db_dept)
                    print(f"Deleted department {db_dept.id} as it no longer exists in API")
            
            for department in departments:
                department_id = department.get("ID")
                name = department.get("NAME")
                uf_head = resolve_uf_head(department, departments)
                parent_id = department.get("PARENT")
                existed = db.query(refDepartments).filter(refDepartments.id == department_id).first()
                if existed:
                    existed.name = name
                    existed.uf_head = uf_head
                    existed.parent_id = parent_id
                    db.add(existed)
                else:
                    db.add(refDepartments(id=department_id, name=name, uf_head=uf_head, parent_id=parent_id))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

def get_data(user_id: int, ovedue: bool = False):
    url = "https://my.dsk1.one/rest/229/ok7e3fwgsz90v9e2/tasks.task.list"
    payload = {"filter": {"RESPONSIBLE_ID": user_id, "REAL_STATUS": [2, 3]}}
    if ovedue:
        payload["filter"]["STATUS"] = "-1"
    retries = 3
    while retries:
        try:
            response = httpx.post(url, json=payload, timeout=10.0)
            if response.status_code == 503 and "QUERY_LIMIT_EXCEEDED" in response.text:
                time.sleep(1)
                retries -= 1
                continue
            response.raise_for_status()
            return response.json().get("total")
        except httpx.ReadTimeout:
            time.sleep(1)
            retries -= 1
    raise Exception("Max retries exceeded for get_data")

def insert_data_task(**kwargs):
    date = pendulum.now("Europe/Moscow").format("YYYY-MM-DD HH:mm:ss")
    ti = kwargs["ti"]
    data_1c = ti.xcom_pull(task_ids="fetch_1c")
    users = ti.xcom_pull(task_ids="fetch_users")
    with SessionLocal() as db:
        try:
            for user in users:
                user_id = user.get("ID")
                dept_list = user.get("UF_DEPARTMENT")
                dept_id = None
                supervisor_id = None
                
                if isinstance(dept_list, list) and dept_list:
                    for possible_dept_id in dept_list:
                        department = db.query(refDepartments).filter(refDepartments.id == possible_dept_id).first()
                        if department:
                            dept_id = possible_dept_id
                            supervisor_id = department.uf_head
                            if user_id == department.id and department.parent_id:
                                parent_dept = db.query(refDepartments).filter(refDepartments.id == department.parent_id).first()
                                if parent_dept:
                                    supervisor_id = parent_dept.uf_head
                            break
                    else:
                        print(f"{dept_list}")
                tasks = get_data(user_id)
                overdue_tasks = get_data(user_id, ovedue=True)
                
                tasks_1c = 0
                overdue_tasks_1c = 0
                user_1c = db.query(refUsers).filter(refUsers.id == user_id).first()
                if user_1c and user_1c.id_1c:
                    for employee in data_1c:
                        if employee.get("Code") == user_1c.id_1c:
                            tasks_1c = employee.get("Tasks", 0)
                            overdue_tasks_1c = employee.get("Delay", 0)
                            break
                
                db.add(Data(user_id=user_id,
                            department_id=dept_id,
                            tasks=tasks,
                            overdue_tasks=overdue_tasks,
                            tasks_1c=tasks_1c,
                            overdue_tasks_1c=overdue_tasks_1c,
                            supervisor_id=supervisor_id,
                            date=date))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

def fetch_1c_data(**kwargs):
    try:
        url = URL_1C
        auth = ("HttpUser", "q111111!")
        response = httpx.post(url, auth=auth)
        data = response.json()
        return data
    except Exception as e:
        raise e


#         #
#   DAG   #  
#         #


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 3, 25),
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "bitrix_dag",
    default_args=default_args,
    schedule_interval="0 4 * * 5",
    catchup=False,
) as dag:
    init_db_task = PythonOperator(
        task_id="init_db",
        python_callable=init_db
    )
    fetch_1c_task = PythonOperator(
        task_id="fetch_1c",
        python_callable=fetch_1c_data,
        provide_context=True
    )
    fetch_users_task = PythonOperator(
        task_id="fetch_users",
        python_callable=fetch_users,
        provide_context=True
    )
    process_users_task = PythonOperator(
        task_id="insert_users",
        python_callable=insert_users_task,
        provide_context=True
    )
    fetch_departments_task = PythonOperator(
        task_id="fetch_departments",
        python_callable=fetch_departments,
        provide_context=True
    )
    process_departments_task = PythonOperator(
        task_id="insert_departments",
        python_callable=insert_departments_task,
        provide_context=True
    )
    process_data_task = PythonOperator(
        task_id="insert_data",
        python_callable=insert_data_task,
        provide_context=True
    )
    
    init_db_task >> fetch_1c_task
    fetch_1c_task >> [fetch_users_task, fetch_departments_task]
    fetch_users_task >> process_users_task
    fetch_departments_task >> process_departments_task
    [process_users_task, process_departments_task] >> process_data_task
