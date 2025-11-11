from fastapi import FastAPI, APIRouter
import os

baseRouter=APIRouter(
    tags=["api_v1"]
)

@baseRouter.get("/")
def welcome():
    appname=os.getenv("app_name")
    APP_VERSION=os.getenv("APP_VERSION")
    return{
     "app_name":appname,
     "APP_VERSION":APP_VERSION
    }