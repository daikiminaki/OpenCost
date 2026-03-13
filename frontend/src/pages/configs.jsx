import { useEffect, useState } from "react";

export default function Configs() {
  const [items, setItems] = useState([]);
  useEffect(() => {
    fetch("http://127.0.0.1:4680/api/configs").then((r) => r.json()).then(setItems);
  }, []);
  return <pre>{JSON.stringify(items, null, 2)}</pre>;
}
