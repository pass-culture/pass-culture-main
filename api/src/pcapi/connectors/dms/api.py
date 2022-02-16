import enum
import logging
import os
import pathlib
import re
from typing import Any

from dateutil import parser as date_parser
import gql
from gql.transport.requests import RequestsHTTPTransport

from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.utils import requests
from pcapi.utils.date import FrenchParserInfo


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


def parse_beneficiary_information_graphql(application_detail: dict, procedure_id: int) -> fraud_models.DMSContent:
    email = application_detail["usager"]["email"]

    information = {
        "last_name": application_detail["demandeur"]["nom"],
        "first_name": application_detail["demandeur"]["prenom"],
        "civility": application_detail["demandeur"]["civilite"],
        "email": email,
        "application_id": application_detail["number"],
        "procedure_id": procedure_id,
        "registration_datetime": application_detail[
            "datePassageEnConstruction"
        ],  # parse with format  "2021-09-15T15:19:20+02:00"
    }
    parsing_errors = {}

    if not fraud_api.is_subscription_name_valid(information["first_name"]):
        parsing_errors["first_name"] = information["first_name"]

    if not fraud_api.is_subscription_name_valid(information["last_name"]):
        parsing_errors["last_name"] = information["last_name"]

    for field in application_detail["champs"]:
        label = field["label"]
        value = field["stringValue"]

        if "Veuillez indiquer votre département" in label:
            information["department"] = re.search("^[0-9]{2,3}|[2BbAa]{2}", value).group(0)
        if label in ("Quelle est votre date de naissance", "Quelle est ta date de naissance ?"):
            try:
                information["birth_date"] = date_parser.parse(value, FrenchParserInfo())
            except Exception:  # pylint: disable=broad-except
                parsing_errors["birth_date"] = value

        if label in (
            "Quel est votre numéro de téléphone",
            "Quel est ton numéro de téléphone ?",
        ):
            information["phone"] = value.replace(" ", "")
        if label in (
            "Quel est le code postal de votre commune de résidence ?",
            "Quel est le code postal de votre commune de résidence ? (ex : 25370)",
            "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
            "Quel est le code postal de ta commune de résidence ?",
        ):
            space_free = str(value).strip().replace(" ", "")
            try:
                information["postal_code"] = re.search("^[0-9]{5}", space_free).group(0)
            except Exception:  # pylint: disable=broad-except
                parsing_errors["postal_code"] = value

        if label in ("Veuillez indiquer votre statut", "Merci d'indiquer ton statut", "Merci d' indiquer ton statut"):
            information["activity"] = value
        if label in (
            "Quelle est votre adresse de résidence",
            "Quelle est ton adresse de résidence",
            "Quelle est ton adresse de résidence ?",
        ):
            information["address"] = value
        if label in (
            "Quel est le numéro de la pièce que vous venez de saisir ?",
            "Quel est le numéro de la pièce que tu viens de saisir ?",
        ):
            value = value.strip()
            if not fraud_api.validate_id_piece_number_format_fraud_item(value):
                parsing_errors["id_piece_number"] = value
            else:
                information["id_piece_number"] = value

    if parsing_errors:
        raise subscription_exceptions.DMSParsingError(email, parsing_errors, "Error validating")
    return fraud_models.DMSContent(**information)
