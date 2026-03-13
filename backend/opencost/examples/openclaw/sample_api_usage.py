import requests

base = "http://127.0.0.1:4680"
print(requests.get(f"{base}/api/overview", params={"period": "7d"}, timeout=2).json())
print(requests.post(f"{base}/api/recommendations/generate", timeout=5).json())
