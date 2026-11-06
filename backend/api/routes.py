"""FastAPI routes implementing the complete AI Bug Triage & Resolution workflow."""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.bug_report import BugReport, Investigation, TestResult, PatchProposal, ResolutionReport, WebhookEvent
from ..models.schemas import (
    BugReportCreate, BugReportResponse, InvestigationResponse,
    TestResultResponse, PatchProposalResponse, ResolutionReportResponse, ReviewAction
)
from ..services.investigator import BugInvestigator
from ..services.test_runner import TestRunner
from ..services.patch_manager import PatchManager
from ..services.switch_client import SwitchClient
from ..services.report_generator import ReportGenerator

router = APIRouter(prefix="/api", tags=["Bug Triage & Resolution"])
investigator = BugInvestigator()
switch_client = SwitchClient()

@router.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# 1. POST /api/bugs - Create new bug report
@router.post("/bugs", response_model=BugReportResponse)
def create_bug(payload: BugReportCreate, db: Session = Depends(get_db)):
    bug = BugReport(
        title=payload.title,
        description=payload.description,
        reported_by=payload.reported_by,
        severity=payload.severity,
        status="new",
        switch_room_id=payload.switch_room_id or "ai-bug-triage",
        switch_message_id=payload.switch_message_id
    )
    db.add(bug)
    db.commit()
    db.refresh(bug)

    # Broadcast to Switch collaboration room
    alert_msg = switch_client.format_bug_alert(bug.title, bug.severity, bug.id)
    switch_client.post_message(bug.switch_room_id, alert_msg)

    return bug

# 2. GET /api/bugs - List all bugs
@router.get("/bugs", response_model=List[BugReportResponse])
def list_bugs(db: Session = Depends(get_db)):
    return db.query(BugReport).order_by(BugReport.id.desc()).all()

# 3. GET /api/bugs/{id} - Get single bug
@router.get("/bugs/{id}", response_model=BugReportResponse)
def get_bug(id: int, db: Session = Depends(get_db)):
    bug = db.query(BugReport).filter(BugReport.id == id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
    return bug

# 4. POST /api/bugs/{id}/investigate - Trigger AI Investigation
@router.post("/bugs/{id}/investigate", response_model=InvestigationResponse)
def trigger_investigation(id: int, db: Session = Depends(get_db)):
    bug = db.query(BugReport).filter(BugReport.id == id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    bug.status = "investigating"
    db.commit()

    # Perform real AST / log analysis
    inv_data = investigator.investigate(bug.title, bug.description)

    # Save to database
    inv = Investigation(
        bug_report_id=bug.id,
        root_cause=inv_data["root_cause"],
        affected_files=inv_data["affected_files"],
        affected_functions=inv_data["affected_functions"],
        reasoning=inv_data["reasoning"],
        evidence=inv_data["evidence"]
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    # Post findings to Switch
    inv_msg = switch_client.format_investigation_result(inv_data, bug.id)
    switch_client.post_message(bug.switch_room_id, inv_msg)

    return inv

# 5. POST /api/bugs/{id}/test - Run reproduction test
@router.post("/bugs/{id}/test", response_model=TestResultResponse)
def run_reproduction_test(id: int, db: Session = Depends(get_db)):
    bug = db.query(BugReport).filter(BugReport.id == id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    file_target = bug.investigation.affected_files if bug.investigation else "demo/sample_app/calculator.py"
    func_target = bug.investigation.affected_functions if bug.investigation else "divide"
    test_code = investigator.generate_reproduction_test(file_target, func_target)

    # Run real test against original buggy code (must FAIL)
    res = TestRunner.execute_test(test_code, file_target)

    test_record = TestResult(
        bug_report_id=bug.id,
        test_name="Reproduction Test Suite",
        test_code=test_code,
        result=res["result"],
        output=res["output"],
        is_reproduction=True,
        is_patch_validation=False
    )
    db.add(test_record)
    db.commit()
    db.refresh(test_record)

    # Send evidence to Switch
    test_msg = switch_client.format_test_result(res["result"], res["output"], is_repro=True)
    switch_client.post_message(bug.switch_room_id, test_msg)

    return test_record

# 6. POST /api/bugs/{id}/patch - Propose AI Patch & validate
@router.post("/bugs/{id}/patch", response_model=PatchProposalResponse)
def create_patch(id: int, db: Session = Depends(get_db)):
    bug = db.query(BugReport).filter(BugReport.id == id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")

    file_target = bug.investigation.affected_files if bug.investigation else "demo/sample_app/calculator.py"
    orig, patched, diff, desc = investigator.generate_patch(file_target)

    patch = PatchProposal(
        bug_report_id=bug.id,
        file_path=file_target,
        original_code=orig,
        patched_code=patched,
        diff_text=diff,
        description=desc,
        status="proposed"
    )
    db.add(patch)
    bug.status = "patch_proposed"
    db.commit()
    db.refresh(patch)

    # Run automated validation test with temporary patch application (must PASS)
    if bug.tests:
        repro_test = bug.tests[0].test_code
        val_res = TestRunner.execute_test(repro_test, target_file=file_target, patched_code=patched)
        val_record = TestResult(
            bug_report_id=bug.id,
            test_name="Patch Pre-validation Test",
            test_code=repro_test,
            result=val_res["result"],
            output=val_res["output"],
            is_reproduction=False,
            is_patch_validation=True
        )
        db.add(val_record)
        db.commit()

        # Send test validation to Switch
        val_msg = switch_client.format_test_result(val_res["result"], val_res["output"], is_repro=False)
        switch_client.post_message(bug.switch_room_id, val_msg)

    # Post patch diff and request approval on Switch
    patch_msg = switch_client.format_patch_proposal(diff, patch.id)
    switch_client.post_message(bug.switch_room_id, patch_msg)

    return patch

# 7. POST /api/bugs/{id}/patches/{patch_id}/approve - Human approval
@router.post("/bugs/{id}/patches/{patch_id}/approve", response_model=PatchProposalResponse)
def approve_patch(id: int, patch_id: int, action: ReviewAction, db: Session = Depends(get_db)):
    patch = db.query(PatchProposal).filter(PatchProposal.id == patch_id, PatchProposal.bug_report_id == id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch proposal not found")
    if action.patch_hash != patch.patch_hash:
        raise HTTPException(status_code=409, detail="Approval does not match this exact patch version")

    patch.status = "approved"
    patch.reviewed_by = action.reviewer_name
    patch.reviewed_at = datetime.utcnow()
    patch.approved_patch_hash = action.patch_hash
    patch.bug_report.status = "approved"
    db.commit()
    db.refresh(patch)

    switch_client.post_message(
        patch.bug_report.switch_room_id,
        f"✅ **[PATCH APPROVED]** Patch #{patch.id} approved by @{action.reviewer_name}. Ready for deployment!"
    )
    return patch

# 8. POST /api/bugs/{id}/patches/{patch_id}/reject - Human rejection
@router.post("/bugs/{id}/patches/{patch_id}/reject", response_model=PatchProposalResponse)
def reject_patch(id: int, patch_id: int, action: ReviewAction, db: Session = Depends(get_db)):
    patch = db.query(PatchProposal).filter(PatchProposal.id == patch_id, PatchProposal.bug_report_id == id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch proposal not found")

    patch.status = "rejected"
    patch.reviewed_by = action.reviewer_name
    patch.reviewed_at = datetime.utcnow()
    patch.bug_report.status = "rejected"
    db.commit()
    db.refresh(patch)

    switch_client.post_message(
        patch.bug_report.switch_room_id,
        f"❌ **[PATCH REJECTED]** Patch #{patch.id} rejected by @{action.reviewer_name}. Reason: {action.reason or 'Not specified'}."
    )
    return patch

# 9. POST /api/bugs/{id}/patches/{patch_id}/apply - Apply patch safely
@router.post("/bugs/{id}/patches/{patch_id}/apply")
def apply_patch_endpoint(id: int, patch_id: int, db: Session = Depends(get_db)):
    patch = db.query(PatchProposal).filter(PatchProposal.id == patch_id, PatchProposal.bug_report_id == id).first()
    if not patch:
        raise HTTPException(status_code=404, detail="Patch proposal not found")

    # Enforce human approval security rule
    if patch.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Security violation: Patch has not been approved! Current status is '{patch.status}'."
        )
    if patch.approved_patch_hash != patch.patch_hash:
        raise HTTPException(status_code=409, detail="Approved patch content has changed; fresh human approval is required.")

    PatchManager.apply_patch(patch.file_path, patch.patched_code, patch.status)
    patch.status = "applied"
    patch.bug_report.status = "resolved"
    db.commit()

    # Generate final resolution report
    report_dict = ReportGenerator.create_report(
        patch.bug_report,
        patch.bug_report.investigation,
        patch.bug_report.tests,
        patch,
        patch.reviewed_by or "Lead Engineer"
    )
    rep = ResolutionReport(
        bug_report_id=patch.bug_report.id,
        summary=report_dict["summary"],
        root_cause=report_dict["root_cause"],
        fix_description=report_dict["fix_description"],
        tests_passed=report_dict["tests_passed"],
        tests_failed=report_dict["tests_failed"],
        approved_by=report_dict["approved_by"]
    )
    db.add(rep)
    db.commit()

    # Broadcast final resolution to Switch
    res_msg = switch_client.format_resolution(patch.bug_report.id, patch.reviewed_by or "Lead Engineer")
    switch_client.post_message(patch.bug_report.switch_room_id, res_msg)

    return {"status": "applied", "message": "Patch successfully applied to source file.", "report": report_dict}

# 10. GET /api/bugs/{id}/report - Get final resolution report
@router.get("/bugs/{id}/report", response_model=ResolutionReportResponse)
def get_resolution_report(id: int, db: Session = Depends(get_db)):
    report = db.query(ResolutionReport).filter(ResolutionReport.bug_report_id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Resolution report not found for this bug.")
    return report

# 11. POST /api/webhook/switch - Handle incoming webhooks from Switch / Mattermost
@router.post("/webhook/switch")
def switch_webhook(payload: dict, db: Session = Depends(get_db)):
    event_id = str(payload.get("event_id") or payload.get("id") or "")
    if event_id:
        if db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first():
            return {"status": "ignored", "reason": "duplicate event"}
        db.add(WebhookEvent(event_id=event_id, source="switch"))
        db.commit()
    text = payload.get("text", "") or payload.get("message", "")
    user = payload.get("user_name", "Team Member")
    channel_id = payload.get("channel_id", "ai-bug-triage")

    if not text:
        return {"status": "ignored", "reason": "empty message"}

    # Automatic creation of bug report when user posts "!bug" or description in Switch room
    if text.startswith("!bug") or "bug:" in text.lower():
        title = text.replace("!bug", "").strip() or "Reported defect via Switch"
        bug = BugReport(
            title=title,
            description=text,
            reported_by=user,
            severity="high",
            status="new",
            switch_room_id=channel_id
        )
        db.add(bug)
        db.commit()
        db.refresh(bug)

        switch_client.post_message(
            channel_id,
            f"🤖 AI Investigator acknowledged bug #{bug.id}: '{title}'. Beginning triage..."
        )
        return {"status": "created", "bug_id": bug.id}

    return {"status": "received"}
