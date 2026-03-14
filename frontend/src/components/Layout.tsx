import Link from "next/link";

const links = [
  ["Overview", "/dashboard/overview"],
  ["Log Explorer", "/dashboard/logs"],
  ["Usage Analytics", "/dashboard/analytics"],
  ["Cost Reports", "/dashboard/reports"],
  ["Optimization Insights", "/dashboard/insights"],
] as const;

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-7xl p-6">
      <h1 className="mb-4 text-3xl font-bold">OpenCost Dashboard</h1>
      <nav className="mb-6 flex flex-wrap gap-2">
        {links.map(([label, href]) => (
          <Link className="rounded bg-slate-800 px-3 py-2 hover:bg-slate-700" key={href} href={href}>
            {label}
          </Link>
        ))}
      </nav>
      {children}
    </div>
  );
}
