import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";

export default function TokenScatter({ data }: { data: any[] }) {
  return (
    <div className="card h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="prompt_tokens" name="Prompt" stroke="#94a3b8" />
          <YAxis dataKey="completion_tokens" name="Completion" stroke="#94a3b8" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter data={data} fill="#22d3ee" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
