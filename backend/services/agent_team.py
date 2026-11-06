"""Structured specialist agents for a human-controlled bug-resolution workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .llm_client import OpenAIResponsesClient


@dataclass
class AgentRecord:
    role: str
    status: str
    output: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class InvestigationContext:
    bug_id: int
    title: str
    description: str
    source_evidence: list[dict[str, Any]] = field(default_factory=list)
    log_evidence: list[dict[str, Any]] = field(default_factory=list)
    history: list[AgentRecord] = field(default_factory=list)

    def record(self, role: str, status: str, output: dict[str, Any]) -> None:
        self.history.append(AgentRecord(role=role, status=status, output=output))

    def serialise(self) -> dict[str, Any]:
        return {
            "bug_id": self.bug_id,
            "title": self.title,
            "description": self.description,
            "source_evidence": self.source_evidence,
            "log_evidence": self.log_evidence,
            "history": [asdict(item) for item in self.history],
        }


class IncidentManagerAgent:
    def __init__(self, llm: OpenAIResponsesClient) -> None:
        self.llm = llm

    def classify(self, context: InvestigationContext) -> dict[str, Any]:
        result = self.llm.structured(
            "You are the incident manager. Classify a software bug. Return keys severity "
            "(low|medium|high|critical), priority (P0-P3), summary, and investigation_focus.",
            f"Title: {context.title}\nDescription: {context.description}",
        )
        context.record("incident_manager", "completed", result)
        return result


class DebuggingAgent:
    def __init__(self, llm: OpenAIResponsesClient) -> None:
        self.llm = llm

    def analyse(self, context: InvestigationContext) -> dict[str, Any]:
        result = self.llm.structured(
            "You are a debugging agent. Use only supplied evidence. Return keys root_cause, "
            "affected_files, affected_functions, explanation, confidence (0-1), and evidence_refs.",
            str(context.serialise()),
        )
        context.record("debugging", "completed", result)
        return result


class CodeFixAgent:
    def __init__(self, llm: OpenAIResponsesClient) -> None:
        self.llm = llm

    def propose(self, context: InvestigationContext) -> dict[str, Any]:
        result = self.llm.structured(
            "You are a code-fix agent. Propose a minimal unified diff only for files supplied "
            "in evidence. Return keys description, file_path, unified_diff, and risks. Never apply changes.",
            str(context.serialise()),
        )
        context.record("code_fix", "completed", result)
        return result


class ReviewerAgent:
    def __init__(self, llm: OpenAIResponsesClient) -> None:
        self.llm = llm

    def review(self, context: InvestigationContext, patch: dict[str, Any], tests: dict[str, Any]) -> dict[str, Any]:
        result = self.llm.structured(
            "You are a security reviewer. Review the supplied patch and test evidence. Return "
            "keys recommendation (approve|reject), findings, required_changes, and rationale. "
            "Your recommendation is advisory and can never apply a patch.",
            str({"context": context.serialise(), "patch": patch, "tests": tests}),
        )
        context.record("reviewer", "completed", result)
        return result
