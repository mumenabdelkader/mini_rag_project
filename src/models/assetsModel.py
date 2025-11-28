from .baseDataModel import BaseDataModel
from .db_schemes import assets  
from .enums.dataBase_enum import DataBaseEnum
from models.db_schemes.assets import Asset
from pymongo import InsertOne
from bson import ObjectId


class assetsModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection_name = DataBaseEnum.collection_asset_name
        self.collection = self.db_client[DataBaseEnum.collection_asset_name.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = assetsModel(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if self.collection_name not in all_collections:
            self.collection = self.db_client[DataBaseEnum.collection_asset_name.value]
            indexes = assets.Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_asset(self, data_asset: assets.Asset):
        result = await self.collection.insert_one(data_asset.dict(by_alias=True, exclude_unset=True))
        data_asset.id = str(result.inserted_id) 
        return data_asset

    async def get_all_project_asset(self, asset_project_id: str, asset_type: str):
        records =await self.collection.find({
        "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type
        }).to_list(length=None)

        result = [
            Asset(**record)
              for record in records] 
        return result
        
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name})
        if record:
            return Asset(**record)
        return None

    # async def insert_many_assets(self, assets: list, batch_size: int = 100):
    #     for i in range(0, len(assets), batch_size):
    #         batch = assets[i:i + batch_size]
    #         operations = [InsertOne(asset.dict()) for asset in batch]
    #         await self.collection.bulk_write(operations)
    #     return len(assets)

    # async def delete_assets_by_project_id(self, project_id: ObjectId):
    #     result = await self.collection.delete_many({"asset_project_id": project_id})
    #     return result.deleted_count
    
