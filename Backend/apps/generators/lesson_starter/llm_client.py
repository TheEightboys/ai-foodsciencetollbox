"""
LLM Client for Lesson Starter module.
Now delegates to the centralised OpenRouter gateway via shared.llm_client.
"""

from ..shared.llm_client import (
    OpenRouterLLMClient,
    LLMClient,
    get_llm_client,
)

# Backward-compatible alias — callers that do
#   from .llm_client import OpenAILLMClient
# will now get the OpenRouter-backed client automatically.
OpenAILLMClient = OpenRouterLLMClient
OpenAIServiceLLMClient = OpenRouterLLMClient
