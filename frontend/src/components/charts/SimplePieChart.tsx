import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = ["#60a5fa", "#34d399", "#f59e0b", "#f472b6", "#a78bfa"];

export default function SimplePieChart({ data, dataKey }: { data: any[]; dataKey: string }) {
  return (
    <div className="card h-72">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey={dataKey} nameKey="key" outerRadius={95}>
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
