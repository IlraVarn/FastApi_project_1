from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers.dev_onboarding import router as dev_onboarding_router
from app.routers.organizations import router as organizations_router
from app.routers.gates import router as gates_router
from app.routers.evidence import router as evidence_router



app = FastAPI()

app.include_router(gates_router)
app.include_router(dev_onboarding_router)
app.include_router(organizations_router)
app.include_router(evidence_router)





@app.get('/health')
def health_check():
    return {'ok' : True}

