from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.dev_onboarding import router as dev_onboardin_router
from app.routers.organizations import router as organizations_router
from app.routers.gates import router as gates_router
from app.routers.evidence import router as evidence_router

# for database test endpoint
from fastapi import Depends
from sqlmodel import Session
from sqlalchemy import text
from app.db import get_session

app = FastAPI()

app.include_router(gates_router)
app.include_router(organizations_router)
app.include_router(evidence_router)






@app.get('/health')
def health_check():
    return {'ok' : True}



@app.get("/db-check")
def check_database(
    session: Session = Depends(get_session),
):
    session.execute(
        text("SELECT COUNT(*) FROM organizations")
    ).scalar_one()

    return {"database": "connected"}