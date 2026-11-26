"""Generate local demo traffic and verify the provisioned dashboard queries."""
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def get_json(url):
    with urlopen(url, timeout=5) as response:
        return json.load(response)


def query(expr):
    url = "http://localhost:9090/api/v1/query?" + urlencode({"query": expr})
    results = get_json(url)["data"]["result"]
    return float(results[0]["value"][1]) if results else float("nan")


def predict(data):
    request = Request("http://localhost:8015/predict", data=data,
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status
    except HTTPError as error:
        return error.code


def main():
    assert get_json("http://localhost:8015/health/ready")["model_loaded"]
    assert query('up{job="churn-api"}') == 1, "Wait for the first scrape"
    dashboard = get_json("http://localhost:3000/api/dashboards/uid/churn-api")["dashboard"]
    payload = (Path(__file__).resolve().parents[1] / "examples/predict_request_valid.json").read_bytes()
    for _ in range(12):
        assert (predict(payload), predict(b"{}")) == (200, 422)
        time.sleep(0.5)
    for _ in range(6):
        time.sleep(5)
        values = {p["title"]: query(p["targets"][0]["expr"]) for p in dashboard["panels"]}
        traffic, errors, p95 = values.values()
        if traffic > 0 and 0 < errors < 1 and p95 > 0:
            print(json.dumps(values, indent=2))
            return
    raise SystemExit(f"Missing monitoring samples: {values}")


if __name__ == "__main__":
    main()
