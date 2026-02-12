"""
OpenRouter AI Gateway — centralised LLM call layer.

Every generator in the project calls `generate_ai_content()` which:
1. Checks per-user sliding-window rate limit (cache-backed).
2. Checks the response cache (SHA-256 keyed).
3. Walks the FREE model fallback chain with per-model retry.
4. If all free models fail, falls back to direct OpenAI API (if configured).
5. Enforces circuit-breaker, bulkhead, and timeout resilience.
6. Returns the generated text (and caches it on success).

Environment variables consumed
------------------------------
OPENROUTER_API_KEY          – Bearer token for OpenRouter
OPENAI_API_KEY              – Bearer token for OpenAI (fallback)
OPENAI_MODEL                – OpenAI model name (default gpt-4o-mini)
LLM_RATE_LIMIT_PER_MINUTE  – per-user cap (default 10)
SITE_URL                    – sent as HTTP-Referer (default http://localhost:8080)
"""

import hashlib
import json
import logging
import random
import threading
import time
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model fallback chain (all FREE)
# ---------------------------------------------------------------------------
FREE_MODEL_CHAIN = [
    "google/gemma-3-12b-it:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "qwen/qwen3-4b:free",
    "google/gemma-3-4b-it:free",
]

# ---------------------------------------------------------------------------
# Per-generator routing (max_tokens / temperature)
# ---------------------------------------------------------------------------
GENERATOR_PARAMS = {
    "learning_objectives": {"max_tokens": 2000, "temperature": 0.7},
    "key_terms":           {"max_tokens": 1200, "temperature": 0.5},
    "discussion_questions": {"max_tokens": 2500, "temperature": 0.7},
    "lesson_starter":      {"max_tokens": 2000, "temperature": 0.7},
    "quiz":                {"max_tokens": 2000, "temperature": 0.7},
    "lesson_plan":         {"max_tokens": 3000, "temperature": 0.7},
    "bell_ringer":         {"max_tokens": 1500, "temperature": 0.7},
    "_default":            {"max_tokens": 1500, "temperature": 0.7},
}

# ---------------------------------------------------------------------------
# Resilience helpers
# ---------------------------------------------------------------------------

class _CircuitBreaker:
    """Simple circuit breaker: 5 failures → open for 60 s."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self._lock = threading.Lock()
        self._failure_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._last_failure_time: Optional[float] = None
        self._state = "closed"  # closed | open | half-open

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == "open":
                if (time.time() - (self._last_failure_time or 0)) >= self._recovery_timeout:
                    self._state = "half-open"
            return self._state

    def record_success(self):
        with self._lock:
            self._failure_count = 0
            self._state = "closed"

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self._failure_threshold:
                self._state = "open"
                logger.warning("Circuit breaker OPEN — too many failures")

    def allow_request(self) -> bool:
        s = self.state
        return s in ("closed", "half-open")


class _Bulkhead:
    """Semaphore-based concurrency limiter: max 10 concurrent calls."""

    def __init__(self, max_concurrent: int = 10, acquire_timeout: float = 5.0):
        self._sem = threading.Semaphore(max_concurrent)
        self._acquire_timeout = acquire_timeout

    def acquire(self) -> bool:
        return self._sem.acquire(timeout=self._acquire_timeout)

    def release(self):
        self._sem.release()


_circuit = _CircuitBreaker(failure_threshold=5, recovery_timeout=60)
_bulkhead = _Bulkhead(max_concurrent=10, acquire_timeout=5.0)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_cache(alias: str):
    """Return the Django cache backend (falls back to 'default')."""
    try:
        return caches[alias]
    except Exception:
        return caches["default"]


def _cache_key(generator_type: str, prompt: str) -> str:
    """Build deterministic cache key for a generation request."""
    digest = hashlib.sha256(f"{generator_type}:{prompt}".encode()).hexdigest()[:24]
    return f"openrouter:{generator_type}:{digest}"


def _per_user_rate_ok(user_id) -> bool:
    """Sliding-window per-user rate limit using cache (DB 1 / default)."""
    cache = _get_cache("default")
    limit = getattr(settings, "LLM_RATE_LIMIT_PER_MINUTE", 30)
    key = f"ratelimit:ai:{user_id}"
    current = cache.get(key, 0)
    if current >= limit:
        return False
    # Increment with 60-second window
    try:
        cache.set(key, current + 1, 60)
    except Exception:
        pass
    return True


def _backoff(attempt: int, is_rate_limit: bool = False) -> float:
    """Exponential backoff with jitter. Uses longer waits for 429 rate limits."""
    if is_rate_limit:
        base = 12  # 12-24s for rate limits
    else:
        base = 3
    return base * (attempt + 1) * random.uniform(0.5, 1.0)


_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_NON_RETRYABLE_STATUS = {402}  # payment required → skip model immediately


def _call_openrouter(model: str, messages: list, max_tokens: int,
                     temperature: float, timeout: float = 60.0) -> dict:
    """Single HTTP POST to OpenRouter. Returns parsed JSON or raises."""
    api_key = getattr(settings, "OPENROUTER_API_KEY", "")
    site_url = getattr(settings, "SITE_URL", "http://localhost:8080")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": site_url,
        "X-Title": "Food Science Toolbox",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()


def _extract_text(data: dict) -> str:
    """Pull assistant text from OpenRouter/OpenAI response; raise on empty."""
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        text = ""
    if not text or not text.strip():
        raise ValueError("Empty response from model")
    return text.strip()


# ---------------------------------------------------------------------------
# OpenAI direct fallback
# ---------------------------------------------------------------------------

# Map generator types to OpenAI model (use gpt-4o-mini for cost efficiency)
OPENAI_MODEL_MAP = {
    "lesson_plan":   "gpt-4o-mini",
    "_default":      "gpt-4o-mini",
}


def _call_openai(messages: list, max_tokens: int, temperature: float,
                 timeout: float = 90.0) -> str:
    """
    Direct call to OpenAI API. Used as fallback when OpenRouter is exhausted.
    Returns the generated text or raises on failure.
    """
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OpenAI API key not configured")

    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return _extract_text(data)


# ---------------------------------------------------------------------------
# Public gateway
# ---------------------------------------------------------------------------

def generate_ai_content(
    generator_type: str,
    prompt: str,
    system_message: str = "",
    user_id=None,
    use_cache: bool = True,
) -> str:
    """
    Centralised LLM gateway.

    Priority order:
      1. OpenAI direct (if OPENAI_API_KEY configured) — fast, reliable
      2. OpenRouter free model chain — fallback if OpenAI fails or is absent

    Parameters
    ----------
    generator_type : str
        One of the keys in GENERATOR_PARAMS (e.g. "lesson_starter").
    prompt : str
        The user/teacher prompt text.
    system_message : str, optional
        A system-level instruction prepended into the user message.
    user_id : int | str | None
        Used for per-user rate limiting.
    use_cache : bool
        Set False to bypass the response cache.

    Returns
    -------
    str  – The generated text.

    Raises
    ------
    RuntimeError  – If all providers fail.
    PermissionError – If per-user rate limit exceeded.
    """

    # ------ per-user rate limit ------
    if user_id is not None and not _per_user_rate_ok(user_id):
        raise PermissionError(
            "You have exceeded the AI generation rate limit. Please wait a moment and try again."
        )

    # ------ resolve generator params ------
    params = GENERATOR_PARAMS.get(generator_type, GENERATOR_PARAMS["_default"])
    max_tokens = params["max_tokens"]
    temperature = params["temperature"]

    # ------ build message ------
    if system_message:
        content = f"{system_message}\n\n{prompt}"
    else:
        content = prompt
    messages = [{"role": "user", "content": content}]

    # ------ cache check ------
    llm_cache = _get_cache("llm_cache")
    c_key = _cache_key(generator_type, content)
    if use_cache:
        cached = llm_cache.get(c_key)
        if cached:
            logger.info("Cache HIT for %s (key=%s)", generator_type, c_key)
            return cached

    openai_key = getattr(settings, "OPENAI_API_KEY", "")

    # ======================================================================
    # PRIORITY 1: OpenAI direct (fast, reliable, unlimited)
    # ======================================================================
    if openai_key:
        try:
            text = _call_openai(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if use_cache:
                llm_cache.set(c_key, text, 3600)
            logger.info("OpenAI OK: gen=%s", generator_type)
            return text
        except Exception as openai_exc:
            logger.warning(
                "OpenAI failed, falling back to OpenRouter: %s", openai_exc,
            )
            # Fall through to OpenRouter

    # ======================================================================
    # PRIORITY 2: OpenRouter free model chain (fallback)
    # ======================================================================
    if not _circuit.allow_request():
        raise RuntimeError(
            "AI service is temporarily unavailable (circuit breaker open). "
            "Please try again in a minute."
        )

    if not _bulkhead.acquire():
        raise RuntimeError(
            "Too many concurrent AI requests. Please try again shortly."
        )

    last_exc: Optional[Exception] = None
    try:
        for model in FREE_MODEL_CHAIN:
            try:
                data = _call_openrouter(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=30.0,
                )
                text = _extract_text(data)

                _circuit.record_success()
                if use_cache:
                    llm_cache.set(c_key, text, 3600)
                logger.info(
                    "OpenRouter OK: model=%s gen=%s", model, generator_type,
                )
                return text

            except requests.HTTPError as exc:
                status_code = exc.response.status_code if exc.response is not None else 0
                logger.warning(
                    "OpenRouter HTTP %s model=%s", status_code, model,
                )
                last_exc = exc
                # 429/402 → skip to next model immediately
                continue

            except (requests.ConnectionError, requests.Timeout) as exc:
                logger.warning(
                    "OpenRouter net error model=%s: %s", model, exc,
                )
                last_exc = exc
                continue

            except Exception as exc:
                logger.warning(
                    "OpenRouter error model=%s: %s", model, exc,
                )
                last_exc = exc
                continue

        # All OpenRouter models exhausted
        _circuit.record_failure()
        raise RuntimeError(
            "All AI models failed to generate content. Please try again later."
        ) from last_exc

    finally:
        _bulkhead.release()
