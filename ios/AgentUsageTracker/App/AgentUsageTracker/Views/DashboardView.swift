import SwiftUI
import AgentUsageTrackerCore

struct DashboardView: View {
    @StateObject var viewModel: DashboardViewModel

    var body: some View {
        NavigationStack {
            List {
                if let overview = viewModel.overview {
                    Section("Overview") {
                        LabeledContent("Total Cost", value: overview.totalCostUSD, format: .currency(code: "USD"))
                        LabeledContent("Total Tokens", value: "\(overview.totalTokens)")
                        LabeledContent("Active Sessions", value: "\(overview.activeSessions)")
                    }
                }

                Section("Provider Usage") {
                    ForEach(viewModel.providerUsage, id: \.model) { usage in
                        VStack(alignment: .leading, spacing: 4) {
                            Text("\(usage.provider) • \(usage.model)")
                                .font(.headline)
                            Text("Input: \(usage.inputTokens)  Output: \(usage.outputTokens)")
                                .font(.subheadline)
                            Text(usage.totalCostUSD, format: .currency(code: "USD"))
                                .font(.subheadline.weight(.semibold))
                        }
                    }
                }
            }
            .navigationTitle("Agent Usage")
            .task {
                await viewModel.load()
            }
            .overlay(alignment: .bottom) {
                if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .foregroundStyle(.white)
                        .padding(12)
                        .background(.red.opacity(0.9))
                        .clipShape(.rect(cornerRadius: 10))
                        .padding()
                }
            }
        }
    }
}

#Preview {
    DashboardView(viewModel: .preview)
}
