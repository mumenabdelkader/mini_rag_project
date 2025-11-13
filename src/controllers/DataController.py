from .BaseController import BaseController
from fastapi import UploadFile
from models.enums import ResponseEnum 
from .projectController import projectController
import os
import re
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.sizScale = 1024 * 1024  # 1 MB

    async def validat_upload_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.File_ALLOWED_TYPS:
            return False, ResponseEnum.file_type_not_allowed.value

        # حساب الحجم الفعلي للملف
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # نرجع المؤشر لبداية الملف بعد القراءة

        if file_size > self.app_settings.FILE_MAX_SIZE * self.sizScale:
            return False, ResponseEnum.file_size_exceeded.value

        return True, ResponseEnum.file_valid.value
    def genrate_uniq_file_path(self,original_filename: str, project_id: str) -> str:
        randum_key = self.generate_randum_string()
        project_path= projectController().get_project_path(project_id=project_id)
        clean_filename = self.get_clean_filename(original_filename)
        new_filePath = os.path.join(project_path, f"{randum_key}_{clean_filename}")
        while os.path.exists(new_filePath):
            randum_key = self.generate_randum_string()
            new_filePath = os.path.join(project_path, f"{randum_key}_{clean_filename}")
        return new_filePath ,f"{randum_key}_{clean_filename}"


    def get_clean_filename(self,filename:str)->str:
        # إزالة الأحرف غير المسموح بها من اسم الملف
        clean_name = re.sub(r'[^\w.]', '_', filename)
        clean_name = re.sub(r' ', '_', clean_name) 
        return clean_name