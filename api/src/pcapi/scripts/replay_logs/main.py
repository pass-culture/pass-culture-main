"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=stg \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43713-replay-previous-logs \
  -f NAMESPACE=replay_logs \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import json
import logging
import os

from pcapi.core.subscription.bonus.statistics_api import ATTEMPT_TECHNICAL_MESSAGE_ID
from pcapi.core.subscription.bonus.statistics_api import COUNTERS_TECHNICAL_MESSAGE_ID


logger = logging.getLogger(__name__)


namespace_dir = os.path.dirname(os.path.abspath(__file__))


def replay_logs() -> None:
    with open(f"{namespace_dir}/counters_log.json", encoding="utf-8") as f:
        logs = json.load(f)

    for log_payload in logs:
        logger.info(
            "Bonus credit counters",
            extra={
                "published_at": log_payload["published_at"],
                "counters_since": log_payload["counters_since"],
                "counters": json.dumps(log_payload["counters"]),
                "feature": "bonus_credit",
                "action": "statistics.counters",
            },
            technical_message_id=COUNTERS_TECHNICAL_MESSAGE_ID,
        )

    with open(f"{namespace_dir}/delays_log.json", encoding="utf-8") as f:
        logs = json.load(f)

    for log_payload in logs:
        logger.info(
            "Bonus credit first attempt delays",
            extra={
                "published_at": log_payload["published_at"],
                "first_attempt_delays_since": log_payload["first_attempt_delays_since"],
                "first_attempt_delays": json.dumps(log_payload["first_attempt_delays"]),
                "feature": "bonus_credit",
                "action": "statistics.first_attempt_delays",
            },
            technical_message_id=ATTEMPT_TECHNICAL_MESSAGE_ID,
        )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    replay_logs()
