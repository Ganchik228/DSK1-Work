from .database import Base
from sqlalchemy import Column, Integer, Numeric, Date

#                      #
# GSM DELIVERY  NB CTX #
#                      #


class Maz045(Base):
    __tablename__ = "maz045"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Maz060(Base):
    __tablename__ = "maz060"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Sitrak142(Base):
    __tablename__ = "sitrak142"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Sitrak191(Base):
    __tablename__ = "sitrak191"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Maz354(Base):
    __tablename__ = "maz354"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Maz370(Base):
    __tablename__ = "maz370"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Maz315(Base):
    __tablename__ = "maz315"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)


class Sitrak107(Base):
    __tablename__ = "sitrak107"
    __table_args__ = {"schema": "gsmnbctx"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)
