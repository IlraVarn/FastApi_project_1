from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers.dev_onboarding import router as dev_onboarding_router
from routers.organizations import router as organizations_router
from routers.gates import router as gates_router



app = FastAPI()

app.include_router(gates_router)
app.include_router(dev_onboarding_router)
app.include_router(organizations_router)





@app.get('/health')
def health_check():
    return {'ok' : True}

