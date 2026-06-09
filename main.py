from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import create_db_and_tables
from routers.orders import router as orders_router
from routers.customers import router as customers_router
from routers.items import router as items_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(orders_router)
app.include_router(customers_router)
app.include_router(items_router)

@app.get('/health')
def health_check():
    return {'ok' : True}