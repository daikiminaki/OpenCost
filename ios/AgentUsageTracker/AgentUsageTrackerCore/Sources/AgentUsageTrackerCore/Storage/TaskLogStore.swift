import Foundation

public protocol TaskLogStoring {
    func load() throws -> [AgentTask]
    func save(_ tasks: [AgentTask]) throws
}

public struct TaskLogStore: TaskLogStoring {
    private let fileURL: URL
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    public init(fileURL: URL) {
        self.fileURL = fileURL
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
    }

    public func load() throws -> [AgentTask] {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            return []
        }

        let data = try Data(contentsOf: fileURL)
        return try decoder.decode([AgentTask].self, from: data)
    }

    public func save(_ tasks: [AgentTask]) throws {
        let data = try encoder.encode(tasks)
        try data.write(to: fileURL, options: .atomic)
    }
}
