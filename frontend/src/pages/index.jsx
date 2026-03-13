import { useEffect, useState } from "react";

export default function Overview() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch("http://127.0.0.1:4680/api/overview?period=30d").then((r) => r.json()).then(setData).catch(() => setData({ error: true }));
  }, []);
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
