"""Database models for Bug Triage and Resolution workflow."""

from datetime import datetime
import hashlib
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reported_by = Column(String(100), default="Developer")
    severity = Column(String(50), default="high")
    status = Column(String(50), default="new")  # new, investigating, patch_proposed, approved, rejected, resolved
    switch_room_id = Column(String(255), nullable=True)
    switch_message_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    investigation = relationship("Investigation", back_populates="bug_report", uselist=False, cascade="all, delete-orphan")
    tests = relationship("TestResult", back_populates="bug_report", cascade="all, delete-orphan")
    patches = relationship("PatchProposal", back_populates="bug_report", cascade="all, delete-orphan")
    resolution_report = relationship("ResolutionReport", back_populates="bug_report", uselist=False, cascade="all, delete-orphan")


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"), nullable=False)
    root_cause = Column(Text, nullable=False)
    affected_files = Column(Text, nullable=False)  # JSON or comma-separated
    affected_functions = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bug_report = relationship("BugReport", back_populates="investigation")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"), nullable=False)
    test_name = Column(String(255), nullable=False)
    test_code = Column(Text, nullable=False)
    result = Column(String(50), nullable=False)  # PASS or FAIL
    output = Column(Text, nullable=False)
    is_reproduction = Column(Boolean, default=False)
    is_patch_validation = Column(Boolean, default=False)
    executed_at = Column(DateTime, default=datetime.utcnow)

    bug_report = relationship("BugReport", back_populates="tests")


class PatchProposal(Base):
    __tablename__ = "patch_proposals"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    original_code = Column(Text, nullable=False)
    patched_code = Column(Text, nullable=False)
    diff_text = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="proposed")  # proposed, approved, rejected, applied
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_patch_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bug_report = relationship("BugReport", back_populates="patches")

    @property
    def patch_hash(self) -> str:
        return hashlib.sha256(self.patched_code.encode("utf-8")).hexdigest()


class ResolutionReport(Base):
    __tablename__ = "resolution_reports"

    id = Column(Integer, primary_key=True, index=True)
    bug_report_id = Column(Integer, ForeignKey("bug_reports.id"), nullable=False)
    summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    fix_description = Column(Text, nullable=False)
    tests_passed = Column(Integer, default=0)
    tests_failed = Column(Integer, default=0)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bug_report = relationship("BugReport", back_populates="resolution_report")


class WebhookEvent(Base):
    """Idempotency record for real inbound collaboration events."""
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    source = Column(String(50), nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
