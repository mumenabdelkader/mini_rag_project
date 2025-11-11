from fastapi import FastAPI
from routs import base
from dotenv import load_dotenv

load_dotenv(".env")

app = FastAPI()

app.include_router(base.baseRouter)