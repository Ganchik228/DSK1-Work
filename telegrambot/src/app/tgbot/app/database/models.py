from sqlalchemy import Column, UUID, String, TIMESTAMP
from sqlalchemy.orm import declarative_base


Base = declarative_base()
SCHEMA = "fd-tgbot"
class Reviews(Base):
    __tablename__ = "reviews"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID,primary_key=True)
    comment = Column(String)
    user_id = Column(UUID)
    role_id = Column(UUID)
    date_time = Column(TIMESTAMP)


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID,primary_key=True)
    chat_id = Column(String)
    name = Column(String)
    phone = Column(String)


class Roles(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema":SCHEMA}

    id = Column(UUID, primary_key=True)
    name = Column(String)

