from sqlalchemy import create_engine, Column, Integer, String, URL
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from config import USERNAME, PASSWORD, DBHOSTNAME, PORT, DBNAME


Base = declarative_base()

# DATABASE_URL = f"postgresql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}"

DATABASE_URL = URL.create(
    "postgresql",
    username=USERNAME,
    password=PASSWORD,
    host=DBHOSTNAME,
    port=PORT,
    database=DBNAME,
)


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class YourTable(Base):
    __tablename__ = "db_duplication_test"

    nocodbid = Column(Integer, primary_key=True, index=True)

    title = Column(String, index=True)
    description = Column(String, index=True)
