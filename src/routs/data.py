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
from models.assetsModel import assetsModel
from models.db_schemes.assets import Asset
from bson.objectid import ObjectId
from models.enums.assetType import AssetTypeEnum
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
    

    assets_model= await  assetsModel.create_instance(db_client=request.app.mongodb)
    asset_resource= Asset(
            asset_project_id=ObjectId(project.id),
            asset_name=file_id ,
            asset_type=AssetTypeEnum.FILE,
            asset_size=os.path.getsize(file_path),
        )
    
    assets_record=await assets_model.create_asset(data_asset=asset_resource)

    return JSONResponse(
          content={
                    "result_signal": ResponseEnum.file_uploaded_success.value
                    ,"file_id":str(assets_record.id)
                    ,"project_id":str(project.id)
                    
                    
                }
        )

@data_router.post("/process/{project_id}")

async def process_endpoint(project_id:str,request: Request,process_request: processeRequest):
   
    chank_size= process_request.chunk_size
    chunk_overlap= process_request.overlap_size
    do_reset= process_request.do_reset

    project_model  =await ProjectModel.create_instance(db_client=request.app.mongodb)
    assets_model= await  assetsModel.create_instance(db_client=request.app.mongodb)

    project= await project_model .get_project_or_create_one(project_id=project_id)
    project_file_ids= {}
    if process_request.file_id is not None:
        asset_record= await assets_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )
        if asset_record is None:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result_signal": ResponseEnum.file_not_found.value,
                
            }
        )
        
        project_file_ids={
            asset_record.id : str(asset_record.asset_name)
        }
    else:
        
        project_files= await assets_model.get_all_project_asset(asset_project_id=project.id , asset_type=AssetTypeEnum.FILE.value)
        project_file_ids={ 
            record.id : str(record.asset_name)
            for record in project_files
            }
    if len( project_file_ids) ==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result_signal": ResponseEnum.no_files_to_process.value,
                
            }
        )
  
    process_controller = ProcessController(project_id=project_id)
    noChunks=0
    nofiles=0
    chunk_model=await chunkModel.create_instance(db_client=request.app.mongodb)

    if do_reset ==1:
            
            deleted_count= await chunk_model.delete_chunks_by_project_id(prject_id=project.id)
            logger.info(f"Deleted {deleted_count} chunks for project ID {project_id} due to reset request.")
        
    for asset_id,file_id in project_file_ids.items():

        file_content= process_controller.get_file_content(file_id=file_id)
        if file_content is None:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, 
            content={"signal": "File not found or has been deleted."}
                )
        if file_content is None:
            logger.error(f"Failed to load content for file ID {file_id}. Skipping processing.")
            continue
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
                chunk_project_id=project.id,
                chunk_asset_id=str(asset_id)

        )
            for i,chunk  in enumerate(chunks)
        ]
        
        
        noChunks += await chunk_model.insert_many_chunks(file_chunks_records)
        nofiles +=1
        logger.info(f"Inserted {noChunks} chunks into the database for file ID {file_id}.")
    
    return JSONResponse(
          content={
                    "signal": ResponseEnum.file_processed_success.value,
                    "inserted_chunks": noChunks
                    ,"processed_files": nofiles
                    
                }
                )
@data_router.delete("/reset-database")
async def reset_database(request: Request):
    try:
        # استدعاء الـ Model
        asset_model = await assetsModel.create_instance(db_client=request.app.mongodb)
        
        # تنفيذ دالة المسح الشامل
        deleted_assets_count = await asset_model.delete_all_assets()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK, 
            content={
                "signal": "Database cleaned successfully!",
                "deleted_files_count": deleted_assets_count
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={"signal": f"Error cleaning database: {str(e)}"}
        )