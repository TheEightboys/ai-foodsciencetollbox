"""
LLM Client adapter for Discussion Questions module.
Now delegates to the centralised OpenRouter gateway via shared.llm_client.
"""

from ..shared.llm_client import (
    OpenRouterLLMClient,
    LLMClient,
    get_llm_client,
)

# Backward-compatible aliases
OpenAILLMClient = OpenRouterLLMClient
OpenAIServiceLLMClient = OpenRouterLLMClient
OpenRouterServiceLLMClient = OpenRouterLLMClient
