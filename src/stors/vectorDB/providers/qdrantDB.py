from qdrant_client import models,QdrantClient
from ..vectorDbinterface import VectorDBInterface
from ..vectorDBenums import DistanceMethodEnums
import logging

class QdrantDb (VectorDBInterface):
    def __init__(self,db_path:str,distanc_method:str):
       
       self.client=None
       self.db_path=db_path
       self.distanc_method=distanc_method
       self.logger=logging.getLogger(__name__) 

       if self.distanc_method ==DistanceMethodEnums.COSINE.value:
           self.distanc_method=models.Distance.COSINE
       elif self.distanc_method ==DistanceMethodEnums.DOT.value:
           self.distanc_method=models.Distance.DOT

          

    def  connect(self):
        self.client= QdrantClient(path= self.db_path)
    def disconnect (self):
        self.client= None

    def isCollectionExisted(self, collection_name):
        return self.client.collection_exists(collection_name= collection_name)
    def listAllCollection(self):
        return self.client.get_collections()
    def getCollectionInfo(self, collection_name):
        return self.client.get_collection (collection_name=collection_name)
    def deleteCollection(self, collection_name):
        if self.isCollectionExisted(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    def createCollection(self, collection_name, embedding_size, do_reset = False):
        if do_reset :
           _= self.deleteCollection(collection_name=collection_name)
        if not self.isCollectionExisted(collection_name=collection_name):
            _=self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distanc_method
                )
            )
            return True
        return False
    def insertOne(self, collection_name, text, vector, metadate, record_id = None):
        if not self.isCollectionExisted(collection_name=collection_name):
            self.logger.error("this collection is none exist {collection_name}")
            return False
        try:
            _=self.client.upload_points(                      # في الفيديو upload_records
                collection_name= collection_name,
                points=[   #records بس ي الفيديو 
                    models.PointStruct(
                        id=[record_id] ,
                        vector=vector,
                        payload={
                            "text":text,"metadate":metadate
                        }
                    )
                ]
                
            )
        except Exception as e:
            self.logger.error("error while insertion one  {e}")
            return False


        return True
    def insertMany(self, collection_name, text, vector, metadate, record_ids, batch_size = 50):
       
         if metadate is None:
             metadate=[None]*len(text)
         if record_ids is None:
             record_ids=list(range(0,len(text)))
         for i in range(0,len(text),batch_size):
             batch_end =i+batch_size
             batch_texts=text[i:batch_end]
             batch_vectors=vector[i:batch_end]
             batch_metadate=metadate[i:batch_end]
             batch_record_ids=record_ids[i:batch_end]

             batch_records=[
                 models.Record(
                     id=batch_record_ids[x],
                     vector=batch_vectors[x],
                     payload={
                         "text":batch_texts[x],
                         "metadate":batch_metadate[x]
                     }
                 )
                 for x in range (len(batch_texts))
             ]
             try:
                _=self.client.upload_points(
                    collection_name=collection_name,
                    points=batch_records
                )
             except Exception as e:
                self.logger.error("error while inserting batch {e}")
                return False
            
         return True
    
    def searchByVector(self, collection_name, query_vector, limit):
        return self.client.query_points(
            collection_name=collection_name,
            query=query_vector,   # ✅ الاسم الصح
            limit=limit,
            with_payload=True,
            with_vectors=False
        )


          
    
    

    