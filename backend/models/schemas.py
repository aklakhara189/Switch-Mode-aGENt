"""Pydantic schemas for request and response validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class BugReportCreate(BaseModel):
    title: str
    description: str
    reported_by: Optional[str] = "Developer"
    severity: Optional[str] = "high"
    switch_room_id: Optional[str] = None
    switch_message_id: Optional[str] = None

class InvestigationResponse(BaseModel):
    id: int
    bug_report_id: int
    root_cause: str
    affected_files: str
    affected_functions: str
    reasoning: str
    evidence: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TestResultResponse(BaseModel):
    id: int
    bug_report_id: int
    test_name: str
    test_code: str
    result: str
    output: str
    is_reproduction: bool
    is_patch_validation: bool
    executed_at: datetime

    class Config:
        from_attributes = True

class PatchProposalResponse(BaseModel):
    id: int
    bug_report_id: int
    file_path: str
    original_code: str
    diff_text: str
    description: str
    status: str
    patch_hash: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResolutionReportResponse(BaseModel):
    id: int
    bug_report_id: int
    summary: str
    root_cause: str
    fix_description: str
    tests_passed: int
    tests_failed: int
    approved_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BugReportResponse(BaseModel):
    id: int
    title: str
    description: str
    reported_by: str
    severity: str
    status: str
    switch_room_id: Optional[str] = None
    switch_message_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    investigation: Optional[InvestigationResponse] = None
    tests: List[TestResultResponse] = []
    patches: List[PatchProposalResponse] = []
    resolution_report: Optional[ResolutionReportResponse] = None

    class Config:
        from_attributes = True

class ReviewAction(BaseModel):
    reviewer_name: str = "Lead Engineer"
    reason: Optional[str] = None
    patch_hash: str
