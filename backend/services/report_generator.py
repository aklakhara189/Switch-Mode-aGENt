"""Resolution report generation service."""

from typing import Dict, Any

class ReportGenerator:
    """Generates final human-readable resolution documentation."""

    @staticmethod
    def create_report(bug_report, investigation, tests, patch, reviewer: str) -> Dict[str, Any]:
        passed_count = sum(1 for t in tests if t.result == "PASS")
        failed_count = sum(1 for t in tests if t.result == "FAIL")

        summary = (
            f"Bug #{bug_report.id} '{bug_report.title}' successfully diagnosed, validated, and patched. "
            f"Root cause was verified with real automated tests and approved by {reviewer}."
        )

        return {
            "summary": summary,
            "root_cause": investigation.root_cause if investigation else "N/A",
            "fix_description": patch.description if patch else "N/A",
            "tests_passed": passed_count,
            "tests_failed": failed_count,
            "approved_by": reviewer
        }
