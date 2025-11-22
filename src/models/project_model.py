from .baseDataModel import BaseDataModel
from .db_schemes import project
from .enums.dataBase_enum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client:object):
        super().__init__(db_client)
        self.collection_name = DataBaseEnum.collection_project_name
        self.collection = self.db_client[DataBaseEnum.collection_project_name.value]
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = ProjectModel(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if self.collection_name not in all_collections:
             self.collection=    self.db_client[DataBaseEnum.collection_project_name.value]
             indexes = project.Project.get_indexes()
             for index in indexes:
                    await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_project(self, project:project):
        result = await self.collection.insert_one(project.dict( by_alias=True,exclude_unset=True))
        project.id =str(result.inserted_id) 
        return project
    async def get_project_or_create_one(self, project_id:str):
        record = await self.collection.find_one({"project_id":project_id})
        if record is None:
            new_project = project.Project(project_id=project_id)
            created_project = await self.create_project(new_project)
            return created_project
        return project.Project(**record)
    async def get_all_project(self, page:int=1, page_size:int=10):
        
        total_decoments = await self.collection.count_documents({})
        total_pages=total_decoments // page_size + (1 if total_decoments % page_size >0 else 0)

        course= self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects =[]
        async for doc in course:
            projects.append(project.Project(**doc))
        return projects, total_pages
           