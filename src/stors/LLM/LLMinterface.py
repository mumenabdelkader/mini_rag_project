from abc import ABC, abstractmethod

class LLMInterface (ABC):

    @abstractmethod
    def set_gnration_model(self, model_id: str):
        
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size_limit: int = None):
        pass
    @abstractmethod
    def generate_text(self, prompt: str,chat_history:list =[],max_output_tokens:int=None, temperature:float=None) :
        pass
    @abstractmethod
    def embedding_text(self, text: str,decument_type=None) :
        pass
    @abstractmethod
    def construct_prompt(self,prompt: str, role: str) :
        pass