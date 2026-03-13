import { useEffect, useState } from "react";

import { api } from "../../lib/api";

export default function InsightsPage() {
  const [items, setItems] = useState<any[]>([]);
  useEffect(() => {
    api.insights().then((d) => setItems(d.insights || []));
  }, []);

  return (
    <div className="grid gap-4">
      {items.map((i, idx) => (
        <div key={idx} className="card">
          <h3 className="text-lg font-semibold">{i.title}</h3>
          <p className="text-slate-300">{i.description}</p>
          <p className="mt-2 text-sm text-slate-400">Suggested: {i.suggested_routing_strategy}</p>
          <p className="text-sm text-emerald-400">Est. monthly savings: ${i.estimated_monthly_savings_usd}</p>
          <pre className="mt-2 whitespace-pre-wrap text-xs text-slate-400">{JSON.stringify(i.evidence, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}
