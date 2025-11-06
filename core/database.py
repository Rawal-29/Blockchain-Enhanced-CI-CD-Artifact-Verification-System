from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker
from core.config import DB_URL

engine = create_engine(DB_URL, echo=False)
metadata = MetaData()

verification_table = Table(
    "verifications",
    metadata,
    Column("artifact_hash", String, primary_key=True),
    Column("status", String)
)

metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
