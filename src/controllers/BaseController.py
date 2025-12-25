from helpers.config import get_settings
import os
import random
import string
class BaseController:
 def __init__(self):
  self.app_settings=get_settings()
  self.base_dir=os.path.dirname(os.path.dirname(__file__))
  self.file_dir=os.path.join(self.base_dir,"assets","files")
  self.database_dir=os.path.join(
    self.base_dir,
    "assets",
    "database"
  )
  
 def generate_randum_string(self,length:int=12)->str:
     letters_and_digits = string.ascii_letters + string.digits
     result_str = ''.join(random.choices(letters_and_digits,k=length))
     return result_str
 def get_db_path(self , db_name:str):
    database_path=os.path.join(
        self.database_dir,
        db_name
    )
    if not os.path.exists(database_path):
        os.makedirs(database_path)
    return database_path 