from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from routs import base, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
    app.mongodb = app.mongodb_client[settings.mongo_db_name]
    print("📌 MongoDB Connected")

    yield  # ← هنا التطبيق يشتغل

    # shutdown
    app.mongodb_client.close()
    print("📌 MongoDB Closed")


app = FastAPI(lifespan=lifespan)

app.include_router(base.baseRouter)
app.include_router(data.data_router)
