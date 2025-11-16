create schema test;

create table test.sales (
    id serial Primary key,
    dish_id varchar,
    paymenttransaction_id varchar,
    uniqorder_id varchar,
    departament_id varchar,
    session_id varchar
);

create table test.paymentsshifts (
    payment_id varchar Primary key,
    date date,
    creationdate date,
    paymenttype_id varchar,
    type varchar,
    sum int,
    actualsum int,
    originalsum int,
    status varchar,

    cashshift_id varchar,
    sessionnumber int,
    fiscalnumber int,
    cashregnumber int,
    cashregserial varchar,
    opendate date,
    closedate date,
    acceptdate date,
    managerid varchar,
    responsibleuserid varchar,
    sessionstartcash Numeric,
    payorders Numeric,
    sumwriteofforders Numeric,
    salescash Numeric,
    salescredit Numeric,
    salescard Numeric,
    payin Numeric,
    payout Numeric,
    payincome Numeric,
    cashremain Numeric,
    cashdiff Numeric,
    sessionstatus varchar,
    conceptionid varchar,
    pointofsaleid varchar
);

create table test.ref_departments (
    id varchar Primary key,
    department_id varchar,
    pointofsale_id varchar,
    pointofsale_name varchar,
    cashregister_id varchar,
    cashregister_name varchar,
    restaurantsection_id varchar,
    restaurantsection_name varchar
);

create table test.ref_paymenttype (
    paymenttype_id varchar Primary key,
    deleted varchar,
    code varchar,
    name varchar
);

create table test.ref_price (
    uid serial Primary key,
    department_id varchar,
    product_id varchar,
    datefrom varchar,
    dateto varchar,
    taxcategory_id varchar,
    pricecategory_id varchar,
    price varchar,
    includecategory_id varchar,
    include boolean,
    document_id varchar
);

create table test.ref_pricecategories (
    pricecategory_id varchar Primary key,
    name varchar,
    deleted boolean,
    code varchar
);

create table test.ref_products (
    product_id varchar Primary key,
    deleted boolean,
    name varchar,
    taxcategory_id varchar
);

create table test.ref_taxcategory (
    taxcategory_id varchar Primary key,
    deleted boolean,
    name varchar,
    vatpercent Numeric
);

