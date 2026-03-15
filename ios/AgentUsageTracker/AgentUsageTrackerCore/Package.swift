// swift-tools-version: 6.1
import PackageDescription

let package = Package(
    name: "AgentUsageTrackerCore",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(name: "AgentUsageTrackerCore", targets: ["AgentUsageTrackerCore"])
    ],
    targets: [
        .target(name: "AgentUsageTrackerCore"),
        .testTarget(name: "AgentUsageTrackerCoreTests", dependencies: ["AgentUsageTrackerCore"])
    ]
)
