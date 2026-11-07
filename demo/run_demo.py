"""Interactive CLI / Simulator for end-to-end Bug Triage & Resolution with Switch."""

import sys
import time
import requests

# Set stdout encoding to UTF-8 for safe execution in Windows PowerShell/cmd
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def run_demo():
    print("=" * 70)
    print("[*] FLIP THE SWITCH HACKATHON: AI BUG TRIAGE & RESOLUTION DEMO")
    print("=" * 70)

    # 1. Developer reports bug
    print("\n[Step 1] Developer posts bug in Switch collaboration room...")
    time.sleep(1)
    payload = {
        "title": "Division precision truncation in calculate_average",
        "description": "Calling divide(10, 3) yields integer 3 instead of 3.3333333333333335. Causes high inaccuracy in average metrics.",
        "reported_by": "Alex_Dev",
        "severity": "high",
        "switch_room_id": "ai-bug-triage"
    }
    r = requests.post(f"{BASE_URL}/api/bugs", json=payload)
    bug = r.json()
    print(f"  [+] Created Bug #{bug['id']} - Status: {bug['status']}")
    print(f"  [!] Dispatched notification to Switch room '#{bug['switch_room_id']}'")

    # 2. AI Bug Investigator starts investigation
    print("\n[Step 2] AI Bug Investigator inspects source code AST and application logs...")
    time.sleep(1.5)
    r = requests.post(f"{BASE_URL}/api/bugs/{bug['id']}/investigate")
    inv = r.json()
    print(f"  [*] Root Cause Identified: {inv['root_cause']}")
    print(f"  [*] Affected Files: {inv['affected_files']} -> {inv['affected_functions']}")
    print(f"  [*] Reasoning: {inv['reasoning']}")

    # 3. Automated Reproduction Test
    print("\n[Step 3] AI generates & executes automated reproduction test...")
    time.sleep(1.5)
    r = requests.post(f"{BASE_URL}/api/bugs/{bug['id']}/test")
    test_res = r.json()
    print(f"  [*] Reproduction Test Result: {test_res['result']} (Expected: Bug confirmed by test failure)")
    print(f"  [*] Test Evidence Captured: {len(test_res['output'])} bytes of pytest output.")

    # 4. Patch Generation & Automated Pre-Validation
    print("\n[Step 4] AI creates minimal code patch and runs pre-validation suite...")
    time.sleep(1.5)
    r = requests.post(f"{BASE_URL}/api/bugs/{bug['id']}/patch")
    patch = r.json()
    print(f"  [+] Patch #{patch['id']} generated!")
    print("  [*] Diff Proposal:")
    print("  " + "\n  ".join(patch["diff_text"].splitlines()[:6]))

    # 5. Security Gate Verification
    print("\n[Step 5] Testing Security Policy: Attempting to apply unapproved patch...")
    r = requests.post(f"{BASE_URL}/api/bugs/{bug['id']}/patches/{patch['id']}/apply")
    if r.status_code == 400:
        print(f"  [SHIELD] BLOCKED: Security rule enforced! {r.json()['detail']}")

    # 6. Explicit Human Approval in Switch Room
    print("\n[Step 6] Senior Engineer explicitly approves the patch in Switch room...")
    time.sleep(1)
    r = requests.post(f"{BASE_URL}/api/bugs/{bug['id']}/patches/{patch['id']}/approve", json={
        "reviewer_name": "SeniorDev_Priya",
        "reason": "Code diff reviewed and pre-validation test verified passing."
    })
    print(f"  [+] Patch Approved by @{r.json()['reviewed_by']}")

    # 7. Apply Approved Patch & Generate Final Resolution Report
    print("\n[Step 7] Applying approved patch & publishing final resolution report...")
    time.sleep(1)
    r = requests.post(f"{BASE_URL}/api/bugs/{bug['id']}/patches/{patch['id']}/apply")
    res_data = r.json()
    print(f"  [SUCCESS] Status: {res_data['status'].upper()}")
    print(f"  [*] Resolution Summary: {res_data['report']['summary']}")
    print("=" * 70)
    print("[WINNER] ALL PHASES COMPLETE: DEMO SCENARIO EXECUTED WITH REAL EVIDENCE!")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
