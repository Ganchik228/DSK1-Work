from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped
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

database_url = URL.create(
    "postgresql",
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

engine = create_engine(database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
    print("Created tables:", list(Base.metadata.tables.keys()))

'''
IICO
'''

SCHEMA_IICO = {"schema": "prod"}

class refDepartments(Base):
    __tablename__ = "ref_departments"
    __table_args__ = SCHEMA_IICO

    id = Column(String, primary_key=True)
    department_id = Column(String)
    pointofsale_id = Column(String)
    pointofsale_name = Column(String)
    cashregister_id = Column(String)
    cashregister_name = Column(String)
    restaurantsection_id = Column(String)
    restaurantsection_name = Column(String)


class refPaymentType(Base):
    __tablename__ = "ref_paymenttype"
    __table_args__ = SCHEMA_IICO

    paymenttype_id = Column(String, primary_key=True)
    deleted = Column(Boolean)
    code = Column(String)
    name = Column(String)


class refPrice(Base):
    __tablename__ = "ref_price"
    __table_args__ = SCHEMA_IICO

    uid = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(String)
    product_id = Column(String)
    datefrom = Column(String)
    dateto = Column(String)
    taxcategory_id = Column(String)
    pricecategory_id = Column(String)
    price = Column(String)
    includecategory_id = Column(String)
    include = Column(Boolean)
    document_id = Column(String)


class refPriceCategories(Base):
    __tablename__ = "ref_pricecategories"
    __table_args__ = SCHEMA_IICO

    pricecategory_id = Column(String, primary_key=True)
    name = Column(String)
    deleted = Column(Boolean)
    code = Column(String)


class refProducts(Base):
    __tablename__ = "ref_products"
    __table_args__ = SCHEMA_IICO
    
    product_id = Column(String, primary_key=True)
    deleted = Column(Boolean)
    name = Column(String)
    taxcategory_id = (String)


class iicoPrices(Base):
    __tablename__ = "sales"
    __table_args__ = SCHEMA_IICO

    id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(String)
    paymenttransaction_id = Column(String)
    uniqorder_id = Column(String)
    departament_id = Column(String)
    session_id = Column(String)


class iicoPaymentsShifts(Base):
    __tablename__ = "paymentsshifts"
    __table_args__ = SCHEMA_IICO

    payment_id = Column(String, primary_key=True)
    date = Column(DateTime)
    creationdate = Column(DateTime)
    paymenttype_id = Column(String)
    type = Column(String)
    sum = Column(Numeric)
    actualsum = Column(Numeric)
    originalsum = Column(Numeric)
    status = Column(String)

    cashshift_id = Column(String)
    sessionnumber = Column(Integer)
    fiscalnumber = Column(Integer)
    cashregnumber = Column(Integer)
    cashregserial = Column(String)
    opendate = Column(DateTime)
    closedate = Column(DateTime)
    acceptdate = Column(DateTime, nullable=True)
    managerid = Column(String)
    responsibleuserid = Column(String)
    sessionstartcash = Column(Numeric)
    payorders = Column(Numeric)
    sumwriteofforders = Column(Numeric)
    salescash = Column(Numeric)
    salescredit = Column(Numeric)
    salescard = Column(Numeric)
    payin = Column(Numeric)
    payout = Column(Numeric)
    payincome = Column(Numeric)
    cashremain = Column(Numeric)
    cashdiff = Column(Numeric)
    sessionstatus = Column(String)
    conceptionid = Column(String, nullable=True)
    pointofsaleid = Column(String, nullable=True)


class refTaxCategory(Base):
    __tablename__ = "ref_taxcategory"
    __table_args__ = SCHEMA_IICO
    
    taxcategory_id = Column(String, primary_key=True)
    deleted = Column(Boolean)
    name = Column(String)
    vatpercent = Column(Numeric)


class OutgoingInvoice(Base):
    __tablename__ = "outgoinginvoice"
    __table_args__ = SCHEMA_IICO

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String)
    document_number = Column(String)
    date_incoming = Column(DateTime)
    status = Column(String)
    store_id = Column(String)
    counteragent_id = Column(String)

    product_id = Column(String)
    product_article = Column(String)
    price = Column(Numeric)
    price_without_vat = Column(Numeric)
    amount = Column(Numeric)
    sum = Column(Numeric)
    discount_sum = Column(Numeric)
    vat_percent = Column(Numeric)
    vat_sum = Column(Numeric)


'''
1С номенкратура
'''
SCHEMA_1C = "1c-wastepaper"

class Nomenclature(Base):
    __tablename__ = "nomenclature"
    __table_args__ = {"schema": SCHEMA_1C}

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = Column(String)
    name: Mapped[str] = Column(String)

