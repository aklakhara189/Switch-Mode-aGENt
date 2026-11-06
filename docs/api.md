# API Workflow Reference

| Endpoint | Purpose |
|---|---|
| `POST /api/bugs` | Persist a new bug report |
| `POST /api/bugs/{id}/investigate` | Collect code/log evidence |
| `POST /api/bugs/{id}/test` | Run an actual reproduction test |
| `POST /api/bugs/{id}/patch` | Create a patch proposal and isolated validation evidence |
| `POST /api/bugs/{id}/patches/{patch_id}/approve` | Approve an exact `patch_hash` only |
| `POST /api/bugs/{id}/patches/{patch_id}/reject` | Reject a proposal |
| `POST /api/bugs/{id}/patches/{patch_id}/apply` | Apply only an approved, hash-matching patch |
| `POST /api/webhook/switch` | Receive a Switch event and ignore duplicate event IDs |

Approval requests must include the `patch_hash` returned with the patch proposal. This binds a human decision to the precise code that was reviewed.
