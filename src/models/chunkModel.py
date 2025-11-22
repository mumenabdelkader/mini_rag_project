from .baseDataModel import BaseDataModel
from .db_schemes import data_chunk
from .enums.dataBase_enum import DataBaseEnum
from pymongo import InsertOne
from bson import ObjectId


class chunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection_name = DataBaseEnum.collection_chunk_name
        self.collection = self.db_client[DataBaseEnum.collection_chunk_name.value]
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = chunkModel(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if self.collection_name not in all_collections:
            self.collection = self.db_client[DataBaseEnum.collection_chunk_name.value]
            indexes = data_chunk.DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_chunk(self, data_chunk: data_chunk.DataChunk):
        result = await self.collection.insert_one(data_chunk.dict(by_alias=True,exclude_unset=True))
        data_chunk._id = str(result.inserted_id) 
        return data_chunk

    async def get_chunks_by_file_id(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if result is None:
            return None
        return data_chunk.DataChunk(**result)

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            operations = [InsertOne(chunk.dict()) for chunk in batch]
            await self.collection.bulk_write(operations)
        return len(chunks)
    async def delete_chunks_by_project_id(self, prject_id: ObjectId):
        result = await self.collection.delete_many({"chunk_prject_id": prject_id})
        return result.deleted_count
