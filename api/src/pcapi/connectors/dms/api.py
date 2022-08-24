import datetime
import logging
import os
import pathlib
from typing import Any
from typing import Generator

import gql
from gql.transport.requests import RequestsHTTPTransport

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.utils import requests

from . import exceptions


logger = logging.getLogger(__name__)
GRAPHQL_DIRECTORY = pathlib.Path(os.path.dirname(__file__)) / "graphql"

ARCHIVE_APPLICATION_QUERY_NAME = "archive_application"
GET_BIC_QUERY_NAME = "pro/get_banking_info_v2"
GET_DELETED_APPLICATIONS_QUERY_NAME = "get_deleted_applications"
GET_SINGLE_APPLICATION_QUERY_NAME = "beneficiaries/get_single_application_details"
GET_APPLICATIONS_WITH_DETAILS_QUERY_NAME = "beneficiaries/get_applications_with_details"
MAKE_ON_GOING_MUTATION_NAME = "make_on_going"
MARK_WITHOUT_CONTINUATION_MUTATION_NAME = "mark_wihtout_continuation"
SEND_USER_MESSAGE_QUERY_NAME = "send_user_message"
UPDATE_TEXT_ANNOTATION_QUERY_NAME = "update_text_annotation"


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
            retries=3,
        )
        self.client = gql.Client(transport=transport, fetch_schema_from_transport=not settings.IS_RUNNING_TESTS)

    def build_query(self, query_name: str) -> str:
        return (GRAPHQL_DIRECTORY / f"{query_name}.graphql").read_text()

    def execute_query(self, query_name: str, variables: dict[str, Any]) -> dict:
        query = self.build_query(query_name)
        logger.info("Executing dms query %s", query_name, extra=variables)

        return self.client.execute(gql.gql(query), variable_values=variables)

    def get_applications_with_details(  # type: ignore [misc]
        self,
        procedure_id: int,
        state: dms_models.GraphQLApplicationStates | None = None,
        page_token: str = "",
        since: datetime.datetime | None = None,
    ) -> list[dms_models.DmsApplicationResponse]:
        variables: dict[str, int | str] = {
            "demarcheNumber": procedure_id,
        }
        if state:
            variables["state"] = state.value
        if since:
            variables["since"] = since.isoformat()
        if page_token:
            variables["after"] = page_token
        results = self.execute_query(GET_APPLICATIONS_WITH_DETAILS_QUERY_NAME, variables=variables)
        # pylint: disable=unsubscriptable-object
        dms_demarche_response = dms_models.DmsProcessApplicationsResponse(**results["demarche"]["dossiers"])
        # pylint: enable=unsubscriptable-object
        logger.info(
            "[DMS] Found %s applications for procedure %d (page token :%s)",
            len(dms_demarche_response.dms_applications),
            procedure_id,
            page_token,
        )
        for application in dms_demarche_response.dms_applications:
            yield application

        if dms_demarche_response.page_info.has_next_page:
            yield from self.get_applications_with_details(
                procedure_id, state, dms_demarche_response.page_info.end_cursor or "", since
            )

    def get_deleted_applications(
        self, procedure_id: int, page_token: str | None = None, deletedSince: datetime.datetime | None = None
    ) -> Generator[dms_models.DmsDeletedApplication, None, None]:
        variables: dict[str, Any] = {"demarcheNumber": procedure_id}
        if page_token:
            variables["after"] = page_token
        if deletedSince:
            variables["deletedSince"] = deletedSince.isoformat()
        results = self.execute_query(GET_DELETED_APPLICATIONS_QUERY_NAME, variables=variables)
        # pylint: disable=unsubscriptable-object
        dms_response = dms_models.DmsDeletedApplicationsResponse(**results["demarche"]["deletedDossiers"])
        # pylint: enable=unsubscriptable-object
        logger.info(
            "[DMS] Found %s deleted applications for procedure %d",
            len(dms_response.dms_deleted_applications),
            procedure_id,
        )
        for application in dms_response.dms_deleted_applications:
            yield application

        if dms_response.page_info.has_next_page:
            yield from self.get_deleted_applications(procedure_id, dms_response.page_info.end_cursor, deletedSince)

    def send_user_message(self, application_scalar_id: str, instructeur_techid: str, body: str) -> Any:
        try:
            return self.execute_query(
                SEND_USER_MESSAGE_QUERY_NAME,
                variables={
                    "input": {"dossierId": application_scalar_id, "instructeurId": instructeur_techid, "body": body}
                },
            )
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "DMS : unexpected error when sending message", extra={"application_scalar_id": application_scalar_id}
            )
            return None

    def archive_application(self, application_techid: str, instructeur_techid: str) -> Any:
        return self.execute_query(
            ARCHIVE_APPLICATION_QUERY_NAME,
            variables={"input": {"dossierId": application_techid, "instructeurId": instructeur_techid}},
        )

    def make_on_going(
        self, application_techid: str, instructeur_techid: str, disable_notification: bool | None = False
    ) -> Any:
        try:
            response = self.execute_query(
                MAKE_ON_GOING_MUTATION_NAME,
                variables={
                    "input": {
                        "dossierId": application_techid,
                        "instructeurId": instructeur_techid,
                        "disableNotification": disable_notification,
                    }
                },
            )
        except Exception:
            logger.exception(
                "[DMS] Unexpected error when marking on going", extra={"application_techid": application_techid}
            )
            raise exceptions.DmsGraphQLApiException()
        if response["dossierPasserEnInstruction"]["errors"]:  # pylint: disable=unsubscriptable-object
            logger.error(
                "[DMS] Error while marking application on going %s",
                response["dossierPasserEnInstruction"]["errors"],  # pylint: disable=unsubscriptable-object
                extra={"application_techid": application_techid},
            )
            raise exceptions.DmsGraphQLApiException()

    def mark_without_continuation(self, application_techid: str, instructeur_techid: str, motivation: str) -> Any:
        try:
            response = self.execute_query(
                MARK_WITHOUT_CONTINUATION_MUTATION_NAME,
                variables={
                    "input": {
                        "dossierId": application_techid,
                        "instructeurId": instructeur_techid,
                        "motivation": motivation,
                    }
                },
            )
        except Exception:
            logger.exception(
                "[DMS] Unexpected error when marking without continuation",
                extra={"application_techid": application_techid},
            )
            raise exceptions.DmsGraphQLApiException()
        if response["dossierClasserSansSuite"]["errors"]:  # pylint: disable=unsubscriptable-object
            logger.error(
                "[DMS] Error while marking application without continuation %s",
                response["dossierClasserSansSuite"]["errors"],  # pylint: disable=unsubscriptable-object
                extra={"application_techid": application_techid},
            )
            raise exceptions.DmsGraphQLApiException()

    def get_single_application_details(self, application_number: int) -> dms_models.DmsApplicationResponse:
        response = self.execute_query(
            GET_SINGLE_APPLICATION_QUERY_NAME, variables={"applicationNumber": application_number}
        )

        return dms_models.DmsApplicationResponse(**response["dossier"])  # pylint: disable=unsubscriptable-object

    def get_bic(self, dossier_id: int) -> Any:
        variables = {"dossierNumber": dossier_id}
        return self.execute_query(GET_BIC_QUERY_NAME, variables=variables)

    def update_text_annotation(self, dossier_id: str, instructeur_id: str, annotation_id: str, value: str) -> Any:
        variables = {
            "input": {
                "dossierId": dossier_id,
                "instructeurId": instructeur_id,
                "annotationId": annotation_id,
                "value": value,
            }
        }
        return self.execute_query(UPDATE_TEXT_ANNOTATION_QUERY_NAME, variables=variables)
