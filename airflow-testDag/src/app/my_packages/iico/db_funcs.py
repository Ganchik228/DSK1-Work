from ..models.db import get_db
import xml.etree.ElementTree as ET

def insertDepartment(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='ResponseDepartmentsUpdate', key='data')
        tree = ET.fromstring(data)

        for department in tree.findall("groupDto"):
            ex_entry = db.query(model).filter(model.id == department.find("id").text).first()
            point_of_sale = department.find("pointOfSaleDtoes/pointOfSaleDto")
            restaurant_section = department.find("restaurantSectionInfos/restaurantSectionInfo")

            if ex_entry:
                ex_entry.pointofsale_id = point_of_sale.find("id").text if point_of_sale is not None else None
                ex_entry.pointofsale_name = point_of_sale.find("name").text if point_of_sale is not None else None
                ex_entry.cashregister_id = point_of_sale.find("cashRegisterInfo/id").text if point_of_sale is not None else None
                ex_entry.cashregister_name = point_of_sale.find("cashRegisterInfo/name").text if point_of_sale is not None else None
                ex_entry.restaurantsection_id = restaurant_section.find("id").text if restaurant_section is not None else None
                ex_entry.restaurantsection_name = restaurant_section.find("name").text if restaurant_section is not None else None
            else:
                new_entry = model(
                    id=department.find("id").text,
                    department_id=department.find("departmentId").text,
                    pointofsale_id=point_of_sale.find("id").text if point_of_sale is not None else None,
                    pointofsale_name=point_of_sale.find("name").text if point_of_sale is not None else None,
                    cashregister_id=point_of_sale.find("cashRegisterInfo/id").text if point_of_sale is not None else None,
                    cashregister_name=point_of_sale.find("cashRegisterInfo/name").text if point_of_sale is not None else None,
                    restaurantsection_id=restaurant_section.find("id").text if restaurant_section is not None else None,
                    restaurantsection_name=restaurant_section.find("name").text if restaurant_section is not None else None,
                )
                db.add(new_entry)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError("{e}")
    

def refPaymentsInsert(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='ResponsePaymentsUpdate',key='data')


        for payment in data:
            ex_entry = db.query(model).filter(model.paymenttype_id == payment.get("id")).first()   
            if ex_entry:
                ex_entry.deleted = payment["deleted"]
                ex_entry.code = payment.get("code")
                ex_entry.name = payment.get("name")
            else:
                new_etnry = model(
                paymenttype_id = payment.get("id"),
                deleted = payment["deleted"],
                code = payment.get("code"),
                name = payment.get("name")
                )
                db.add(new_etnry)
        db.commit() 
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError("{e}")
    

#def dropTable(**kwargs):
#
#    try:
#        model = kwargs['model']
#        db = next(get_db())
#        table_name = f"{model.__table_args__['schema']}.{model.__tablename__}"
#        db.execute(f"TRUNCATE TABLE {table_name};")
#        db.commit()
#    except Exception as e:
#        print(e)
#        raise RuntimeError("{e}")
    

def refPricesInsert(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='ResponsePricesUpdate',key='data')
    
        table_name = f"{model.__table_args__['schema']}.{model.__tablename__}"
        db.execute(f"TRUNCATE TABLE {table_name};")
        db.commit()
        
        for department in data['response']:
            for price_entry in department['prices']:
                for price_category in price_entry['pricesForCategories']:
                    ref_price = model(
                        department_id=department['departmentId'],
                        product_id=department['productId'],
                        datefrom=price_entry['dateFrom'],
                        dateto=price_entry['dateTo'],
                        taxcategory_id=price_entry.get('taxCategoryId', None),
                        pricecategory_id=price_category['categoryId'],
                        price=str(price_category['price']),
                        includecategory_id=price_category['categoryId'],
                        include=next(
                            (include['include'] for include in price_entry['includeForCategories']
                            if include['categoryId'] == price_category['categoryId']), 
                            False),
                        document_id=price_entry['documentId']
                    )
                    db.add(ref_price)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=True)
        raise RuntimeError('{e}')
    

def refPriceCategoryInsert(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='ResponsePriceCategoryUpdate',key='data')

        for category in data["response"]:
            ex_entry = db.query(model).filter(model.pricecategory_id == category.get("id")).first()   
            if ex_entry:
                ex_entry.name = category.get("name")
                ex_entry.deleted = category.get("deleted")
                ex_entry.code = category.get("code")
            else:
                new_etnry = model(
                    pricecategory_id = category.get("id"),
                    name = category.get("name"),
                    deleted = category.get("deleted"),
                    code = category.get("code")
                )
                db.add(new_etnry)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError('{e}')


def refProductsInsert(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='ResponseProductsUpdate',key='data')

        for category in data:
            ex_entry = db.query(model).filter(model.product_id == category.get("id")).first()   
            if ex_entry:
                    ex_entry.deleted = category.get("deleted")
                    ex_entry.name = category.get("name")
                    ex_entry.taxcategory_id = category.get("taxCategory")
            else:
                new_entry = model(
                    product_id = category.get("id"),
                    deleted = category.get("deleted"),
                    name = category.get("name"),
                    taxcategory_id = category.get("taxCategory")
                )
                db.add(new_entry)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError('{e}')


def InsertSales(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='iicoSalesOlap', key='data')
        tree = ET.fromstring(data)
    
        for sale in tree.findall("r"):
            dish_id = sale.find("DishId").text
            
            new_entry = model(
                dish_id=dish_id,
                paymenttransaction_id=sale.find("PaymentTransaction.Id").text,
                uniqorder_id=sale.find("UniqOrderId.Id").text,
                departament_id=sale.find("Department.Id").text,
                session_id=sale.find("SessionID").text
            )
            
            db.add(new_entry)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError('{e}')
    

def InsertPayments(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        shifts = kwargs['ti'].xcom_pull(task_ids='iicoPayments', key='shifts')
        payments_list = kwargs['ti'].xcom_pull(task_ids='iicoPayments', key='payments')

        record_keys = ['cashlessRecords', 'payOutsRecords']

        for shift, payments in zip(shifts, payments_list):
            for record_key in record_keys:
                for payment in payments.get(record_key, []):
                    info = payment.get('info', {})
                    ex_entry = db.query(model).filter(model.payment_id == info.get("id")).first()    
                    if ex_entry:
                        continue
                    
                    new_entry = model(
                        payment_id=info.get('id'),
                        date=info.get('date'),
                        creationdate=info.get('creationDate'),
                        paymenttype_id=info.get('paymentTypeId'),
                        type=info.get('type'),
                        sum=info.get('sum'),
                        actualsum=payment.get('actualSum'),
                        originalsum=payment.get('originalSum'),
                        status=payment.get('status'),
                        cashshift_id=shift.get("id"),
                        sessionnumber=shift.get("sessionNumber"),
                        fiscalnumber=shift.get("fiscalNumber"),
                        cashregnumber=shift.get("cashRegNumber"),
                        cashregserial=shift.get("cashRegSerial"),
                        opendate=shift.get('openDate'),
                        closedate=shift.get('closeDate'),
                        acceptdate=shift.get('acceptDate'),
                        managerid=shift.get("managerId"),
                        responsibleuserid=shift.get("responsibleUserId"),
                        sessionstartcash=shift.get("sessionStartCash"),
                        payorders=shift.get("payOrders"),
                        sumwriteofforders=shift.get("sumWriteoffOrders"),
                        salescash=shift.get("salesCash"),
                        salescredit=shift.get("salesCredit"),
                        salescard=shift.get("salesCard"),
                        payin=shift.get("payIn"),
                        payout=shift.get("payOut"),
                        payincome=shift.get("payIncome"),
                        cashremain=shift.get("cashRemain"),
                        cashdiff=shift.get("cashDiff"),
                        sessionstatus=shift.get("sessionStatus"),
                        conceptionid=shift.get("conceptionId"),
                        pointofsaleid=shift.get("pointOfSaleId")
                    )
                    db.add(new_entry)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError("{e}")    

def refTaxCategoryInsert(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='ResponseTaxCategoryUpdate',key='data')
    
        for category in data:
            ex_entry = db.query(model).filter(model.taxcategory_id == category.get("id")).first()   
            if ex_entry:
                ex_entry.deleted =category.get("deleted")
                ex_entry.name = category["name"]
                ex_entry.vatpercent = category["vatPercent"]   
            else:
                new_etnry = model(
                taxcategory_id = category["id"],
                deleted = category.get("deleted"),
                name = category["name"],
                vatpercent = category["vatPercent"]
                )
                db.add(new_etnry)
        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError("{e}")
    

def insertOutgoingInvoice(**kwargs):
    try:
        model = kwargs['model']
        db = next(get_db())
        data = kwargs['ti'].xcom_pull(task_ids='OutgoingInvoice', key='data')
        tree = ET.fromstring(data)
    
        for document in tree.findall("document"):
            document_id = document.find("id").text
            document_number = document.find("documentNumber").text
            date_incoming = document.find("dateIncoming").text
            status = document.find("status").text
            default_store_id = document.find("defaultStoreId").text
            counteragent_id = document.find("counteragentId").text

            items = document.find("items")
            for item in items.findall("item"):
                new_entry = model(
                    document_id=document_id,
                    document_number=document_number,
                    date_incoming=date_incoming,
                    status=status,
                    store_id=default_store_id,
                    counteragent_id=counteragent_id,
                    product_id=item.find("productId").text,
                    product_article=item.find("productArticle").text,
                    price=float(item.find("price").text),
                    price_without_vat=float(item.find("priceWithoutVat").text),
                    amount=float(item.find("amount").text),
                    sum=float(item.find("sum").text),
                    discount_sum=float(item.find("discountSum").text),
                    vat_percent=float(item.find("vatPercent").text),
                    vat_sum=float(item.find("vatSum").text),
                )
                db.add(new_entry)

        db.commit()
        kwargs['ti'].xcom_push(key='TaskState', value=True)

    except Exception as e:
        db.rollback()
        print(e)
        kwargs['ti'].xcom_push(key='TaskState', value=False)
        raise RuntimeError('{e}')