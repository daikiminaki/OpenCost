import { Fragment, useState } from "react";

export default function LogsTable({ events }: { events: any[] }) {
  const [expanded, setExpanded] = useState<number | null>(null);
  return (
    <div className="card overflow-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-400">
            <th>timestamp</th><th>session</th><th>event</th><th>model</th><th>provider</th><th>tokens</th><th>cost</th><th>latency</th><th>tool_calls</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <Fragment key={e.id}>
              <tr className="cursor-pointer border-t border-slate-800" onClick={() => setExpanded(expanded === e.id ? null : e.id)}>
                <td>{e.timestamp}</td><td>{e.session_id}</td><td>{e.event_type}</td><td>{e.model}</td><td>{e.provider}</td><td>{e.tokens}</td><td>{e.cost}</td><td>{e.latency}</td><td>{e.tool_calls}</td>
              </tr>
              {expanded === e.id && (
                <tr className="border-t border-slate-800">
                  <td colSpan={9}><pre className="whitespace-pre-wrap text-xs">{JSON.stringify(e.raw_event_json, null, 2)}</pre></td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
