import Foundation

public struct ProviderUsageSummary: Codable, Equatable, Sendable {
    public var provider: String
    public var model: String
    public var inputTokens: Int
    public var outputTokens: Int
    public var totalCostUSD: Double

    public init(provider: String, model: String, inputTokens: Int, outputTokens: Int, totalCostUSD: Double) {
        self.provider = provider
        self.model = model
        self.inputTokens = inputTokens
        self.outputTokens = outputTokens
        self.totalCostUSD = totalCostUSD
    }
}

public struct OpenCostOverview: Codable, Equatable, Sendable {
    public var totalCostUSD: Double
    public var totalTokens: Int
    public var activeSessions: Int

    public init(totalCostUSD: Double, totalTokens: Int, activeSessions: Int) {
        self.totalCostUSD = totalCostUSD
        self.totalTokens = totalTokens
        self.activeSessions = activeSessions
    }
}
