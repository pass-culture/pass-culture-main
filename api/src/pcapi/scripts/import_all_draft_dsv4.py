import argparse
from typing import Iterable

from pcapi.connectors.dms.api import DMSGraphQLClient
from pcapi.connectors.dms.api import GET_BANK_INFO_APPLICATIONS_QUERY_NAME
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.settings import DMS_VENUE_PROCEDURE_ID_V4
from pcapi.use_cases.save_venue_bank_informations import ApplicationDetailNewJourney
from pcapi.use_cases.save_venue_bank_informations import ImportBankAccountV4


app.app_context().push()


def fetch_dsv4_applications(client: DMSGraphQLClient, variables: dict, page_token: str | None = None) -> Iterable[dict]:
    if page_token:
        variables["after"] = page_token

    results = client.execute_query(GET_BANK_INFO_APPLICATIONS_QUERY_NAME, variables=variables)
    nodes = results["demarche"]["dossiers"]["nodes"]
    has_next_page = results["demarche"]["dossiers"]["pageInfo"]["hasNextPage"]
    yield from nodes

    if has_next_page:
        page_token = results["demarche"]["dossiers"]["pageInfo"]["endCursor"]
        yield from fetch_dsv4_applications(client, variables, page_token=page_token)


def do_import() -> None:
    client = DMSGraphQLClient()
    variables = {
        "demarcheNumber": int(DMS_VENUE_PROCEDURE_ID_V4),
        "archived": False,
        "state": GraphQLApplicationStates.draft.value,
    }
    procedure_version = 4
    for node in fetch_dsv4_applications(client, variables):
        data = parse_raw_bank_info_data(node, procedure_version=procedure_version)
        application = ApplicationDetailNewJourney(**{"application_type": procedure_version, **data})
        importer = ImportBankAccountV4(application)
        importer.execute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import all existing draft DSv4")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        do_import()
    except Exception:
        db.session.rollback()
    else:
        if args.dry_run:
            print("--- dry run ---")
            db.session.rollback()
        else:
            print("--- commit ---")
            db.session.commit()
