from fastapi import FastAPI, APIRouter,status,Request
from fastapi.responses import JSONResponse
from routs.schemes.nlp import pushNLPRequest, searchRequest
from models.project_model import ProjectModel
from models.chunkModel import chunkModel
from controllers import NLPController
from models.enums.responsEnums import ResponseEnum
import logging

logger = logging.getLogger('uvicorn.error')
nlp_router=APIRouter(
    tags=["api_v1", "nlp"],
    prefix="/api/v1/nlp"
)

@nlp_router.post("/index/push/{project_id}")
async def push_data_to_index(request: Request, project_id: str,puch_request: pushNLPRequest ):
     project_Model =await ProjectModel.create_instance(db_client=request.app.mongodb)
     chunck_model= await chunkModel .create_instance(db_client=request.app.mongodb)
     project= await project_Model.get_project_or_create_one(project_id=project_id)
     if not project:
   
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "signal": ResponseEnum.project_not_found.value
            })
     nlp_controller=NLPController(
         vector_db_client=request.app.vector_db_client,
         ganeration_client=request.app.ganeration_client,
         embedding_client=request.app.embedding_client
         )
     has_recodrs=True
     page_num=1
     inserted_items_count = 0
     idx=0
     while has_recodrs:
         
        page_chunks= await chunck_model.get_project_chunks(project_id=project.id,page_num=page_num)
        if len(page_chunks)==0:
            page_num+=1
        if not page_chunks or len(page_chunks)==0:
            has_recodrs=False
            break
        chunks_ids=list(range( idx, idx + len(page_chunks)))
        idx+=len(page_chunks)
        is_inserted= nlp_controller.index_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset= puch_request.do_reset,
            chunk_ids=chunks_ids
            )
        if not is_inserted:
            logger.error(f"Failed to index chunks for project {project.project_id} on page {page_num}")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
                "signal": ResponseEnum.INSERT_INTO_VECTOR_DB_FAILED.value
                })
        inserted_items_count += len(page_chunks)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={
                "signal": ResponseEnum.INSERT_INTO_VECTOR_DB_SUCCESS.value,
                "inserted_items_count": inserted_items_count
            }
            )
     

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
     project_Model =await ProjectModel.create_instance(db_client=request.app.mongodb)
     project= await project_Model.get_project_or_create_one(project_id=project_id)
     if not project:
   
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
            "signal": ResponseEnum.project_not_found.value
            })
     nlp_controller=NLPController(
         vector_db_client=request.app.vector_db_client,
         ganeration_client=request.app.ganeration_client,
         embedding_client=request.app.embedding_client
         )
     collection_info= nlp_controller.get_vector_db_collection_info(project=project)
     if not collection_info:
         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
             "signal": ResponseEnum.VECTOR_DB_COLLECTION_NOT_FOUND.value
             })
   
     return JSONResponse(
         status_code=status.HTTP_200_OK, content={
             "signal": ResponseEnum.VECTOR_DB_COLLECTION_INFO_RETRIEVED.value,
             "collection_info": collection_info
         }
         )
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: searchRequest):
        project_Model =await ProjectModel.create_instance(db_client=request.app.mongodb)
        project= await project_Model.get_project_or_create_one(project_id=project_id)
        if not project:
    
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={
                "signal": ResponseEnum.project_not_found.value
                })
        nlp_controller=NLPController(
            vector_db_client=request.app.vector_db_client,
            ganeration_client=request.app.ganeration_client,
            embedding_client=request.app.embedding_client
            )
        
        search_results= nlp_controller.search_vector_db(
            project=project,
            text=search_request.text,
            limit=search_request.limit
            )
        if not search_results :
           return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
               "signal": ResponseEnum.VECTOR_DB_SEARCH_FAILED.value
               })

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={
                "signal":  ResponseEnum.VECTOR_DB_SEARCH_SUCCESS.value,
                "results": search_results
            }
            )