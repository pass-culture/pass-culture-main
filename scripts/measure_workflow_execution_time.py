from datetime import datetime
import http.client
import json
import sys

import tzlocal


def measure_workflow_execution_time(
    circle_ci_token,
    metrics_endpoint,
    workflow_id,
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

    conn.request(
        "POST",
        "/push-metric",
        json.dumps(
            {
                "value": int(worfklow_execution_time.total_seconds()),
                "creationDate": datetime.now(tzlocal.get_localzone()).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "project": 988,
                "metricType": "0442e902-b72c-45b7-8482-d2afe7842bf7",
            }
        ),
        headers,
    )


if __name__ == "__main__":
    measure_workflow_execution_time(sys.argv[1], sys.argv[2], sys.argv[3])
