from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from routs import base, data, nlp
from stors.LLM.llmFactory import LLMProviderFactory
from stors.vectorDB.vectorDBfactory import VectorDBFactory
from stors.LLM.templets.templet_parser import Templete_Parser

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.mongo_db_url)
    app.mongodb = app.mongodb_client[settings.mongo_db_name]
    llm_provider_factory=LLMProviderFactory(settings)
    vector_db_provider_factory= VectorDBFactory(settings)
    app.ganeration_client=llm_provider_factory.create(provider= settings.GENERATION_BACKEND)
    app.ganeration_client.set_gnration_model(model_id= settings.GENERATION_MODEL_ID )

    app.embedding_client=llm_provider_factory.create(provider=settings.EMPEDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id= settings.EMPEDDING_MODEL_ID,
        embedding_size_limit= settings.EMPEDDING_MODEL_SIZE
        )

    app.vector_db_client = vector_db_provider_factory.create(settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()
    print("📌 MongoDB Connected")
    app.templete_parser= Templete_Parser(lang=settings.PRIMARY_LANGUAGE,defoult_lang=settings.DEFOULT_LANGUAGE)

    yield  # ← هنا التطبيق يشتغل

    # shutdown
    app.mongodb_client.close()
    app.vector_db_client.disconnect()
    print("📌 MongoDB Closed")


app = FastAPI(lifespan=lifespan)

app.include_router(base.baseRouter)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
