import sys
from dataclasses import dataclass

import click

from pcapi.models import db
from pcapi.utils import requests
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


TABLE_WHITELIST = {
    "transaction",  # exist but not declared in code
    "applicative_database_offer_legacy",  # does not exists
}


COLUMN_WHITELIST = {
    "beneficiary_fraud_check.content",  # does not exists
    "beneficiary_fraud_check.eligibility_type",  # typo it should be beneficiary_fraud_check.eligibilityType
    "beneficiary_fraud_check.user_id",  # typo it should be beneficiary_fraud_check.userId
    "opening_hours.afternoon_opening_hours",  # does not exists
    "opening_hours.morning_opening_hours",  # does not exists
}


@dataclass(frozen=True, slots=True)
class Contract:
    table_name: str
    columns: list[str]


def _load_contracts(contract_str: str) -> list[Contract]:
    contracts = []
    for line in contract_str.split("\n"):
        if not line.strip():
            continue
        raw_table, raw_columns = line.split(":")
        table = raw_table.split(".")[-1].strip()
        columns = [c.strip() for c in raw_columns.split(",")]
        contracts.append(Contract(table_name=table, columns=columns))
    print(f"{len(contracts)} contracts loaded")
    return contracts


def _validate_contacts(contracts: list[Contract]) -> list:
    errors = []
    for contract in contracts:
        table = db.metadata.tables.get(contract.table_name)
        if table is None:
            if contract.table_name not in TABLE_WHITELIST:
                errors.append(f"Table '{contract.table_name}' has been removed")
            continue
        columns = {c.name.lower() for c in table.columns}
        for contracted_column in contract.columns:
            if contracted_column.lower() not in columns:
                if f"{contract.table_name}.{contracted_column.lower()}" not in COLUMN_WHITELIST:
                    errors.append(f"Column '{contracted_column}' has been removed from table '{contract.table_name}'")
    return errors


@blueprint.cli.command("check_data_contracts")
@click.option(
    "-f",
    "--file",
    help="""Path to the data contracts""",
)
@click.option(
    "-u",
    "--url",
    help="""Url of the data contracts""",
)
def check_data_contracts(file: str | None, url: str | None) -> None:
    if all((file, url)) or not any((file, url)):
        print("Exactly one of -f or -u is mandatory")
        sys.exit(1)

    if url:
        print(f"Loading contracts from url {url}")
        response = requests.get(url)
        if not response.status_code == 200:
            print(f"Error {response.status_code} while downloading contracts")
            sys.exit(2)
        contract_str = response.text
    if file:
        print(f"Loading contracts from file {file}")
        with open(file, "r") as fp:
            contract_str = fp.read()

    contracts = _load_contracts(contract_str)
    errors = _validate_contacts(contracts)

    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"{len(errors)} errors found")
        sys.exit(3)
    print("Success")
