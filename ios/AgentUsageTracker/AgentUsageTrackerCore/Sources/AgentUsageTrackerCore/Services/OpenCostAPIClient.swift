import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

public protocol OpenCostAPIClienting {
    func fetchOverview() async throws -> OpenCostOverview
    func fetchProviderUsage() async throws -> [ProviderUsageSummary]
}

public struct OpenCostAPIClient: OpenCostAPIClienting {
    private let baseURL: URL
    private let urlSession: URLSession

    public init(baseURL: URL, urlSession: URLSession = .shared) {
        self.baseURL = baseURL
        self.urlSession = urlSession
    }

    public func fetchOverview() async throws -> OpenCostOverview {
        let endpoint = baseURL.appendingPathComponent("api/dashboard/overview")
        let response: OverviewDTO = try await get(endpoint)
        return OpenCostOverview(
            totalCostUSD: response.totalCost,
            totalTokens: response.totalTokens,
            activeSessions: response.activeSessions
        )
    }

    public func fetchProviderUsage() async throws -> [ProviderUsageSummary] {
        let endpoint = baseURL.appendingPathComponent("api/analytics/provider-usage")
        let response: [ProviderUsageDTO] = try await get(endpoint)
        return response.map {
            ProviderUsageSummary(
                provider: $0.provider,
                model: $0.model,
                inputTokens: $0.inputTokens,
                outputTokens: $0.outputTokens,
                totalCostUSD: $0.totalCost
            )
        }
    }

    private func get<T: Decodable>(_ url: URL) async throws -> T {
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("application/json", forHTTPHeaderField: "Accept")

        let (data, response) = try await urlSession.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              (200..<300).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(T.self, from: data)
    }
}

private struct OverviewDTO: Decodable {
    let totalCost: Double
    let totalTokens: Int
    let activeSessions: Int
}

private struct ProviderUsageDTO: Decodable {
    let provider: String
    let model: String
    let inputTokens: Int
    let outputTokens: Int
    let totalCost: Double
}
