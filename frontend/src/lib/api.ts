const BASE = process.env.NEXT_PUBLIC_OPENCOST_API || "http://localhost:4680";

async function getJson(path: string) {
  const response = await fetch(`${BASE}${path}`);
  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
  }
  return response.json();
}

export const api = {
  dashboardOverview: () => getJson("/api/dashboard/overview"),
  recentSessions: () => getJson("/api/dashboard/recent-sessions"),
  logs: (params: Record<string, string | number>) => {
    const qs = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString();
    return getJson(`/api/logs?${qs}`);
  },
  modelUsage: () => getJson("/api/analytics/model-usage"),
  providerUsage: () => getJson("/api/analytics/provider-usage"),
  agentUsage: () => getJson("/api/analytics/agent-usage"),
  tokenEfficiency: () => getJson("/api/analytics/token-efficiency"),
  costReport: (period = "30d") => getJson(`/api/reports/cost?period=${period}`),
  insights: () => getJson("/api/insights"),
};
