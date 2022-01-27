import enum
import logging
import os
import pathlib
from typing import Any

import gql
from gql.transport.requests import RequestsHTTPTransport

from pcapi import settings
from pcapi.utils import requests


logger = logging.getLogger(__name__)
GRAPHQL_DIRECTORY = pathlib.Path(os.path.dirname(__file__)) / "graphql"


class ApiDemarchesSimplifieesException(Exception):
    pass


class DmsApplicationStates(enum.Enum):
    closed = enum.auto()
    initiated = enum.auto()
    refused = enum.auto()
    received = enum.auto()
    without_continuation = enum.auto()


class GraphQLApplicationStates(enum.Enum):
    draft = "en_construction"
    on_going = "en_instruction"
    accepted = "accepte"
    refused = "refuse"
    without_continuation = "sans_suite"


def get_application_details(application_id: str, procedure_id: str, token: str) -> dict:
    response = requests.get(
        f"https://www.demarches-simplifiees.fr/api/v1/procedures/{procedure_id}/dossiers/{application_id}?token={token}"
    )

    if response.status_code != 200:
        raise ApiDemarchesSimplifieesException(
            f"Error getting API démarches simplifiées DATA for procedure_id: {procedure_id}, application_id: {application_id}"
        )

    return response.json()


class DMSGraphQLClient:
    def __init__(self) -> None:
        transport = RequestsHTTPTransport(
            url="https://www.demarches-simplifiees.fr/api/v2/graphql",
            headers={"Authorization": f"Bearer {settings.DMS_TOKEN}"},
        )
        self.client = gql.Client(transport=transport, fetch_schema_from_transport=not settings.IS_RUNNING_TESTS)

    def build_query(self, query_name: str) -> str:
        return (GRAPHQL_DIRECTORY / f"{query_name}.graphql").read_text()

    def execute_query(self, query: str, variables: dict[str, Any]) -> Any:
        return self.client.execute(gql.gql(query), variable_values=variables)

    def get_applications_with_details(
        self, procedure_id: int, state: GraphQLApplicationStates, page_token: str = ""
    ) -> Any:
        query = self.build_query("beneficiaries/get_applications_with_details")
        variables = {
            "demarcheNumber": procedure_id,
            "state": state.value,
        }
        if page_token:
            variables["after"] = page_token
        results = self.execute_query(query, variables=variables)
        logger.info(
            "Found %s applications for procedure %d (page token :%s)",
            len(results["demarche"]["dossiers"]["nodes"]),
            procedure_id,
            page_token,
        )
        for application in results["demarche"]["dossiers"]["nodes"]:
            yield application

        if results["demarche"]["dossiers"]["pageInfo"]["hasNextPage"]:
            yield from self.get_applications_with_details(
                procedure_id, state, results["demarche"]["dossiers"]["pageInfo"]["endCursor"]
            )

    def send_user_message(self, dossier_techid: str, instructeur_techid: str, body: str) -> Any:
        query = self.build_query("send_user_message")
        return self.execute_query(
            query, variables={"input": {"dossierId": dossier_techid, "instructeurId": instructeur_techid, "body": body}}
        )

    def archive_application(self, application_techid: str, instructeur_techid: str) -> Any:
        query = self.build_query("archive_application")

        return self.execute_query(
            query, variables={"input": {"dossierId": application_techid, "instructeurId": instructeur_techid}}
        )

    def get_single_application_details(self, application_id: int) -> Any:
        query = self.build_query("beneficiaries/get_single_application_details")

        return self.execute_query(query, variables={"applicationNumber": application_id})

    def get_bic(self, dossier_id: int) -> Any:
        query = self.build_query("pro/get_banking_info_v2")
        variables = {"dossierNumber": dossier_id}
        return self.execute_query(query, variables=variables)

    def update_checkbox_annotation(self, dossier_id: str, instructeur_id: str, annotation_id: str, value: bool) -> Any:
        query = self.build_query("update_checkbox_annotation")
        variables = {
            "input": {
                "dossierId": dossier_id,
                "instructeurId": instructeur_id,
                "annotationId": annotation_id,
                "value": value,
            }
        }
        return self.execute_query(query, variables=variables)

    def update_text_annotation(self, dossier_id: str, instructeur_id: str, annotation_id: str, value: str) -> Any:
        query = self.build_query("update_text_annotation")
        variables = {
            "input": {
                "dossierId": dossier_id,
                "instructeurId": instructeur_id,
                "annotationId": annotation_id,
                "value": value,
            }
        }
        return self.execute_query(query, variables=variables)
