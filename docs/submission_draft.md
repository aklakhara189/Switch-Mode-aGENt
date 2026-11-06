# Hackathon Submission Draft

## Project title
AI Bug Triage & Resolution Team

## Tracks
Best Business Workflow / Switch collaboration workflow

## Project description
AI Bug Triage & Resolution Team turns a bug report from a Switch room into an evidence-backed, human-controlled resolution workflow. Specialized agents classify incidents, inspect application logs and source code, generate and execute reproduction tests, propose minimal diffs, and validate those diffs in an isolated workspace. A patch cannot be applied until an authorized human approves the exact SHA-256 hash of the reviewed code.

The project is for software teams that need faster incident triage without losing safety, traceability, or final human control.

## How Switch is used
The backend uses Switch as the collaboration surface. A developer posts a `!bug` report to a Switch room. The backend deduplicates the incoming event, starts the agent workflow, and posts investigation, test, patch, review, and resolution messages through the registered Switch agent API. Human approval/rejection is routed back to the backend and bound to the exact proposed patch hash.

## What worked and what to improve
Switch provides a clear shared room for the human/agent workflow and a documented agent bridge protocol. The biggest improvement would be an official reference SDK for Python clients, including typed WebSocket event models and local integration-test fixtures.

## Fill before submitting

- Public repository: `TODO`
- Demo video (under 3 minutes): `TODO`
- Live deployment (optional): `TODO`
- Blog post (optional): `TODO`
- Wispr card / #HowISwitch post (only if entering those tracks): `TODO`
