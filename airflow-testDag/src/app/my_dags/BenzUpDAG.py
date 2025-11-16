import requests
from requests.auth import HTTPBasicAuth
import datetime
import pytz

from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL

from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
DATABASE=os.getenv("DATABASE")

DATABASE_URL = URL.create(
    "postgresql",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FuelPrices(Base):
    __tablename__ = "fuel_prices"
    __table_args__ = {"schema":"car_filling_station"}

    id = Column(Integer,primary_key=True,autoincrement=True)
    station_id = Column(Integer)
    product_code = Column(String)
    product_name = Column(String)
    date_of_change = Column(TIMESTAMP)
    date_of_insertion = Column(TIMESTAMP)
    price = Column(Numeric)


Base.metadata.create_all(bind=engine)


BASE_URL = "http://data.omt-consult.ru"
LOGIN = "odubkova@dsk1.one"
PASSWORD = "odubkova111"

time_zone = pytz.timezone("Europe/Moscow")
date = datetime.datetime.now(time_zone)

def get_my_stations(**kwargs):
    try:
        baseUrl = kwargs['url']
        login = kwargs['login']
        password = kwargs['password']
        response = requests.get(f"{baseUrl}/api/v1/customer_stations", auth=HTTPBasicAuth(username=login, password=password))
        if response.status_code == 200:
            data = response.json()
            all_stations = []
            for item in data:
                if 'own' in item and item['own']:
                    all_stations.append(item['own'])

                if 'competitors' in item and item['competitors']:
                    all_stations.extend(item['competitors'])

            kwargs['ti'].xcom_push(key='Stations', value=all_stations) 
        else:
            message = f"[{datetime.datetime.now(time_zone)}].error.response.status_code:{response.status_code}\n" 
            print(message)
            print(response.connection)
            raise Exception(message)
    except Exception as e:
        raise Exception(e)

def get_prices(**kwargs):
    try:
        stations = kwargs['ti'].xcom_pull(task_ids='GetStations', key='Stations')
        baseUrl = kwargs['url']
        login = kwargs['login']
        password = kwargs['password']
        station_ids = [station['id'] for station in stations if 'id' in station]
        prices = []
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{baseUrl}/api/v1/bulk/prices", headers=headers, json=station_ids, auth=HTTPBasicAuth(username=login, password=password))
        if response.status_code == 200:
            data = response.json()
            prices = [item for item in data]

            kwargs['ti'].xcom_push(key='Prices', value=prices)
        else:
            message = f"[{datetime.datetime.now(time_zone)}].error.response.status_code:{response.status_code}\n"
            print(message)
            print(response.connection)
            raise Exception(message)
    except Exception as e:
        raise Exception(e)

def insert_prices_into_db(**kwargs):
    prices = kwargs['ti'].xcom_pull(task_ids='GetPrices', key='Prices')
    n = 0
    db = next(get_db())
    try:
        for price in prices:
            station_id = price.get('station_id')
            product_code = price.get('product_code')
            product_name = price.get('product_name')
            price_value = price.get('price')
            date_of_change = price.get('date')
            
            existing_entry = db.query(FuelPrices).filter_by(
                station_id=station_id,
                product_code=product_code,
                date_of_change=date_of_change
            ).first()
            
            if not existing_entry:
                fuel_price = FuelPrices(
                    station_id=station_id,
                    product_code=product_code,
                    product_name=product_name,
                    price=price_value,
                    date_of_change=date_of_change,
                    date_of_insertion=date.strftime('%Y-%m-%d %H:%M:%S')
                )

                db.add(fuel_price)
                n += 1

        db.commit()
        print(f"[{datetime.datetime.now(time_zone)}].success.quantity:{n}\n")
    except Exception as e:
        db.rollback()
        print(f"[{datetime.datetime.now(time_zone)}].error.exception:{e}\n")
        raise Exception(e)
    finally:
        db.close()


#          #
#   DAG    #
#          #


args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(year=2024, month=12, day=26, tz='Etc/GMT+1'),
    'retries': 2,
    'retry_delay': datetime.timedelta(minutes=5),
}


with DAG(
    dag_id='BenzUpDAG',
    default_args=args,
    description='BenzUP',
    schedule_interval='@hourly',
    catchup=False,
) as dag:
    
    task1 = PythonOperator(
        task_id = "GetStations",
        python_callable=get_my_stations,
        op_kwargs={"url":BASE_URL, "login":LOGIN, "password":PASSWORD}
    )

    task2 = PythonOperator(
        task_id = "GetPrices",
        python_callable=get_prices,
        op_kwargs={"url":BASE_URL, "login":LOGIN, "password":PASSWORD}
    )

    task3 = PythonOperator(
        task_id = "InsertPricesIntoDB",
        python_callable=insert_prices_into_db,
        op_kwargs={}
    )

    task1 >> task2 >> task3