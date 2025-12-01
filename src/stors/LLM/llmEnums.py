from enum import Enum
class LLMEnums( Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    AI21 = "ai21"
    GOOGLE_PALM = "google_palm"
    LLM_PROVIDER_X = "llm_provider_x"  # Placeholder for future providers

class openAIenums( Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    system = "system"
    assistant = "assistant" 
    user = "user"