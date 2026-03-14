export default function KpiCard({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="card">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}
