import pytest
from backend.api.routes import health
from backend.services.investigator import BugInvestigator
from backend.services.patch_manager import PatchManager
from backend.services.test_runner import TestRunner

def test_health_endpoint_contract():
    assert health()["status"] == "ok"

def test_investigator_finds_source_evidence():
    report = BugInvestigator().investigate("Division precision", "divide returns 3")
    assert "calculator.py" in report["affected_files"] and "//" in report["root_cause"]

def test_reproduction_fails_then_patch_passes_in_isolation():
    investigator = BugInvestigator()
    original, patched, _, _ = investigator.generate_patch("demo/sample_app/calculator.py")
    code = investigator.generate_reproduction_test("demo/sample_app/calculator.py", "divide")
    assert TestRunner.execute_test(code, "demo/sample_app/calculator.py")["result"] == "FAIL"
    assert TestRunner.execute_test(code, "demo/sample_app/calculator.py", patched)["result"] == "PASS"
    assert "return a // b" in original

def test_patch_manager_blocks_unapproved_and_unsafe_paths():
    with pytest.raises(ValueError): PatchManager.apply_patch("demo/sample_app/calculator.py", "x", "proposed")
    with pytest.raises(ValueError): PatchManager.resolve_target("../README.md")
