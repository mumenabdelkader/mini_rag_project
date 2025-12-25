from pydantic import BaseModel
from typing import List, Optional

class pushNLPRequest(BaseModel):
   
    do_reset: bool = False

class searchRequest(BaseModel):
    text: str
    limit: Optional[int] = 5