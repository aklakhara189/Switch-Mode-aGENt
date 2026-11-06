"""Coordinates agent hand-offs and preserves their structured execution history."""

from __future__ import annotations

from typing import Any

from .agent_team import DebuggingAgent, IncidentManagerAgent, InvestigationContext
from .investigator import BugInvestigator
from .llm_client import LLMUnavailable, OpenAIResponsesClient


class AgentOrchestrator:
    """Runs local evidence collection before asking the provider for interpretation."""

    def __init__(self, llm: OpenAIResponsesClient | None = None, investigator: BugInvestigator | None = None) -> None:
        self.llm = llm or OpenAIResponsesClient()
        self.investigator = investigator or BugInvestigator()

    def investigate(self, bug_id: int, title: str, description: str) -> dict[str, Any]:
        context = InvestigationContext(bug_id=bug_id, title=title, description=description)
        local = self.investigator.investigate(title, description)
        context.source_evidence.append({
            "file": local["affected_files"],
            "functions": local["affected_functions"],
            "finding": local["root_cause"],
        })
        if local.get("evidence"):
            context.log_evidence.append({"evidence": local["evidence"]})
        context.record("log_analyzer", "completed", {"evidence": context.log_evidence})

        try:
            classification = IncidentManagerAgent(self.llm).classify(context)
            diagnosis = DebuggingAgent(self.llm).analyse(context)
        except LLMUnavailable as exc:
            context.record("orchestrator", "blocked", {"reason": str(exc)})
            return {
                "status": "blocked",
                "reason": str(exc),
                "local_evidence": local,
                "context": context.serialise(),
            }

        return {
            "status": "completed",
            "classification": classification,
            "diagnosis": diagnosis,
            "local_evidence": local,
            "context": context.serialise(),
        }
