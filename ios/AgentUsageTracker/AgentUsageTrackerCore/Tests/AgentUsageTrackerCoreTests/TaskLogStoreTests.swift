import Foundation
import Testing
@testable import AgentUsageTrackerCore

struct TaskLogStoreTests {
    @Test func saveAndLoadRoundTrip() throws {
        let tempDirectory = FileManager.default.temporaryDirectory
        let fileURL = tempDirectory.appendingPathComponent("agent_tasks_\(UUID().uuidString).json")
        defer { try? FileManager.default.removeItem(at: fileURL) }

        let store = TaskLogStore(fileURL: fileURL)
        let expected = [
            AgentTask(
                title: "Investigate context window errors",
                details: "Compare GPT-4o and Claude responses",
                status: .running,
                provider: "openai",
                model: "gpt-4o",
                startedAt: Date(timeIntervalSince1970: 1_710_000_000)
            )
        ]

        try store.save(expected)
        let loaded = try store.load()

        #expect(loaded == expected)
    }
}
