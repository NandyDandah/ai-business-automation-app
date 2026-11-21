import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./automation.db")
engine_options = {}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Automation(Base):
    __tablename__ = "automations"

    id = Column(Integer, primary_key=True, index=True)
    customer_email = Column(String, nullable=True)
    customer_message = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(String, default="New")
    lead_score = Column(Integer, default=0)
    follow_up_date = Column(String, default="")
    notes = Column(Text, default="")
    ai_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)

 
class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    clinic_name = Column(String, nullable=False)
    website = Column(String, default="")
    town = Column(String, default="")
    postcode = Column(String, default="")
    public_email = Column(String, default="")
    phone = Column(String, default="")
    contact_name = Column(String, default="")
    contact_role = Column(String, default="")
    source_url = Column(String, nullable=False)
    contact_source_url = Column(String, default="")
    fit_score = Column(Integer, default=0)
    fit_summary = Column(Text, default="")
    status = Column(String, default="New")
    fingerprint = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

