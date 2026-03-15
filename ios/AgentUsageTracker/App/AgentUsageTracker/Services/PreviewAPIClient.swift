import Foundation
import AgentUsageTrackerCore

struct PreviewAPIClient: OpenCostAPIClienting {
    func fetchOverview() async throws -> OpenCostOverview {
        OpenCostOverview(totalCostUSD: 42.17, totalTokens: 154_220, activeSessions: 3)
    }

    func fetchProviderUsage() async throws -> [ProviderUsageSummary] {
        [
            ProviderUsageSummary(provider: "openai", model: "gpt-4.1", inputTokens: 60_000, outputTokens: 22_000, totalCostUSD: 18.4),
            ProviderUsageSummary(provider: "anthropic", model: "claude-3-7-sonnet", inputTokens: 52_000, outputTokens: 20_220, totalCostUSD: 23.77)
        ]
    }
}
