import SwiftUI
import AgentUsageTrackerCore

@main
struct AgentUsageTrackerApp: App {
    var body: some Scene {
        WindowGroup {
            DashboardView(viewModel: .preview)
        }
    }
}
