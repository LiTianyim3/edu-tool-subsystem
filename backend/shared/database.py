from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://Litianyi:USTB_zsgc123@rm-2zeg0q709d84e28mzeo.mysql.rds.aliyuncs.com:3306/teaching_assistant"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
