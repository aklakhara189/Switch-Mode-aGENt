# Agent Team Roles

## Incident Manager
Classifies impact and priority, starts the workflow, and records hand-offs.

## Log Analyzer
Finds timestamps, exceptions, warnings, and correlations from configured application logs. It returns file references and never invents log entries.

## Debugging Agent
Connects source evidence, logs, and failing-test output into a root-cause explanation.

## Testing Agent
Writes a reproduction test, executes it against the original source, validates a proposed patch only in an isolated workspace, and retains subprocess output.

## Code Fix Agent
Produces the smallest scoped unified diff. It cannot write source files.

## Reviewer Agent
Reviews the diff, validation output, patch scope, and security risks. Its recommendation is advisory. Only a human reviewer can approve a patch hash.
