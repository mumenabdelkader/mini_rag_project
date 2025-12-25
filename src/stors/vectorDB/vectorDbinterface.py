from abc import ABC ,abstractmethod
from typing import List

class VectorDBInterface(ABC):
    @abstractmethod 
    def connect (self):
        pass
    @abstractmethod 
    def disconnect (self):
        pass
    @abstractmethod 
    def isCollectionExisted (self,collection_name:str)->bool:
        pass
    @abstractmethod 
    def listAllCollection (self)-> List :
        pass
    @abstractmethod 
    def getCollectionInfo (self,collection_name:str)-> dict :
        pass
    @abstractmethod 
    def deleteCollection (self,collection_name:str) :
        pass
    @abstractmethod 
    def createCollection (self,collection_name:str, embedding_size:int, do_reset:bool=False) :
        pass

    @abstractmethod 
    def insertOne (self,collection_name:str,text:str,vector:list ,metadate:dict,record_id:str=None):
        pass

    @abstractmethod 
    def insertMany(self,collection_name:str,text:list,vector:list ,metadate:list,record_ids:list,batch_size:int=50):
        pass
    @abstractmethod 
    def searchByVector(self,collection_name:str,vector:list ,limit:int):
        pass

