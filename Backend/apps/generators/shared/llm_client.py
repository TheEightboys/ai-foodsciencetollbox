"""
Shared LLM Client Interface — backed by the OpenRouter gateway.

Canonical class: ``OpenRouterLLMClient``
Backward-compatible aliases:
    OpenAILLMClient            = OpenRouterLLMClient
    GeminiLLMClient            = OpenRouterLLMClient
    OpenRouterServiceLLMClient = OpenRouterLLMClient
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""
        pass


class OpenRouterLLMClient(LLMClient):
    """
    Canonical LLM client — delegates every call to the centralised
    OpenRouter gateway (``apps.generators.openrouter_gateway``).
    """

    def __init__(self, generator_type: str = "_default", user_id=None, **_kwargs):
        """
        Parameters
        ----------
        generator_type : str
            Used for per-generator max_tokens / temperature routing.
        user_id : int | str | None
            Passed to the gateway for per-user rate limiting.
        """
        self.generator_type = generator_type
        self.user_id = user_id

    def generate_text(self, prompt: str, system_message: str = "", use_cache: bool = True) -> str:
        """Generate text via the OpenRouter gateway."""
        from apps.generators.openrouter_gateway import generate_ai_content

        return generate_ai_content(
            generator_type=self.generator_type,
            prompt=prompt,
            system_message=system_message,
            user_id=self.user_id,
            use_cache=use_cache,
        )


# ------------------------------------------------------------------
# Backward-compatible aliases
# ------------------------------------------------------------------
OpenAILLMClient = OpenRouterLLMClient
GeminiLLMClient = OpenRouterLLMClient
OpenRouterServiceLLMClient = OpenRouterLLMClient


def get_llm_client(generator_type: str = "_default", user_id=None) -> OpenRouterLLMClient:
    """Factory — returns a configured OpenRouterLLMClient."""
    return OpenRouterLLMClient(generator_type=generator_type, user_id=user_id)
