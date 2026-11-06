"""Non-destructive readiness check for local Switch and LLM configuration."""

from __future__ import annotations

import sys
import httpx

from backend.config import settings


def check(name: str, value: bool, detail: str) -> bool:
    status = "PASS" if value else "BLOCKED"
    print(f"[{status}] {name}: {detail}")
    return value


def main() -> int:
    results = []
    results.append(check("OpenAI configuration", bool(settings.OPENAI_API_KEY), "API key present" if settings.OPENAI_API_KEY else "set OPENAI_API_KEY in .env"))
    results.append(check("Switch agent configuration", bool(settings.SWITCH_AGENT_ID and settings.SWITCH_AGENT_API_KEY), "agent ID/key present" if settings.SWITCH_AGENT_ID and settings.SWITCH_AGENT_API_KEY else "set SWITCH_AGENT_ID and SWITCH_AGENT_API_KEY"))
    if settings.SWITCH_API_URL:
        try:
            response = httpx.get(f"{settings.SWITCH_API_URL.rstrip('/')}/health", timeout=5.0)
            results.append(check("Switch bridge health", response.is_success, f"HTTP {response.status_code}"))
        except httpx.HTTPError as exc:
            results.append(check("Switch bridge health", False, str(exc)))
    else:
        results.append(check("Switch bridge health", False, "set SWITCH_API_URL"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
