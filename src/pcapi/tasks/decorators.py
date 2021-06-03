import json
import logging

from flask.blueprints import Blueprint
from google.cloud import tasks_v2

from pcapi import settings


GCP_PROJECT = "passculture-metier-ehp"
GCP_LOCATION = "europe-west1"
CLOUD_TASK_SUBPATH = "/cloud-tasks"


default_queue = "test-cyril"


logger = logging.getLogger(__name__)

cloud_task_api = Blueprint("Cloud task internal API", __name__, url_prefix=CLOUD_TASK_SUBPATH)

client = tasks_v2.CloudTasksClient()


def enqueue_cloud_task(queue, path, payload):
    parent = client.queue_path(GCP_PROJECT, GCP_LOCATION, queue)

    url = settings.API_URL + CLOUD_TASK_SUBPATH + path
    body = json.dumps(payload).encode()

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "headers": {"Content-type": "application/json"},
            "body": body,
        },
    }

    response = client.create_task(request={"parent": parent, "task": task})
    print("Created task {}".format(response.name))
