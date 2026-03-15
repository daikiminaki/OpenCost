import Foundation

public enum TaskStatus: String, Codable, CaseIterable, Sendable {
    case queued
    case running
    case completed
    case failed
}

public struct AgentTask: Identifiable, Codable, Equatable, Sendable {
    public let id: UUID
    public var title: String
    public var details: String
    public var status: TaskStatus
    public var provider: String
    public var model: String
    public var startedAt: Date
    public var finishedAt: Date?

    public init(
        id: UUID = UUID(),
        title: String,
        details: String,
        status: TaskStatus,
        provider: String,
        model: String,
        startedAt: Date = Date(),
        finishedAt: Date? = nil
    ) {
        self.id = id
        self.title = title
        self.details = details
        self.status = status
        self.provider = provider
        self.model = model
        self.startedAt = startedAt
        self.finishedAt = finishedAt
    }
}
