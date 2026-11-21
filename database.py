from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./automation.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Automation(Base):
    __tablename__ = "automations"

    id = Column(Integer, primary_key=True, index=True)
    customer_message = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    ai_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)