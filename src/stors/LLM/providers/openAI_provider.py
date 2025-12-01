from ..LLMinterface import LLMInterface
from ..llmEnums import openAIenums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str,api_url: str = None,defaulet_input_max_characters: int = 1000,defaulet_output_token_limit: int = 1000, defaulet_temperature: float = 0.1):
        self.api_key = api_key
        self.api_url = api_url
        self.defaulet_input_max_characters = defaulet_input_max_characters
        self.defaulet_output_token_limit = defaulet_output_token_limit
        self.defaulet_temperature = defaulet_temperature
        self.generation_model_id = None 
        self.embedding_model_id = None
        self.embedding_size_limit = None  # tokens
        self.client = OpenAI(api_key=self.api_key, api_url=self.api_url)
        self.logger = logging.getLogger(__name__)

    def prosses_text(self,text:str,decument_type=None):
        return text[:self.defaulet_input_max_characters].strip()
    def set_gnration_model(self, model_id: str):
        self.generation_model_id = model_id


    def set_embedding_model(self, model_id: str, embedding_size_limit: int ):
        self.embedding_model_id = model_id
        self.embedding_size_limit = embedding_size_limit  # tokens
    
    def generate_text(self, prompt: str,max_output_tokens:int=None
                   , chat_history:list =[]  , temperature:float=None) :
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None
        max_output_tokens = max_output_tokens if max_output_tokens  else self.defaulet_output_token_limit
        temperature = temperature if temperature  else self.defaulet_temperature
        
        chat_history.append( self.construct_prompt(prompt, openAIenums.user.value))
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Failed to get response from OpenAI.")
            return None
        return response.choices[0].message.content
    
    
    def embedding_text(self, text: str) :
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text
        )
        if not response or not response.data   or len(response.data) == 0:
            self.logger.error("Failed to get embedding from OpenAI.")
            return None
        return response.data[0].embedding
    

    def construct_prompt(self,prompt: str, role: str) :
        return{
            "role": role,
            "content": self.prosses_text(prompt)
        }
