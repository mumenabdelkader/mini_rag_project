from ..LLMinterface import LLMInterface
from ..llmEnums import cohereEnums, DecomentTypeEnums
import cohere
from cohere.errors import TooManyRequestsError
import logging
import time
from typing import List, Optional, Union


class CohereProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        defaulet_input_max_characters: int = 2000, # زيادة عدد الحروف للـ RAG
        defaulet_output_token_limit: int = 1000,
        defaulet_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.defaulet_input_max_characters = defaulet_input_max_characters
        self.defaulet_output_token_limit = defaulet_output_token_limit
        self.defaulet_temperature = defaulet_temperature

        self.generation_model_id: Optional[str] = None
        self.embedding_model_id: Optional[str] = None
        self.embedding_size_limit: Optional[int] = None
        self.enums = cohereEnums

        self.client = cohere.Client(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Utils
    # ------------------------------------------------------------------
    def prosses_text(self, text: str) -> str:
        return text[: self.defaulet_input_max_characters].strip()

    # ------------------------------------------------------------------
    # Model setters
    # ------------------------------------------------------------------
    def set_gnration_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size_limit: int):
        self.embedding_model_id = model_id
        self.embedding_size_limit = embedding_size_limit

    # ------------------------------------------------------------------
    # Text generation (مع منطق إعادة المحاولة الذكي)
    # ------------------------------------------------------------------
    def generate_text(
        self,
        prompt: str,
        max_output_tokens: Optional[int] = None,
        chat_history: Optional[List[dict]] = None,
        temperature: Optional[float] = None,
    ):
        if not self.client or not self.generation_model_id:
            self.logger.error("Cohere client or Model ID not initialized.")
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # انتظار تأميني بسيط لتقليل فرص التصادم
                time.sleep(2) 

                response = self.client.chat(
                    model=self.generation_model_id,
                    chat_history=chat_history or [],
                    message=self.prosses_text(prompt),
                    max_tokens=max_output_tokens or self.defaulet_output_token_limit,
                    temperature=temperature or self.defaulet_temperature,
                )
                return response.text if response else None

            except Exception as e:
                # التحقق إذا كان الخطأ بسبب تخطي عدد الطلبات (429)
                if "429" in str(e) or isinstance(e, TooManyRequestsError):
                    wait_time = (attempt + 1) * 12  # انتظار تصاعدي: 12، 24، 36 ثانية
                    self.logger.warning(f"Rate limit hit! Waiting {wait_time}s before retry {attempt+1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                
                self.logger.error(f"Error in generate_text: {str(e)}")
                break
        return None

    # ------------------------------------------------------------------
    # Embeddings (مع منطق إعادة المحاولة الذكي)
    # ------------------------------------------------------------------
    def embedding_text(self, text: Union[str, List[str]], decument_type: Optional[str] = None):
        if not self.client or not self.embedding_model_id:
            self.logger.error("Cohere client or Embedding Model ID not initialized.")
            return None

        is_single_input = isinstance(text, str)
        input_list = [text] if is_single_input else text
        
        input_type = cohereEnums.DOCUMENT.value 
        if decument_type == DecomentTypeEnums.QUERY.value:
            input_type = cohereEnums.QUERY.value

        processed_texts = [self.prosses_text(t) for t in input_list]

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # انتظار تأميني لضمان عدم تخطي 10 طلبات في الدقيقة
                time.sleep(3)

                response = self.client.embed(
                    model=self.embedding_model_id,
                    texts=processed_texts,
                    input_type=input_type,
                )

                if response and response.embeddings:
                    return response.embeddings[0] if is_single_input else response.embeddings
                
            except Exception as e:
                if "429" in str(e) or isinstance(e, TooManyRequestsError):
                    wait_time = (attempt + 1) * 12
                    self.logger.warning(f"Embedding Rate limit hit! Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                self.logger.error(f"Cohere API Error: {str(e)}")
                break
        return None

    # ------------------------------------------------------------------
    # Prompt helper
    # ------------------------------------------------------------------
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.prosses_text(prompt),
        }