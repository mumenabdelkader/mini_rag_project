from fastapi import FastAPI
from routs import base,data


app = FastAPI()

app.include_router(base.baseRouter)
app.include_router(data.data_router)