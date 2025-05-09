from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "examples.db");
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"


engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},  
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    echo=True  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base();

def get_db():
    db = SessionLocal()
    try: 
        yield db

    finally:
        db.close()    

