import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function SimpleBarChart({ data, xKey, yKey }: { data: any[]; xKey: string; yKey: string }) {
  return (
    <div className="card h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey={xKey} stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip />
          <Bar dataKey={yKey} fill="#34d399" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
