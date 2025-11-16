import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

from my_packages.iico.db_funcs import *
from my_packages.models.db import *
from my_packages.iico.iicoRequests import *
from my_packages.iico.nt_telegram import send_message

from dotenv import load_dotenv
import os

load_dotenv()


BASE_URL = os.getenv("IICO_URL")


args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(year=2024, month=3, day=3, tz='Etc/GMT+1'),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1),
}
#iicoDAG
with DAG(
    dag_id='iicoDAG',
    default_args=args,
    description='iicoDBaseUpdate',
    schedule_interval='@daily',
    catchup=True,

)as dag:
    
    task1 = PythonOperator(
        task_id ='iicoLogin',
        python_callable= iicoLogin,
        op_kwargs={'url': BASE_URL, 'login': "katya", 'paswd': "e96e664645a6cdea80aa809199f6a9d2987684d2"},
    )

    taskDepReq = PythonOperator(
        task_id ='ResponseDepartmentsUpdate',
        python_callable= refDepartmentUpdate,
        op_kwargs={'url':BASE_URL},
    )

    taskDepUpd = PythonOperator(
        task_id ='DepartentsInsert',
        python_callable= insertDepartment,
        op_kwargs={'model': refDepartments},
        trigger_rule='all_done'
    )

    taskPaymentTypeReq = PythonOperator(
        task_id ='ResponsePaymentsUpdate',
        python_callable= refPaymentsUpdate,
        op_kwargs={'url':BASE_URL},
    )

    taskPaymentTypeInsert = PythonOperator(
        task_id ='PaymentsInsert',
        python_callable= refPaymentsInsert,
        op_kwargs={'model': refPaymentType},
        trigger_rule='all_done'
    )

    taskPricesReq = PythonOperator(
        task_id = 'ResponsePricesUpdate',
        python_callable=refPriceUpdate,
        op_kwargs={'url': BASE_URL},
    )

    #taskDropTable = PythonOperator(
    #    task_id = 'DropTable',
    #    python_callable=dropTable,
    #    op_kwargs={'model': refPrice},
    #)

    taskPriceInsert = PythonOperator(
        task_id = 'PriceInsert',
        python_callable=refPricesInsert,
        op_kwargs={'model': refPrice},
        trigger_rule='all_done'
    )

    taskPriceCategoryReq = PythonOperator(
        task_id ='ResponsePriceCategoryUpdate',
        python_callable= refPriceCategotyUpdate,
        op_kwargs={'url':BASE_URL},
    )

    taskPriceCategoryInsert = PythonOperator(
        task_id ='PriceCategoryInsert',
        python_callable= refPriceCategoryInsert,
        op_kwargs={'model': refPriceCategories},
        trigger_rule='all_done'

    )

    taskProductsReq = PythonOperator(
        task_id ='ResponseProductsUpdate',
        python_callable= refProductsUpdate,
        op_kwargs={'url':BASE_URL},
    )

    taskProductsIns = PythonOperator(
        task_id ='ProductsInsert',
        python_callable= refProductsInsert,
        op_kwargs={'model': refProducts},
        trigger_rule='all_done'
    )

    taskSalesReq = PythonOperator(
        task_id='iicoSalesOlap',
        python_callable=iicoSalesOlap,
        op_kwargs={'url': BASE_URL},
    )

    taskSalesIns = PythonOperator(
        task_id='InsertSales',
        python_callable=InsertSales,
        op_kwargs={'model': iicoPrices},
        trigger_rule='all_done'
    )

    taskShiftsReq = PythonOperator(
        task_id='iicoPayments',
        python_callable=iicoCashShifts,
        op_kwargs={'url': BASE_URL},
    )

    taskShiftsIns = PythonOperator(
        task_id='InsertPayments',
        python_callable=InsertPayments,
        op_kwargs={'model': iicoPaymentsShifts},
        trigger_rule='all_done'
    )

    taskTaxCatReq = PythonOperator(
        task_id ='ResponseTaxCategoryUpdate',
        python_callable= refTaxCategoryUpdate,
        op_kwargs={'url':BASE_URL},
    )

    taskTaxCatIns = PythonOperator(
        task_id ='TaxCategoryInsert',
        python_callable= refTaxCategoryInsert,
        op_kwargs={'model': refTaxCategory},
        trigger_rule='all_done'
    )
    
    taskOutgoingInvoiceReq = PythonOperator(
        task_id ='OutgoingInvoice',
        python_callable= getOutgoingInvoice,
        op_kwargs={'url':BASE_URL},
    )

    taskOutgoinInvoiceIns = PythonOperator(
        task_id ='OutgoingInoiceInsert',
        python_callable= insertOutgoingInvoice,
        op_kwargs={'model': OutgoingInvoice},
        trigger_rule='all_done'
    )

    task2 = PythonOperator(
        task_id ='iicoLogout',
        python_callable= iicoLogout,
        op_kwargs={'url': BASE_URL},
        trigger_rule='all_done'
    )

    task3 = PythonOperator(
        task_id = 'TelegramNotification',
        python_callable=send_message,
        trigger_rule='all_done'
    )

    task1 >> taskDepReq >> taskDepUpd >> task2
    task1 >> taskSalesReq >> taskSalesIns >> task2
    task1 >> taskPricesReq >> taskPriceInsert >> task2
    task1 >> taskShiftsReq >> taskShiftsIns >> task2
    task1 >> taskTaxCatReq >> taskTaxCatIns >> task2
    task1 >> taskProductsReq >> taskProductsIns >> task2
    task1 >> taskPaymentTypeReq >> taskPaymentTypeInsert >> task2
    task1 >> taskPriceCategoryReq >> taskPriceCategoryInsert >> task2
    task1 >> taskOutgoingInvoiceReq >> taskOutgoinInvoiceIns >> task2
    
    task2 >> task3