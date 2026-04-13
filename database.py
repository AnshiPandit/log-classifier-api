from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# This creates a local SQLite file called logs.db
# In production you'd swap this URL for PostgreSQL
ENGINE = create_engine("sqlite:///logs.db", connect_args={"check_same_thread": False})

Base = declarative_base()

# This class = one table in your database
class LogRecord(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    label = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Creates the table if it doesn't exist yet
Base.metadata.create_all(bind=ENGINE)

SessionLocal = sessionmaker(bind=ENGINE)