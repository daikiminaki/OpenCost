# AgentUsageTracker (iOS subproject)

AgentUsageTracker is a starter iOS subproject for OpenCost that focuses on:

1. **Task tracking** for OpenClaw agent runs (task title, status, timestamps, notes).
2. **Usage summaries** across providers/models (input/output tokens, estimated cost).
3. **OpenCost backend integration** so mobile users can quickly understand what an agent worked on and how much it cost.

## Layout

- `AgentUsageTrackerCore/`: Swift Package with portable domain models, persistence, and API client logic.
- `App/AgentUsageTracker/`: SwiftUI app scaffold wired to the core package.

## Quick start

### 1) Validate the core package (Linux/macOS)

```bash
cd ios/AgentUsageTracker/AgentUsageTrackerCore
swift test
```

### 2) Open in Xcode (macOS)

1. Create a new **iOS App** project named `AgentUsageTracker` in Xcode.
2. Replace its source files with files from `App/AgentUsageTracker`.
3. Add local package dependency:
   - `ios/AgentUsageTracker/AgentUsageTrackerCore`
4. Configure base URL to your OpenCost backend (`http://localhost:4680` for simulator with local networking setup).

## Planned next steps

- OAuth/API key management for provider usage APIs.
- Background refresh and local notifications for task status changes.
- Charts for daily token/cost trends.
- Optional sync to iCloud/CloudKit.
