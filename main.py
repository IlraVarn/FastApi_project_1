from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers.orders import router as orders_router
#from routers.items import router as items_router
from routers.auth import router as auth_router
from routers.dev_onboarding import router as dev_onboarding_router
from routers.organizations import router as organizations_router



app = FastAPI()

app.include_router(orders_router)
app.include_router(dev_onboarding_router)
app.include_router(organizations_router)

# app.include_router(customers_router)
# app.include_router(items_router)
# app.include_router(auth_router)


@app.get('/health')
def health_check():
    return {'ok' : True}

