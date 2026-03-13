import { useEffect, useState } from "react";

export default function Usage() {
  const [models, setModels] = useState([]);
  const [categories, setCategories] = useState([]);
  useEffect(() => {
    fetch("http://127.0.0.1:4680/api/usage/models").then((r) => r.json()).then(setModels);
    fetch("http://127.0.0.1:4680/api/usage/categories").then((r) => r.json()).then(setCategories);
  }, []);
  return <div><h3>Models</h3><pre>{JSON.stringify(models, null, 2)}</pre><h3>Categories</h3><pre>{JSON.stringify(categories, null, 2)}</pre></div>;
}
