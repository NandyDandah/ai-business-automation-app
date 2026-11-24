import os
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint,
    create_engine, inspect, text,
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
    # Keep provider-enriched contact data distinct from information published
    # by the business itself, and retain the lookup provenance/status.
    enriched_email = Column(String, default="")
    enriched_phone = Column(String, default="")
    enriched_contact_name = Column(String, default="")
    enriched_contact_role = Column(String, default="")
    enrichment_provider = Column(String(80), default="")
    enrichment_status = Column(String(80), default="")
    enrichment_confidence = Column(String(80), default="")
    enrichment_source_url = Column(String(1000), default="")
    source_url = Column(String, nullable=False)
    contact_source_url = Column(String, default="")
    fit_score = Column(Integer, default=0)
    fit_summary = Column(Text, default="")
    status = Column(String, default="New")
    fingerprint = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    """A single-owner outreach brief for a group of saved businesses."""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    industry = Column(String(120), nullable=False, default="")
    business_type = Column(String(120), nullable=False, default="")
    region = Column(String(120), nullable=False, default="")
    country = Column(String(120), nullable=False, default="")
    offer = Column(Text, nullable=False, default="")
    proof = Column(Text, nullable=False, default="")
    tone = Column(String(80), nullable=False, default="Professional")
    language = Column(String(80), nullable=False, default="English")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class CampaignProspect(Base):
    """Campaign-specific draft and review state; never sends messages."""
    __tablename__ = "campaign_prospects"
    __table_args__ = (
        UniqueConstraint("campaign_id", "prospect_id", name="uq_campaign_prospect"),
    )

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False, index=True)
    draft_subject = Column(String(240), nullable=False, default="")
    draft_body = Column(Text, nullable=False, default="")
    draft_reason = Column(Text, nullable=False, default="")
    draft_status = Column(String(24), nullable=False, default="not_drafted", index=True)
    pipeline_stage = Column(String(24), nullable=False, default="new", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)


class HomeownerInquiry(Base):
    """Minimal homeowner request data, kept separate from business prospects."""
    __tablename__ = "homeowner_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(320), nullable=False, default="")
    phone = Column(String(40), nullable=False, default="")
    postcode = Column(String(16), nullable=False)
    property_type = Column(String(40), nullable=False)
    heating_type = Column(String(40), nullable=False)
    ownership = Column(String(40), nullable=False)
    timeframe = Column(String(40), nullable=False)
    consent_contact = Column(Boolean, nullable=False, default=False)
    consent_share = Column(Boolean, nullable=False, default=False)
    consent_version = Column(String(40), nullable=False)
    consented_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(32), nullable=False, default="new", index=True)
    matched_installer_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)


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
        "enriched_email": "VARCHAR(320) NOT NULL DEFAULT ''",
        "enriched_phone": "VARCHAR(80) NOT NULL DEFAULT ''",
        "enriched_contact_name": "VARCHAR(160) NOT NULL DEFAULT ''",
        "enriched_contact_role": "VARCHAR(160) NOT NULL DEFAULT ''",
        "enrichment_provider": "VARCHAR(80) NOT NULL DEFAULT ''",
        "enrichment_status": "VARCHAR(80) NOT NULL DEFAULT ''",
        "enrichment_confidence": "VARCHAR(80) NOT NULL DEFAULT ''",
        "enrichment_source_url": "VARCHAR(1000) NOT NULL DEFAULT ''",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(
                    text(f"ALTER TABLE prospects ADD COLUMN {name} {definition}")
                )
