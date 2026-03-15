import Foundation
import AgentUsageTrackerCore

@MainActor
final class DashboardViewModel: ObservableObject {
    @Published var tasks: [AgentTask] = []
    @Published var overview: OpenCostOverview?
    @Published var providerUsage: [ProviderUsageSummary] = []
    @Published var errorMessage: String?

    private let apiClient: OpenCostAPIClienting

    init(apiClient: OpenCostAPIClienting) {
        self.apiClient = apiClient
    }

    func load() async {
        do {
            async let overviewTask = apiClient.fetchOverview()
            async let providerUsageTask = apiClient.fetchProviderUsage()
            overview = try await overviewTask
            providerUsage = try await providerUsageTask
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

extension DashboardViewModel {
    static var preview: DashboardViewModel {
        DashboardViewModel(apiClient: PreviewAPIClient())
    }
}
