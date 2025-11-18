"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-delete-redis-lock \
  -f NAMESPACE=delete_redis_lock \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

from pcapi.app import app
from pcapi.core.finance import conf


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()
    redis_key = conf.REDIS_PUSH_INVOICE_LOCK
    if app.redis_client.exists(redis_key):
        print(app.redis_client.get(redis_key))
        app.redis_client.delete(redis_key)
