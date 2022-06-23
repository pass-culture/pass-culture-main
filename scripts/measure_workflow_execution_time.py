from datetime import datetime
import http.client
import json
import sys

import tzlocal


def measure_workflow_execution_time(
    circle_ci_token: str,
    metrics_endpoint: str,
    workflow_id: str,
    has_run_e2e_tests: str,
):
    conn = http.client.HTTPSConnection("circleci.com")
    auth = f"Basic {circle_ci_token}"
    circle_ci_headers = {"authorization": auth}
    conn.request("GET", f"/api/v2/workflow/{workflow_id}", headers=circle_ci_headers)

    res = conn.getresponse()
    data = res.read()

    created_at = datetime.strptime(json.loads(data.decode("utf-8"))["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    worfklow_execution_time = datetime.utcnow() - created_at
    conn = http.client.HTTPSConnection(metrics_endpoint)
    headers = {"Content-Type": "text/plain"}
    metric_type = "0442e902-b72c-45b7-8482-d2afe7842bf7" if has_run_e2e_tests == "True" else "2f6cabcf-51ee-44c5-b3f5-102854159dad"

    conn.request(
        "POST",
        "/push-metric",
        json.dumps(
            {
                "value": int(worfklow_execution_time.total_seconds()),
                "creationDate": datetime.now(tzlocal.get_localzone()).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "project": 988,
                "metricType": metric_type,
            }
        ),
        headers,
    )


if __name__ == "__main__":
    measure_workflow_execution_time(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
