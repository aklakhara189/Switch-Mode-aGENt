# Environment and Recovery Guide

## Local prerequisites

- Python 3.12+
- Git
- A running Switch bridge reachable from this computer
- A registered Switch agent with its agent API key
- An OpenAI API key for the multi-agent reasoning steps

Copy `.env.example` to an untracked `.env`; never commit that file. Set `SWITCH_API_URL`, `SWITCH_AGENT_ID`, `SWITCH_AGENT_API_KEY`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL`.

## Readiness checks

```powershell
python -m compileall -q backend
python -m pytest tests -v
python start.py
```

The Switch bridge is healthy only when `GET $SWITCH_API_URL/health` succeeds. The backend reports delivery as failed if the bridge or agent credentials are unavailable; it never reports an unsent message as delivered.

## Recovery

1. Do not delete the SQLite database, Docker volumes, or the Switch deployment.
2. Confirm the bridge URL with `/health`.
3. Verify the registered agent ID and rotate a compromised agent key.
4. Restart `python start.py` after updating `.env`.
5. Post a single `!bug` message in the authorized room and confirm its event ID is processed once.

## Switch protocol used

The client uses the documented server-side agent endpoint:

`POST /agents/{agent_id}/message` with `Authorization: Bearer <agent-api-key>` and `{ "room_id", "content" }`.

See the official [Switch agent protocol](https://docs.switchagents.ai/switch-rooms/internals/agent-protocol) for registration, room authorization, and WebSocket event delivery.
