from fastapi import FastAPI, APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings
from controllers import DataController, ProjectController, ProcessController
import os
import aiofiles
from models.enums import ResponseEnum
import logging
from .schemes.data import processeRequest
from models.project_model import ProjectModel
from models.db_schemes.data_chunk import DataChunk
from models.chunkModel import chunkModel
logger = logging.getLogger('uvicorn.error')
data_router=APIRouter(
    tags=["api_v1", "data"],
    prefix="/api/v1/data"
)

@data_router.post("/upload/{project_id}")
async def upload_data( request: Request , project_id: str,file:UploadFile,app_settings=Depends(get_settings)):
   
    project_Model =await ProjectModel.create_instance(db_client=request.app.mongodb)
   
    project= await project_Model.get_project_or_create_one(project_id=project_id)
   
    controller = DataController()
    is_valid, result_signal = await controller.validat_upload_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "is_valid": is_valid,
                "result_signal": result_signal,
            }
        )
    # project_dir = ProjectController().get_project_path(project_id=project_id)
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
                    ,"project_id":str(project.id)
                    
                    
                }
        )

@data_router.post("/process/{project_id}")

async def process_endpoint(project_id:str,request: Request,process_request: processeRequest):
    file_id= process_request.project_id
    chank_size= process_request.chunk_size
    chunk_overlap= process_request.overlap_size
    do_reset= process_request.do_reset

    project_model  =await ProjectModel.create_instance(db_client=request.app.mongodb)

    project= await project_model .get_project_or_create_one(project_id=project_id)

  
    process_controller = ProcessController(project_id=project_id)
    file_content= process_controller.get_file_content(file_id=file_id)
    chunks= process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chank_size,
        chunk_overlap=chunk_overlap
    )
    if chunks is None or len(chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result_signal": ResponseEnum.file_processing_failed.value,
                "error": "No chunks were created from the file content."
            }
        )
    file_chunks_records= [
       DataChunk(
            chunk_txt =chunk.page_content, 
            chunk_metadata = chunk.metadata,
            chunk_order =i+1,
            chunk_project_id=project.id

       )
        for i,chunk  in enumerate(chunks)
    ]
    chunk_model=await chunkModel.create_instance(db_client=request.app.mongodb)
    if do_reset ==1:
        
        deleted_count= await chunk_model.delete_chunks_by_project_id(prject_id=project.id)
        logger.info(f"Deleted {deleted_count} chunks for project ID {project_id} due to reset request.")

    
    noChunks= await chunk_model.insert_many_chunks(file_chunks_records)
    logger.info(f"Inserted {noChunks} chunks into the database for file ID {file_id}.")

    return JSONResponse(
          content={
                    "signal": ResponseEnum.file_processed_success.value,
                    "inserted_chunks": noChunks
                    
                }
                )