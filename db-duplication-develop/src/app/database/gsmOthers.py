from .database import Base
from sqlalchemy import Column, Integer, Numeric, Date

#               #
#   GSM OTHERS  #
#               #


class AllTransp(Base):
    __tablename__ = "alltransport"
    __table_args__ = {"schema": "gsmothers"}

    nocodbid = Column(Integer, primary_key=True, index=True)

    date = Column(Date, index=True)
    plan_tonn = Column(Numeric, index=True)
    fact_tonn = Column(Numeric, index=True)
