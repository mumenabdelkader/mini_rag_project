from ..LLMinterface import LLMInterface
from ..llmEnums import cohereEnums, DecomentTypeEnums
import cohere
import logging
from typing import List, Optional


class CohereProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        defaulet_input_max_characters: int = 1000,
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
    # Text generation
    # ------------------------------------------------------------------
    def generate_text(
        self,
        prompt: str,
        max_output_tokens: Optional[int] = None,
        chat_history: Optional[List[dict]] = None,
        temperature: Optional[float] = None,
    ):
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None

        if chat_history is None:
            chat_history = []

        max_output_tokens = (
            max_output_tokens
            if max_output_tokens
            else self.defaulet_output_token_limit
        )
        temperature = temperature if temperature else self.defaulet_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.prosses_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        if not response or not getattr(response, "text", None):
            self.logger.error("Failed to get response from Cohere.")
            return None

        return response.text

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    def embedding_text(self, text: str, decument_type: Optional[str] = None):
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None

        # ✅ default for indexing
        input_type = cohereEnums.DOCUMENT.value  # "search_document"

        # ✅ query embeddings
        if decument_type == DecomentTypeEnums.QUERY.value:
            input_type = cohereEnums.QUERY.value  # "search_query"

        self.logger.info(
            f"Embedding | model={self.embedding_model_id} | input_type={input_type}"
        )

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.prosses_text(text)],
            input_type=input_type,
        )

        if not response or not response.embeddings:
            self.logger.error("Failed to get embedding from Cohere.")
            return None

        # Cohere SDK (latest): embeddings = List[List[float]]
        return response.embeddings[0]

    # ------------------------------------------------------------------
    # Prompt helper
    # ------------------------------------------------------------------
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.prosses_text(prompt),
        }
