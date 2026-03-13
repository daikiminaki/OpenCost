import { useEffect, useState } from "react";

import LogFilters from "../../components/filters/LogFilters";
import LogsTable from "../../components/tables/LogsTable";
import { api } from "../../lib/api";

export default function LogsPage() {
  const [filters, setFilters] = useState<any>({ limit: 50, offset: 0 });
  const [data, setData] = useState<any>({ events: [], total_count: 0 });

  const load = () => api.logs(filters).then(setData);

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <LogFilters filters={filters} setFilters={setFilters} onApply={load} />
      <p className="text-sm text-slate-400">Total events: {data.total_count}</p>
      <LogsTable events={data.events} />
      <div className="flex gap-2">
        <button className="rounded bg-slate-800 px-3 py-2" onClick={() => { const next = { ...filters, offset: Math.max((filters.offset || 0) - 50, 0) }; setFilters(next); api.logs(next).then(setData); }}>Prev</button>
        <button className="rounded bg-slate-800 px-3 py-2" onClick={() => { const next = { ...filters, offset: (filters.offset || 0) + 50 }; setFilters(next); api.logs(next).then(setData); }}>Next</button>
      </div>
    </div>
  );
}
