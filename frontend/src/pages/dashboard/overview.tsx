import { useEffect, useState } from "react";

import KpiCard from "../../components/cards/KpiCard";
import SimpleBarChart from "../../components/charts/SimpleBarChart";
import SimpleLineChart from "../../components/charts/SimpleLineChart";
import SimplePieChart from "../../components/charts/SimplePieChart";
import { api } from "../../lib/api";

export default function OverviewPage() {
  const [data, setData] = useState<any>(null);
  const [sessions, setSessions] = useState<any[]>([]);

  useEffect(() => {
    api.dashboardOverview().then(setData);
    api.recentSessions().then((res) => setSessions(res.sessions || []));
  }, []);

  if (!data) return <p>Loading dashboard...</p>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <KpiCard title="Cost Today" value={`$${data.kpis.total_cost_today}`} />
        <KpiCard title="Cost 7d" value={`$${data.kpis.total_cost_7d}`} />
        <KpiCard title="Tokens 7d" value={data.kpis.total_tokens_7d} />
        <KpiCard title="Sessions 7d" value={data.kpis.total_sessions_7d} />
        <KpiCard title="Avg Cost / Task" value={`$${data.kpis.avg_cost_per_task_7d}`} />
        <KpiCard title="Most Used Model" value={data.kpis.most_used_model_7d || "n/a"} />
      </div>

      <SimpleLineChart data={data.cost_trend} xKey="day" yKey="total_cost_usd" />
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <SimplePieChart data={data.provider_breakdown.map((p: any) => ({ ...p, key: p.provider }))} dataKey="cost_usd" />
        <SimpleBarChart data={data.model_distribution} xKey="key" yKey="count" />
      </div>
      <SimpleBarChart data={data.task_category_distribution} xKey="key" yKey="total_cost_usd" />

      <div className="card overflow-auto">
        <h3 className="mb-2 text-lg font-semibold">Recent Sessions</h3>
        <table className="w-full text-sm">
          <thead className="text-slate-400"><tr><th>session_id</th><th>agent</th><th>model</th><th>tokens</th><th>cost</th><th>duration(s)</th><th>category</th></tr></thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.session_id} className="border-t border-slate-800">
                <td>{s.session_id}</td><td>{s.agent}</td><td>{s.model}</td><td>{s.total_tokens}</td><td>{s.estimated_cost_usd}</td><td>{s.duration_seconds}</td><td>{s.task_category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
