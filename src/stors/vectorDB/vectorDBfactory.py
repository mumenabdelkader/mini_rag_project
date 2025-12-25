from stors.vectorDB.providers.qdrantDB import QdrantDb  # ← استدعاء الكلاس مش الموديل
from .vectorDBenums import VectorDBEnums
from controllers.BaseController import BaseController

class VectorDBFactory:
    def __init__(self,config):
        self.config=config
        self.basecontroller=BaseController()
    def create(self ,providers):
        if providers == VectorDBEnums.QDRANT.value:
           
            db_path = self.basecontroller.get_db_path(db_name=self.config.VECTOR_DB_PATH)

            return QdrantDb(
                db_path=db_path,
                distanc_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        return None
        