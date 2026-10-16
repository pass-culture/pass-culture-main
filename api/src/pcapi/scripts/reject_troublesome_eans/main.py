"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=.invalid \
  -f NAMESPACE=reject_troublesome_eans \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os

from pcapi.core.offers.api import reject_inappropriate_products
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def main(filename: str, apply: bool) -> None:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = f"{namespace_dir}/{filename}.csv"

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\n")
        rows = list(reader)

    for row in rows:
        ean = row["ean"]
        with atomic():
            if not apply:
                mark_transaction_as_invalid()
            reject_inappropriate_products([ean], author=None, rejected_by_fraud_action=True)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--filename", required=True, type=str)
    args = parser.parse_args()

    main(args.filename, args.apply)
