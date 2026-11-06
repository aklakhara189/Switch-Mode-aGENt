"""Small, provider-backed LLM client used by the agent team.

The application never manufactures an LLM answer: callers get a typed error when
the provider is not configured or when its request fails.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from ..config import settings


class LLMUnavailable(RuntimeError):
    """Raised when a genuine provider answer cannot be obtained safely."""


class OpenAIResponsesClient:
    """Minimal client for the official OpenAI Responses HTTP API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.model)

    def structured(self, instructions: str, input_text: str) -> dict[str, Any]:
        """Request a JSON object and reject malformed provider responses."""
        if not self.configured:
            raise LLMUnavailable("OpenAI is not configured. Set OPENAI_API_KEY before running AI agents.")

        try:
            response = httpx.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "instructions": instructions + " Return one valid JSON object and no markdown.",
                    "input": input_text,
                    "temperature": 0,
                    "max_output_tokens": 1400,
                },
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
            response.raise_for_status()
            body = response.json()
            output = body.get("output_text", "").strip()
            parsed = json.loads(output)
            if not isinstance(parsed, dict):
                raise ValueError("Expected an object")
            return parsed
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError) as exc:
            raise LLMUnavailable(f"LLM request failed: {exc}") from exc
