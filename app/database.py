import os
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Integer, String, Text, create_engine, inspect, text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, synonym


def _normalize_database_url(url: str) -> str:
    """Normalize Render's Postgres URL to the installed psycopg 3 driver."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite:///./automation.db")
)
engine_options = {"pool_pre_ping": True}
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


class Prospect(Base):
    """Industry-neutral business prospect with legacy column aliases."""
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    # Keep the original physical column names so existing SQLite/Postgres data
    # remains readable while the API uses business-neutral names.
    business_name = Column("clinic_name", String, nullable=False)
    clinic_name = synonym("business_name")
    website = Column(String, default="")
    city = Column("town", String, default="")
    town = synonym("city")
    postal_code = Column("postcode", String, default="")
    postcode = synonym("postal_code")
    region = Column(String(120), nullable=False, default="", server_default=text("''"))
    country = Column(String(120), nullable=False, default="", server_default=text("''"))
    industry = Column(String(120), nullable=False, default="", server_default=text("''"))
    business_type = Column(String(120), nullable=False, default="", server_default=text("''"))
    business_email = Column("public_email", String, default="")
    public_email = synonym("business_email")
    business_phone = Column("phone", String, default="")
    phone = synonym("business_phone")
    contact_name = Column(String, default="")
    contact_role = Column(String, default="")
    source_url = Column(String, nullable=False)
    contact_source_url = Column(String, default="")
    fit_score = Column(Integer, default=0)
    fit_summary = Column(Text, default="")
    status = Column(String, default="New")
    fingerprint = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    Base.metadata.create_all(bind=engine)

    # Add generic classification/location fields to an existing prospects
    # table without deleting or rewriting any saved records.
    inspector = inspect(engine)
    if not inspector.has_table("prospects"):
        return
    existing = {column["name"] for column in inspector.get_columns("prospects")}
    additions = {
        "region": "VARCHAR(120) NOT NULL DEFAULT ''",
        "country": "VARCHAR(120) NOT NULL DEFAULT ''",
        "industry": "VARCHAR(120) NOT NULL DEFAULT ''",
        "business_type": "VARCHAR(120) NOT NULL DEFAULT ''",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(
                    text(f"ALTER TABLE prospects ADD COLUMN {name} {definition}")
                )

