from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import datetime

from my_packages.models import Nomenclature, get_db, init_db
from my_packages.Nomenclature1C.func import send_request, drop_table, insert_into_table

from dotenv import load_dotenv
import os 

load_dotenv()

URL = os.getenv("NOMENC_URL")
USERNAME = "HttpUser"
PASSWORD = "q111111!"

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(year=2024, month=11, day=10, tz='Etc/GMT+1'),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1),
}

with DAG(
    dag_id='Nomenclature_1C',
    default_args=args,
    description='1C_nomeclatura',
    schedule_interval='@daily',
    catchup=False,

) as dag:
    task1 = PythonOperator(
        task_id = "init_db",
        python_callable=init_db,
    )

    task2 = PythonOperator(
        task_id='fetch_1c',
        python_callable=send_request,
        op_kwargs={'url': URL, 'username': USERNAME, 'password': PASSWORD}
    )

    task3 = PythonOperator(
        task_id='drop_table',
        python_callable=drop_table,
        op_kwargs={'db': next(get_db()),'model': Nomenclature}
    )

    task4 = PythonOperator(
        task_id = "insert_into_db",
        python_callable=insert_into_table,
        op_kwargs={'db':next(get_db()), 'model': Nomenclature}
    )

    task1 >> task2 >> task3 >> task4