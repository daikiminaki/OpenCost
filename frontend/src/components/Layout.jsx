import Link from "next/link";

export default function Layout({ children }) {
  return (
    <div style={{ fontFamily: "Inter, Arial", padding: 20 }}>
      <h1>OpenCost Dashboard</h1>
      <nav style={{ display: "flex", gap: 16, marginBottom: 20 }}>
        <Link href="/">Overview</Link>
        <Link href="/usage">Usage</Link>
        <Link href="/recommendations">Recommendations</Link>
        <Link href="/configs">Config Versions</Link>
      </nav>
      {children}
    </div>
  );
}
