import os
from datetime import date
from pathlib import Path

from pcapi.app import app
from pcapi.routes.serialization.reimbursement_csv_serialize import find_reimbursement_details_by_invoices
from pcapi.routes.serialization.reimbursement_csv_serialize import generate_reimbursement_details_csv


INVOICE_IDS = {"F260003543"}
OFFERER_ID = 12720


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
    content = generate_csv(invoice_ids)
    with open(path, mode="w") as f:
        f.write(content)


if __name__ == "__main__":
    app.app_context().push()

    run(date.today(), OFFERER_ID, INVOICE_IDS)
