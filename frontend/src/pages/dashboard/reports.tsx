import { useEffect, useState } from "react";

import SimpleBarChart from "../../components/charts/SimpleBarChart";
import SimpleLineChart from "../../components/charts/SimpleLineChart";
import { api } from "../../lib/api";

export default function ReportsPage() {
  const [period, setPeriod] = useState("30d");
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    api.costReport(period).then(setReport);
  }, [period]);

  if (!report) return <p>Loading reports...</p>;

  return (
    <div className="space-y-4">
      <select className="rounded bg-slate-800 p-2" value={period} onChange={(e) => setPeriod(e.target.value)}>
        <option value="7d">7d</option>
        <option value="30d">30d</option>
        <option value="90d">90d</option>
      </select>
      <SimpleLineChart data={report.cost_trend} xKey="day" yKey="total_cost_usd" />
      <SimpleBarChart data={report.cost_by_task_type} xKey="key" yKey="total_cost_usd" />
      <SimpleBarChart data={report.cost_by_model} xKey="key" yKey="total_cost_usd" />
      <div className="card overflow-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400"><tr><th>month</th><th>total_cost</th><th>total_tokens</th><th>sessions</th><th>avg_cost_per_session</th></tr></thead>
          <tbody>
            {report.monthly_summary.map((m: any) => (
              <tr key={m.month} className="border-t border-slate-800"><td>{m.month}</td><td>{m.total_cost}</td><td>{m.total_tokens}</td><td>{m.sessions}</td><td>{m.avg_cost_per_session}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
