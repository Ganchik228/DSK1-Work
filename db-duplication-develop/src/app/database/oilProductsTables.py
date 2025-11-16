from .database import Base
from sqlalchemy import Column, Integer, Numeric, Date


#                 #
# OIL PRODUCTS DB #
#                 #


class WagonPriceDynamic(Base):
    __tablename__ = "wagonpricedynamic"
    __table_args__ = {"schema": "oilprices"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    dt = Column(Numeric, index=True)
    ai92 = Column(Numeric, index=True)
    ai95 = Column(Numeric, index=True)


class GeneralPriceDynamic(Base):
    __tablename__ = "generalpricedynamic"
    __table_args__ = {"schema": "oilprices"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    dt = Column(Numeric, index=True)
    ai92 = Column(Numeric, index=True)
    ai95 = Column(Numeric, index=True)
    gaz = Column(Numeric, index=True)
    ai100 = Column(Numeric, index=True)


class StraightPriceDynamic(Base):
    __tablename__ = "straightpricedynamic"
    __table_args__ = {"schema": "oilprices"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    startdate = Column(Date, index=True)
    enddate = Column(Date, index=True)
    dt = Column(Numeric, index=True)
    ai92 = Column(Numeric, index=True)
    ai95 = Column(Numeric, index=True)


class EoilPriceDynamic(Base):
    __tablename__ = "eoilpricedynamic"
    __table_args__ = {"schema": "oilprices"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    dt = Column(Numeric, index=True)
    ai92 = Column(Numeric, index=True)
    ai95 = Column(Numeric, index=True)
