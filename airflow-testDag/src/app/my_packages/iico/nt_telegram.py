import httpx
import pendulum

from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("CHAT_IDS") 

def on_fail_message(context):
    token = TOKEN
    task_id = context["ti"].task_id
    task_state = context["ti"].state
    dag_name = context["ti"].dag_id
    start_date = pendulum.instance(context["ti"].start_date).in_timezone("Etc/GMT-5")
    

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for id in CHAT_ID:
        chat_id = id
        payload = {
        "chat_id": chat_id,
        "text": f"*DAG name*: {dag_name} \n"
                f"*Task id*: {task_id} \n"
                f"*Start Date*: {start_date.format("YYYY-MM-DD HH:mm:ss Z")} \n"
                f"*Task State*: 🔴{task_state}🔴 \n",
        "parse_mode": "Markdown"
        }
        httpx.post(url=url,json=payload)


def on_success_message(context):
    token = TOKEN

    task_state = context["ti"].state
    dag_name = context["ti"].dag_id
    start_date = pendulum.instance(context["ti"].start_date).in_timezone("Etc/GMT-5")
    end_date = pendulum.instance(context["ti"].end_date).in_timezone("Etc/GMT-5")
    

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for id in CHAT_ID:
        chat_id = id
        payload = {
            "chat_id": chat_id,
            "text": f"*DAG name*: {dag_name} \n" 
                    f"*Start Date*: {start_date.format("YYYY-MM-DD HH:mm:ss Z")} \n"
                    f"*End Date*: {end_date.format("YYYY-MM-DD HH:mm:ss Z")} \n"
                    f"*DAG State*: 🟢{task_state}🟢 \n",
            "parse_mode": "Markdown"
        }
        httpx.post(url=url,json=payload)


def send_message(**kwargs):
    task_ids = ['DepartentsInsert','PaymentsInsert', 'PriceInsert', 'PriceCategoryInsert', 'ProductsInsert',
                'InsertSales', 'InsertPayments', 'TaxCategoryInsert', 'OutgoingInoiceInsert']
    states = kwargs['ti'].xcom_pull(task_ids=task_ids, key='TaskState')
    token = TOKEN

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    message_lines = [
        f"*Task*: {task_id}, *State*: {'🟢success🟢' if state else '🔴failed🔴'}"
        for task_id, state in zip(task_ids, states)
    ]
    executionDate = pendulum.instance(kwargs['execution_date']).in_timezone("Etc/GMT-5")
    endDate = pendulum.instance(kwargs['ti'].start_date).in_timezone("Etc/GMT-5")
    ids = CHAT_ID
    #ids = ["7913603106"]
    message_text = "\n".join(message_lines)
    for id in ids:
        payload = {
            "chat_id": id,
            "text": f"{message_text}\n"
                    "\n"
                    f"*Start Date*: {executionDate.format("YYYY-MM-DD HH:mm:ss Z")}\n"
                    f"*End Date*: {endDate.format("YYYY-MM-DD HH:mm:ss Z")}",
            "parse_mode": "Markdown"
        }

        httpx.post(url=url, json=payload)