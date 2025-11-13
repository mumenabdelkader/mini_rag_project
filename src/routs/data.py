from fastapi import FastAPI, APIRouter,Depends,UploadFile,status
from fastapi.responses import JSONResponse
from helpers.config import get_settings
from controllers import DataController,projectController
import os
import aiofiles
from models.enums import ResponseEnum
import logging
logger = logging.getLogger('uvicorn.error')
data_router=APIRouter(
    tags=["api_v1", "data"],
    prefix="/api/v1/data"
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str,file:UploadFile,app_settings=Depends(get_settings)):
    controller = DataController()
    is_valid, result_signal = await controller.validat_upload_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,
                "result_signal": result_signal
            }
        )
    project_dir= projectController().get_project_path(project_id=project_id)
    file_path ,file_id = controller.genrate_uniq_file_path(original_filename=file.filename, project_id=project_id)
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.file_defoult_chunk_size):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result_signal": ResponseEnum.file_upload_failed.value,
                "error": str(e)
            }
        )
    return JSONResponse(
          content={
                    "result_signal": ResponseEnum.file_uploaded_success.value
                    ,"file_id":file_id
                }
        )