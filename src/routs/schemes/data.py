from pydantic import BaseModel
from typing import List, Optional
class processeRequest(BaseModel):
    file_id:str = None
    chunk_size: Optional[int]= 600  
    overlap_size: Optional[int]= 50  
    do_reset: Optional[int]= 0
    
