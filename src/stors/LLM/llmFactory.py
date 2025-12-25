from .llmEnums import LLMEnums
from .providers import openAI_provider
from .providers.cohereProvider import CohereProvider
class LLMProviderFactory :
    def __init__ (self,config :dict):
        self.config=config 

    def create(self ,provider:str ):
        if provider == LLMEnums.OPENAI.value:
            return openAI_provider(
                
                api_key= self.config.OPENAI_API_KEY,
                api_url=  self.config.OPENAI_API_URL,
                defaulet_input_max_characters=self.config.INPUT_DEFOULT_MAX_SIZE,
                defaulet_output_token_limit=self.config.GENERATION_DEFOULT_TOKENS, 
                defaulet_temperature=self.config.GENERATION_DEFOULT_TEMPRETUR
            )
        if provider == LLMEnums.COHERE.value:
            return CohereProvider(

                api_key=self.config.COHERE_API_KEY,
                defaulet_input_max_characters=self.config.INPUT_DEFOULT_MAX_SIZE,
                defaulet_output_token_limit=self.config.GENERATION_DEFOULT_TOKENS,
                defaulet_temperature=self.config.GENERATION_DEFOULT_TEMPRETUR
            ) 


