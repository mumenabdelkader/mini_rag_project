from enum import Enum
class LLMEnums( Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    COHERE = "COHERE"
    AI21 = "ai21"
    GOOGLE_PALM = "google_palm"
    LLM_PROVIDER_X = "llm_provider_x"  # Placeholder for future providers

class openAIenums( Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    system = "system"
    SYSTEM = "system"
    assistant = "assistant"
    ASSISTANT = "assistant"
    user = "user"
    USER = "user"

class cohereEnums( Enum):
    DOCUMENT = "search_document"
    QUERY = "search_query"
    system = "SYSTEM"
    SYSTEM = "SYSTEM"
    assistant = "CHATBOT"
    ASSISTANT = "CHATBOT"
    user = "USER"
    USER = "USER"
class DecomentTypeEnums( Enum):
    DOCUMENT = "document"
    QUERY = "query"