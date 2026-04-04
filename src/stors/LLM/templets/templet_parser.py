import os
class Templete_Parser:
    def __init__(self,lang:str,defoult_lang:str="en"):
        self.current_path =os.path.dirname(os.path.abspath(__file__))
        self.defoult_lang=defoult_lang
        self.lang=lang


    def set_lang(self,lang:str):
       if not lang:
              self.lang=self.defoult_lang
       if lang and os.path.exists(os.path.join(self.current_path,"locales",lang)):
           self.lang=lang

       else:
           self.lang=self.defoult_lang
   
    def get_rag_templet(self, groub:str,key:str,vars:dict={}):
        if not groub or not key:
            return None
        groub_path=os.path.join(self.current_path,"locales",self.lang if self.lang else self.defoult_lang,f"{groub}.py")
        if not os.path.exists(groub_path):
            groub_path=os.path.join(self.current_path,"locales",self.defoult_lang,f"{groub}.py")
        if not os.path.exists(groub_path):
            return None
        module=__import__(f"stors.LLM.templets.locales.{self.lang if self.lang else self.defoult_lang}.{groub}", fromlist=[groub])
        if not module:
            return None
        key_attribute=getattr(module,key)
        # If it's an object with substitute (e.g., string.Template), use it
        substitute = getattr(key_attribute, 'substitute', None)
        if callable(substitute):
            return substitute(vars)

        # If it's a plain string, try str.format first, then fall back to Template
        if isinstance(key_attribute, str):
            try:
                return key_attribute.format(**(vars or {}))
            except Exception:
                from string import Template
                try:
                    return Template(key_attribute).safe_substitute(vars or {})
                except Exception:
                    return key_attribute

        # As a last resort, coerce to string
        try:
            return str(key_attribute)
        except Exception:
            return None
