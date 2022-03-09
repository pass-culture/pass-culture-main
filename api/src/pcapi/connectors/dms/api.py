import logging
import os
import pathlib
import re
from typing import Any

from dateutil import parser as date_parser
import gql
from gql.transport.requests import RequestsHTTPTransport

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.utils import requests
from pcapi.utils.date import FrenchParserInfo


logger = logging.getLogger(__name__)
GRAPHQL_DIRECTORY = pathlib.Path(os.path.dirname(__file__)) / "graphql"


class ApiDemarchesSimplifieesException(Exception):
    pass


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
        self, procedure_id: int, state: dms_models.GraphQLApplicationStates, page_token: str = ""
    ) -> list[dms_models.DmsApplicationResponse]:
        query = self.build_query("beneficiaries/get_applications_with_details")
        variables = {
            "demarcheNumber": procedure_id,
            "state": state.value,
        }
        if page_token:
            variables["after"] = page_token
        results = self.execute_query(query, variables=variables)
        dms_demarche_response = dms_models.DmsProcessApplicationsResponse(**results["demarche"]["dossiers"])
        logger.info(
            "Found %s applications for procedure %d (page token :%s)",
            len(dms_demarche_response.dms_applications),
            procedure_id,
            page_token,
        )
        for application in dms_demarche_response.dms_applications:
            yield application

        if dms_demarche_response.page_info.has_next_page:
            yield from self.get_applications_with_details(
                procedure_id, state, dms_demarche_response.page_info.end_cursor
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

    def get_single_application_details(self, application_id: int) -> dms_models.DmsApplicationResponse:
        query = self.build_query("beneficiaries/get_single_application_details")
        response = self.execute_query(query, variables={"applicationNumber": application_id})

        return dms_models.DmsApplicationResponse(**response["dossier"])

    def get_bic(self, dossier_id: int) -> Any:
        query = self.build_query("pro/get_banking_info_v2")
        variables = {"dossierNumber": dossier_id}
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


def parse_beneficiary_information_graphql(
    application_detail: dms_models.DmsApplicationResponse, procedure_id: int
) -> fraud_models.DMSContent:

    application_id = application_detail.number
    civility = application_detail.applicant.civility
    email = application_detail.profile.email
    first_name = application_detail.applicant.first_name
    last_name = application_detail.applicant.last_name
    registration_datetime = application_detail.draft_date  # parse with format  "2021-09-15T15:19:20+02:00"

    # Fields that may be filled
    activity = None
    address = None
    birth_date = None
    department = None
    id_piece_number = None
    phone = None
    postal_code = None

    parsing_errors = {}

    if not fraud_api.is_subscription_name_valid(first_name):
        parsing_errors["first_name"] = first_name

    if not fraud_api.is_subscription_name_valid(last_name):
        parsing_errors["last_name"] = last_name

    for field in application_detail.fields:
        label = field.label
        value = field.value

        if label in (dms_models.FieldLabel.DEPARTMENT_FR.value, dms_models.FieldLabel.DEPARTMENT_ET.value):
            department = re.search("^[0-9]{2,3}|[2BbAa]{2}", value).group(0)
        if label in (dms_models.FieldLabel.BIRTH_DATE_ET, dms_models.FieldLabel.BIRTH_DATE_FR.value):
            try:
                birth_date = date_parser.parse(value, FrenchParserInfo())
            except Exception:  # pylint: disable=broad-except
                parsing_errors["birth_date"] = value

        if label in (dms_models.FieldLabel.TELEPHONE_FR.value, dms_models.FieldLabel.TELEPHONE_ET.value):
            phone = value.replace(" ", "")
        if label in (
            dms_models.FieldLabel.POSTAL_CODE_ET.value,
            dms_models.FieldLabel.POSTAL_CODE_FR.value,
        ):
            space_free = str(value).strip().replace(" ", "")
            try:
                postal_code = re.search("^[0-9]{5}", space_free).group(0)
            except Exception:  # pylint: disable=broad-except
                parsing_errors["postal_code"] = value

        if label in (dms_models.FieldLabel.ACTIVITY_FR.value, dms_models.FieldLabel.ACTIVITY_ET.value):
            activity = value
        if label in (
            dms_models.FieldLabel.ADDRESS_ET.value,
            dms_models.FieldLabel.ADDRESS_FR.value,
        ):
            address = value
        if label in (
            dms_models.FieldLabel.ID_PIECE_NUMBER_FR.value,
            dms_models.FieldLabel.ID_PIECE_NUMBER_ET.value,
        ):
            value = value.strip()
            if not fraud_api.validate_id_piece_number_format_fraud_item(value):
                parsing_errors["id_piece_number"] = value
            else:
                id_piece_number = value

    if parsing_errors:
        raise subscription_exceptions.DMSParsingError(email, parsing_errors, "Error validating")
    return fraud_models.DMSContent(
        activity=activity,
        address=address,
        application_id=application_id,
        birth_date=birth_date,
        civility=civility,
        department=department,
        email=email,
        first_name=first_name,
        id_piece_number=id_piece_number,
        last_name=last_name,
        phone=phone,
        postal_code=postal_code,
        procedure_id=procedure_id,
        registration_datetime=registration_datetime,
    )
