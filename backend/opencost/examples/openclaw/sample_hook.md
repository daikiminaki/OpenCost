# OpenClaw integration concept

1. Run OpenCost sidecar locally: `uvicorn opencost.api.main:app --port 4680`.
2. OpenClaw post-run hook posts event logs to local file path monitored by OpenCost.
3. Optional OpenClaw tool invocation can call `GET http://127.0.0.1:4680/api/overview?period=7d`.
