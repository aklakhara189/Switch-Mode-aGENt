# Multi-Agent Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer in Switch
    participant SW as Switch room
    participant API as FastAPI backend
    participant IM as Incident Manager
    participant LA as Log Analyzer
    participant DA as Debugging Agent
    participant TA as Testing Agent
    participant CF as Code Fix Agent
    participant RV as Reviewer
    participant Human as Authorized reviewer

    Dev->>SW: !bug description
    SW->>API: addressed Switch event
    API->>IM: classify report
    API->>LA: inspect actual logs
    API->>DA: inspect source and evidence
    DA->>TA: request reproduction test
    TA->>API: failing result from original code
    API->>CF: request minimal proposal
    CF->>TA: validate proposal in isolated workspace
    TA->>RV: pass patch and test evidence
    RV->>SW: advisory review + approval request
    Human->>SW: approve exact patch hash
    SW->>API: signed/authorized decision
    API->>TA: post-apply validation
    API->>SW: resolution report
```

## Roles and safety boundaries

| Role | Does | Cannot do |
|---|---|---|
| Incident Manager | Classifies and coordinates state | Apply a patch |
| Log Analyzer | Reads configured application logs | Invent log evidence |
| Debugging Agent | Connects source evidence to the failure | Claim an LLM result without a provider response |
| Testing Agent | Generates/runs reproduction and validation tests | Mark a process error as a passing test |
| Code Fix Agent | Proposes minimal diffs | Write source files |
| Reviewer | Supplies an advisory risk review | Approve or apply its own patch |
| Human reviewer | Approves/rejects a hash-bound patch through Switch | Bypass validation or authorization checks |

All agent outputs are structured and retained in workflow history. A missing LLM credential creates a `blocked` outcome; it never falls back to fabricated AI text.
