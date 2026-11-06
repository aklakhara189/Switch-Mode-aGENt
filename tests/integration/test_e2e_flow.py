"""End-to-end workflow verification using production route functions and SQLite."""
import pytest
from fastapi import HTTPException
from backend.api.routes import create_bug, trigger_investigation, run_reproduction_test, create_patch, approve_patch, reject_patch, apply_patch_endpoint, get_resolution_report, switch_webhook
from backend.database import SessionLocal
from backend.models.schemas import BugReportCreate, ReviewAction
from backend.services.patch_manager import PatchManager

def test_full_e2e_bug_triage_flow():
    db = SessionLocal()
    try:
        bug = create_bug(BugReportCreate(title="Division precision error", description="divide(10, 3) returns 3", reported_by="qa", severity="high"), db)
        assert "//" in trigger_investigation(bug.id, db).root_cause
        assert run_reproduction_test(bug.id, db).result == "FAIL"
        patch = create_patch(bug.id, db)
        with pytest.raises(HTTPException):
            apply_patch_endpoint(bug.id, patch.id, db)
        approve_patch(bug.id, patch.id, ReviewAction(reviewer_name="SeniorDev", reason="Verified", patch_hash=patch.patch_hash), db)
        assert apply_patch_endpoint(bug.id, patch.id, db)["status"] == "applied"
        assert get_resolution_report(bug.id, db).approved_by == "SeniorDev"
        PatchManager.rollback(patch.file_path, patch.original_code)
    finally:
        db.close()

def test_rejection_stale_approval_and_duplicate_event_are_blocked():
    db = SessionLocal()
    try:
        bug = create_bug(BugReportCreate(title="Inventory total wrong", description="inventory value only includes final item", reported_by="qa"), db)
        trigger_investigation(bug.id, db)
        run_reproduction_test(bug.id, db)
        patch = create_patch(bug.id, db)
        with pytest.raises(HTTPException) as mismatch:
            approve_patch(bug.id, patch.id, ReviewAction(reviewer_name="SeniorDev", patch_hash="0" * 64), db)
        assert mismatch.value.status_code == 409
        rejected = reject_patch(bug.id, patch.id, ReviewAction(reviewer_name="SeniorDev", reason="Needs more review", patch_hash=patch.patch_hash), db)
        assert rejected.status == "rejected"
        with pytest.raises(HTTPException):
            apply_patch_endpoint(bug.id, patch.id, db)
        event = {"event_id": f"dedupe-test-inventory-{bug.id}", "text": "!bug duplicate safe", "user_name": "qa", "channel_id": "room"}
        assert switch_webhook(event, db)["status"] == "created"
        assert switch_webhook(event, db)["reason"] == "duplicate event"
    finally:
        db.close()
