from pydantic import BaseModel
from typing import List, Optional
class processeRequest(BaseModel):
    project_id: str
    chunk_size: Optional[int]= 1024*1024*2  # 1 MB
    overlap_size: Optional[int]= 1024*10  # 10 KB
    do_reset: Optional[int]= 0
    
