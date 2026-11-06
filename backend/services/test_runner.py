"""Test Runner service that runs real pytest subprocess executions."""

import subprocess
import tempfile
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any

class TestRunner:
    """Executes pytest tests in a clean subprocess and captures PASS/FAIL evidence."""

    @staticmethod
    def execute_test(test_code: str, target_file: str = None, patched_code: str = None) -> Dict[str, Any]:
        """Runs the given test code, optionally applying a patch temporarily."""
        try:
            project_root = Path(__file__).resolve().parents[2]
            # Windows sandboxed Python subprocesses cannot always access the system
            # temporary directory, so keep disposable workspaces inside the project.
            sandbox_root = project_root / ".tmp"
            sandbox_root.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="bugtriage-validation-", dir=sandbox_root) as temp_dir:
                workspace = Path(temp_dir)
                # Copy only the application under investigation. Validation never writes
                # into the user's original source tree.
                shutil.copytree(project_root / "demo", workspace / "demo")
                if target_file and patched_code is not None:
                    relative_target = Path(target_file)
                    if relative_target.is_absolute() or ".." in relative_target.parts:
                        raise ValueError("Invalid test target path")
                    target = workspace / relative_target
                    if not target.is_file():
                        raise FileNotFoundError(f"Target file {target_file} not found in isolated workspace")
                    target.write_text(patched_code, encoding="utf-8")

                test_file_path = workspace / "reproduction_test.py"
                test_file_path.write_text(test_code, encoding="utf-8")
                env = os.environ.copy()
                env["PYTHONPATH"] = str(workspace) + os.pathsep + env.get("PYTHONPATH", "")
                cmd = [sys.executable, "-m", "pytest", str(test_file_path), "-v", "--tb=short"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=workspace, env=env)

            output = proc.stdout + "\n" + proc.stderr
            status = "PASS" if proc.returncode == 0 else "FAIL"

            return {
                "result": status,
                "output": output.strip(),
                "returncode": proc.returncode
            }

        except Exception as e:
            return {
                "result": "FAIL",
                "output": f"Execution error: {str(e)}",
                "returncode": -1
            }
