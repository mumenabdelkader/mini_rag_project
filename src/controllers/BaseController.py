from helpers.config import get_settings
import os
import random
import string
class BaseController:
 def __init__(self):
  self.app_settings=get_settings()
  self.base_dir=os.path.dirname(os.path.dirname(__file__))
  self.file_dir=os.path.join(self.base_dir,"assets","files")
  
 def generate_randum_string(self,length:int=12)->str:
     letters_and_digits = string.ascii_letters + string.digits
     result_str = ''.join(random.choices(letters_and_digits,k=length))
     return result_str