import { useEffect, useState } from "react";

export default function Recommendations() {
  const [items, setItems] = useState([]);
  useEffect(() => {
    fetch("http://127.0.0.1:4680/api/recommendations").then((r) => r.json()).then(setItems);
  }, []);
  return <pre>{JSON.stringify(items, null, 2)}</pre>;
}
