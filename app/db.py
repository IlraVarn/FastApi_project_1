
import os
import app.models as models

from sqlmodel import Session, create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ilravarn@localhost:5432/fastapi_learning",
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)
    
def get_session():
    with Session(engine) as session:
        yield session


