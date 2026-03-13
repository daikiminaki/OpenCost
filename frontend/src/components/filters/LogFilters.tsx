export default function LogFilters({ filters, setFilters, onApply }: any) {
  return (
    <div className="card grid grid-cols-2 gap-3 md:grid-cols-5">
      {["provider", "model", "task_category", "agent", "session_id", "q"].map((key) => (
        <input
          key={key}
          className="rounded bg-slate-800 p-2"
          placeholder={key}
          value={filters[key] || ""}
          onChange={(e) => setFilters({ ...filters, [key]: e.target.value })}
        />
      ))}
      <button className="rounded bg-blue-600 px-3 py-2" onClick={onApply}>Apply</button>
    </div>
  );
}
