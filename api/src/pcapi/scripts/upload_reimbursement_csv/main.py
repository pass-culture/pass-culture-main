"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40730/script_generate_and_upload_reimbursement_csv \
  -f NAMESPACE=upload_reimbursement_csv \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import os
from datetime import date
from pathlib import Path

from pcapi.app import app
from pcapi.routes.serialization.reimbursement_csv_serialize import find_reimbursement_details_by_invoices
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv


logger = logging.getLogger("upload_reimbursement_csv")


class MissingContext(Exception):
    pass


def generate_csv(invoice_ids: set[str]) -> str:
    if not invoice_ids:
        raise MissingContext("missing invoices")

    details = find_reimbursement_details_by_invoices(invoice_ids)
    return generate_reimbursement_details_csv(details)


def file_name(day: date, offerer_id: int, invoice_ids: set[str]) -> str:
    if not offerer_id:
        raise MissingContext("missing offerer")

    if not invoice_ids:
        raise MissingContext("missing invoices")

    prefix = f"invoices_offerer-{offerer_id}"

    day_formatted = f"{day.year}-{day.month}-{day.day}"

    invoices_formatted = "_".join([str(iid) for iid in sorted(invoice_ids)])
    return f"{prefix}_{day_formatted}_{invoices_formatted}.csv"


def file_path(file_name: str) -> Path:
    dir = os.environ.get("OUTPUT_DIRECTORY")
    if not dir:
        raise MissingContext("OUTPUT_DIRECTORY not set")

    return Path(dir) / Path(file_name)


def run(day: date, offerer_id: int, invoice_ids: set[str]) -> None:
    path = file_path(file_name(day, offerer_id, invoice_ids))
    logger.info("Output path will be: %s", path)

    content = generate_csv(invoice_ids)
    logger.info("CSV data has been fetched")

    with open(path, mode="w") as f:
        f.write(content)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--offerer", type=int)
    parser.add_argument("--invoices", nargs="+")
    args = parser.parse_args()

    logger.info("starting extract... offerer %d... invoices %s", args.offerer, args.invoices)
    run(date.today(), args.offerer, set(args.invoices))
