from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite for development
SQLALCHEMY_DATABASE_URL = "sqlite:///./pdf_extractor.db"

# For MySQL production, use:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/database"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
