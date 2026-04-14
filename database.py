import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# You can set the DATABASE_URL environment variable to point to your database, or it will default to a local SQLite database named logs.db
DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///logs.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SSL required for Neon
if "neon.tech" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

ENGINE = create_engine(DB_PATH, connect_args=connect_args)

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