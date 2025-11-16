import httpx


def iicoLogin(**kwargs):
    url = kwargs['url']
    login = kwargs['login']
    paswd = kwargs['paswd']
    params = {'login': login, 'pass': paswd}
    token = httpx.get(url=url + "auth", params=params)
    kwargs['ti'].xcom_push(key='token', value=token.text)
    kwargs['ti'].xcom_push(key='startDate', value=kwargs['ti'].start_date)
    print(token.status_code)


def iicoLogout(**kwargs):
    url = kwargs['url']

    try:
        token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')
    except Exception as e:
        return e

    params = {'key': token}
    response = httpx.get(url=url + "logout", params=params)

    print(response.status_code)


def refDepartmentUpdate(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')   
    url = kwargs['url']
    params = {"key": token}

    response = httpx.get(url=url+"corporation/groups/", params=params)
    
    kwargs['ti'].xcom_push(key='data', value=response.text)
    print(response.status_code)


def refPaymentsUpdate(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')
    url = kwargs['url']
    params = {"key": token, "rootType": "PaymentType"}
    response = httpx.get(url=url+"v2/entities/list", params=params)
    
    print(response.url)
    print(response.status_code)
    ti = kwargs['ti']
    ti.xcom_push(key="data", value=response.json())
    print(response.status_code)


def refPriceUpdate(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')    
    url = kwargs['url']
    params = {"key": token, "dateFrom": "2024-03-01"}
    response = httpx.get(url=url+"v2/price", params=params)
    
    print(response.url)
    print(response.status_code)
    ti = kwargs['ti']
    ti.xcom_push(key="data", value=response.json())
    print(response.status_code)


def refPriceCategotyUpdate(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')
    url = kwargs['url']
    params = {"key": token, "includeDeleted": "true"}
    response = httpx.get(url=url+"v2/entities/priceCategories", params=params)
    
    print(response.url)
    print(response.status_code)

    ti = kwargs['ti']
    ti.xcom_push(key="data", value=response.json())
    print(response.status_code)


def refProductsUpdate(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin',key='token')
    url = kwargs['url']
    params = {"key": token, "includeDeleted": "true"}
    response = httpx.get(url=url+"v2/entities/products/list", params=params)
    
    print(response.url)
    print(response.status_code)
    ti = kwargs['ti']
    ti.xcom_push(key="data", value=response.json())
    print(response.status_code)


def iicoSalesOlap(**kwargs):
    url = kwargs['url']
    DATE = kwargs['execution_date']
    
    try:
        token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')    
    except Exception as e:
        print(e)
    params = {'key': token, 'report': 'SALES', 'from': DATE.strftime("%d.%m.%Y"), 'to': DATE.strftime("%d.%m.%Y"), 'groupCol': ['Department.Id', 'UniqOrderId.Id', 'DishId', 'SessionID', 'PaymentTransaction.Id'], 'hideAccepted': 'false'}
    response = httpx.get(url=url + "reports/olap", params=params)

    kwargs['ti'].xcom_push(key="data", value=response.text)
    print(response.status_code)


def iicoCashShifts(**kwargs):
    url = kwargs['url']
    DATE = kwargs['execution_date']

    try:
        token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')
    except Exception as e:
        print(e)
    params = {'key': token, 'openDateFrom': DATE.strftime('%Y-%m-%d'), 'openDateTo': DATE.strftime('%Y-%m-%d'), 'status': 'ANY'}
    response = httpx.get(url=url + "v2/cashshifts/list", params=params)
    shifts = response.json()
    payments = []
    for shift in shifts:
        secpar = {'key': token, 'hideAccepted': 'false'}
        res = httpx.get(url=url + f"v2/cashshifts/payments/list/{shift.get('id')}", params=secpar)
        payments.append(res.json())
    
    ti = kwargs['ti']
    ti.xcom_push(key="payments", value=payments)
    ti.xcom_push(key="shifts", value=shifts)
    print(response.status_code)


def refTaxCategoryUpdate(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')
    url = kwargs['url']
    params = {"key": token, "rootType": "TaxCategory"}
    response = httpx.get(url=url+"v2/entities/list", params=params)
    
    print(response.url)
    print(response.status_code)

    ti = kwargs['ti']
    ti.xcom_push(key="data", value=response.json())
    print(response.status_code)


def getOutgoingInvoice(**kwargs):
    token = kwargs['ti'].xcom_pull(task_ids='iicoLogin', key='token')       
    DATE = kwargs['execution_date']

    url = kwargs['url']
    params = {"key": token, "from": DATE.strftime('%Y-%m-%d'), "to": DATE.strftime('%Y-%m-%d')}
    response = httpx.get(url=url+"documents/export/outgoingInvoice", params=params)

    kwargs['ti'].xcom_push(key="data", value=response.text)
    print(response.status_code)
