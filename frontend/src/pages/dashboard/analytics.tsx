import { useEffect, useState } from "react";

import SimpleBarChart from "../../components/charts/SimpleBarChart";
import SimpleLineChart from "../../components/charts/SimpleLineChart";
import TokenScatter from "../../components/charts/TokenScatter";
import { api } from "../../lib/api";

export default function AnalyticsPage() {
  const [modelUsage, setModelUsage] = useState<any[]>([]);
  const [providerUsage, setProviderUsage] = useState<any[]>([]);
  const [agentUsage, setAgentUsage] = useState<any[]>([]);
  const [eff, setEff] = useState<any[]>([]);

  useEffect(() => {
    api.modelUsage().then((d) => setModelUsage(d.series));
    api.providerUsage().then((d) => setProviderUsage(d.rows.map((r: any) => ({ key: r.provider, tokens: r.tokens })));
    api.agentUsage().then((d) => setAgentUsage(d.rows.map((r: any) => ({ key: r.agent, cost: r.cost_usd })));
    api.tokenEfficiency().then((d) => setEff(d.points));
  }, []);

  return (
    <div className="space-y-4">
      <SimpleLineChart data={modelUsage} xKey="day" yKey="tokens" />
      <SimpleBarChart data={providerUsage} xKey="key" yKey="tokens" />
      <SimpleBarChart data={agentUsage} xKey="key" yKey="cost" />
      <TokenScatter data={eff} />
    </div>
  );
}
