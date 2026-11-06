"""Patch Manager service.
Handles diff generation, safe backup creation, and applying approved patches.
"""

import os
import shutil
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_PATCH_ROOT = (PROJECT_ROOT / "demo" / "sample_app").resolve()

class PatchManager:
    """Manages patch lifecycle with strict human-approval enforcement."""

    @staticmethod
    def resolve_target(file_path: str) -> Path:
        """Accept only existing Python source beneath the demo application root."""
        candidate = (PROJECT_ROOT / file_path).resolve()
        if candidate.suffix != ".py" or not candidate.is_relative_to(ALLOWED_PATCH_ROOT):
            raise ValueError("Patch path is not an allowed application source file")
        if not candidate.is_file():
            raise FileNotFoundError(f"Target file {file_path} not found.")
        return candidate

    @staticmethod
    def apply_patch(file_path: str, patched_code: str, status: str) -> str:
        """Applies patch ONLY if approved."""
        if status != "approved":
            raise ValueError(f"Cannot apply patch with status '{status}'. Explicit human approval is required!")

        abs_path = PatchManager.resolve_target(file_path)

        # Create timestamped backup
        backup_path = f"{abs_path}.backup_{int(time.time())}"
        shutil.copy2(abs_path, backup_path)

        # Write patched code
        abs_path.write_text(patched_code, encoding="utf-8")

        return backup_path

    @staticmethod
    def rollback(file_path: str, original_code: str) -> bool:
        """Rolls back a file to its original code."""
        abs_path = PatchManager.resolve_target(file_path)
        abs_path.write_text(original_code, encoding="utf-8")
        return True
