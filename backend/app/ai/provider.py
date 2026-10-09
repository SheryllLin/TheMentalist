"""
LLMProvider abstraction.
Supports: openai | anthropic | mock

Adding a new provider: subclass LLMProvider and implement `complete()`.
Switch provider via the LLM_PROVIDER environment variable.
"""
import json
import logging
from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMProvider(ABC):

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """Return the assistant's text response."""
        ...

    async def complete_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Calls complete() and parses the result as JSON.
        Handles markdown code blocks that some models wrap responses in.
        """
        raw = await self.complete(system_prompt, user_message, temperature, max_tokens)
        # Strip markdown code fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last fence lines
            lines = lines[1:] if lines[0].startswith("```") else lines
            lines = lines[:-1] if lines[-1].strip() == "```" else lines
            text = "\n".join(lines)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}. Raw response: {raw[:200]}")
            raise ValueError(f"LLM did not return valid JSON: {e}") from e


class OpenAIProvider(LLMProvider):

    def __init__(self):
        import openai
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model or "gpt-4o-mini"

    async def complete(self, system_prompt, user_message, temperature=0.1, max_tokens=4096):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class AnthropicProvider(LLMProvider):

    def __init__(self):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model or "claude-3-haiku-20240307"

    async def complete(self, system_prompt, user_message, temperature=0.1, max_tokens=4096):
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.content[0].text


class MockLLMProvider(LLMProvider):
    """
    Mock provider for development/testing when no API key is configured.
    Always returns valid JSON for extraction calls so the pipeline completes.
    For investigation queries, returns a helpful placeholder message.
    """

    async def complete(self, system_prompt, user_message, temperature=0.1, max_tokens=4096):
        sp = system_prompt.lower()
        # Return valid extraction JSON for any extraction/entity call
        if any(kw in sp for kw in ("extract", "entities", "relationship", "criminal", "investigation analyst")):
            return json.dumps({
                "entities": [],
                "relationships": [],
                "events": []
            })
        # Investigation assistant: return a readable placeholder
        return (
            "Mock LLM active — no real AI extraction. "
            "Set LLM_PROVIDER=openai and OPENAI_API_KEY in .env for live extraction. "
            "Structured data (CSV/CDR/transactions) is processed deterministically regardless."
        )


def get_llm_provider() -> LLMProvider:
    provider = settings.llm_provider
    if provider == "openai":
        if not settings.openai_api_key:
            logger.warning("LLM_PROVIDER=openai but OPENAI_API_KEY is not set. Falling back to mock.")
            return MockLLMProvider()
        return OpenAIProvider()
    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            logger.warning("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY not set. Falling back to mock.")
            return MockLLMProvider()
        return AnthropicProvider()
    elif provider == "mock":
        return MockLLMProvider()
    else:
        logger.warning(f"Unknown LLM_PROVIDER '{provider}'. Using mock.")
        return MockLLMProvider()
