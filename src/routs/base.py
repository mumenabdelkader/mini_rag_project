from fastapi import FastAPI, APIRouter,Depends
from helpers.config import get_settings
baseRouter=APIRouter(
    tags=["api_v1"],
    prefix="/api/v1/data"

)

@baseRouter.get("/")
def welcome(app_settings=Depends(get_settings)):
    
    appname=app_settings.app_name
    app_version=app_settings.app_version
    return{
     "app_name":appname,
     "APP_VERSION":app_version
    }