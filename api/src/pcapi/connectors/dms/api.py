import datetime
import logging
import os
import pathlib
from typing import Any
from typing import Generator

import gql
import gql.transport.exceptions as gql_exceptions
import urllib3.exceptions

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.routes.serialization import BaseModel
from pcapi.utils import requests
from pcapi.utils.requests import exceptions as requests_exception

from . import exceptions


logger = logging.getLogger(__name__)
GRAPHQL_DIRECTORY = pathlib.Path(os.path.dirname(__file__)) / "graphql"
DEFAULT_RETRIES = 3

ARCHIVE_APPLICATION_QUERY_NAME = "archive_application"
GET_BANK_INFO_STATUS_QUERY_NAME = "pro/get_bank_info_status"
GET_DELETED_APPLICATIONS_QUERY_NAME = "get_deleted_applications"
GET_SINGLE_APPLICATION_QUERY_NAME = "beneficiaries/get_single_application_details"
GET_APPLICATIONS_WITH_DETAILS_QUERY_NAME = "beneficiaries/get_applications_with_details"
MAKE_ON_GOING_MUTATION_NAME = "make_on_going"
MAKE_ACCEPTED_MUTATION_NAME = "make_accepted"
MAKE_REFUSED_MUTATION_NAME = "make_refused"
MARK_WITHOUT_CONTINUATION_MUTATION_NAME = "mark_without_continuation"
SEND_USER_MESSAGE_QUERY_NAME = "send_user_message"
UPDATE_TEXT_ANNOTATION_QUERY_NAME = "update_text_annotation"
GET_EAC_APPLICATIONS_STATE_SIRET = "eac/get_applications_state_siret"
GET_BANK_INFO_APPLICATIONS_QUERY_NAME = "pro/get_bank_info_applications"
GET_INSTRUCTORS_QUERY_NAME = "get_instructors"
GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME = "beneficiaries/get_account_update_applications"
ADD_LABEL = "add_label"


class DmsStats(BaseModel):
    status: str
    subscriptionDate: datetime.datetime
    lastChangeDate: datetime.datetime
    url: str


class DMSGraphQLClient:
    def __init__(self, retries: int = DEFAULT_RETRIES, timeout: int | None = None) -> None:
        transport = requests.CustomGqlTransport(
            url="https://www.demarches-simplifiees.fr/api/v2/graphql",
            headers={"Authorization": f"Bearer {settings.DMS_TOKEN}"},
            retries=retries,
        )
        self.client = gql.Client(transport=transport)
        self._timeout = timeout

    def build_query(self, query_name: str) -> str:
        return (GRAPHQL_DIRECTORY / f"{query_name}.graphql").read_text()

    def execute_query(self, query_name: str, variables: dict[str, Any]) -> dict:
        query = self.build_query(query_name)
        logger.info("Executing dms query %s", query_name, extra=variables)

        return self.client.execute(gql.gql(query), variable_values=variables, timeout=self._timeout)

    def get_applications_with_details(
        self,
        procedure_id: int,
        state: dms_models.GraphQLApplicationStates | None = None,
        page_token: str | None = None,
        since: datetime.datetime | None = None,
    ) -> Generator[dms_models.DmsApplicationResponse, None, None]:
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
        dossiers = results["demarche"]["dossiers"]
        dms_demarche_response = dms_models.DmsProcessApplicationsResponse(**dossiers)
        logger.info(
            "[DMS] Found %s applications for procedure %d (page token :%s)",
            len(dms_demarche_response.dms_applications),
            procedure_id,
            page_token,
        )
        yield from dms_demarche_response.dms_applications

        if dms_demarche_response.page_info.has_next_page:
            yield from self.get_applications_with_details(
                procedure_id, state, dms_demarche_response.page_info.end_cursor, since
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
        deleted_dossiers = results["demarche"]["deletedDossiers"]
        dms_response = dms_models.DmsDeletedApplicationsResponse(**deleted_dossiers)
        logger.info(
            "[DMS] Found %s deleted applications for procedure %d",
            len(dms_response.dms_deleted_applications),
            procedure_id,
        )
        yield from dms_response.dms_deleted_applications

        if dms_response.page_info.has_next_page:
            yield from self.get_deleted_applications(procedure_id, dms_response.page_info.end_cursor, deletedSince)

    def send_user_message(
        self, application_scalar_id: str, instructeur_techid: str, body: str, with_correction: bool = False
    ) -> Any:
        variables = {"input": {"dossierId": application_scalar_id, "instructeurId": instructeur_techid, "body": body}}
        if with_correction:
            variables["input"]["correction"] = "incorrect"
        try:
            return self.execute_query(SEND_USER_MESSAGE_QUERY_NAME, variables)
        except gql_exceptions.TransportQueryError as exc:
            raise exceptions.DmsGraphQLApiError(exc.errors)
        except requests_exception.RequestException as exc:
            # DS unavailability does not need to be notified as an error in Sentry
            logger.warning(
                "[DMS] Connection error when sending user message",
                extra={"application_scalar_id": application_scalar_id},
            )
            raise exceptions.DmsGraphQLAPIConnectError(str(exc))
        except Exception:
            logger.exception(
                "DMS : unexpected error when sending message", extra={"application_scalar_id": application_scalar_id}
            )
            raise exceptions.DmsGraphQLApiException()

    def _execute_mutation(
        self,
        mutation_name: str,
        *,
        key: str,
        log_state: str,
        application_techid: str,
        instructeur_techid: str,
        motivation: str | None = None,
        disable_notification: bool | None = False,
    ) -> dict:
        params: dict[str, str | bool] = {
            "dossierId": application_techid,
            "instructeurId": instructeur_techid,
        }
        if disable_notification is not None:
            params["disableNotification"] = disable_notification
        if motivation is not None:
            params["motivation"] = motivation

        try:
            response = self.execute_query(mutation_name, variables={"input": params})
        except gql_exceptions.TransportQueryError as exc:
            raise exceptions.DmsGraphQLApiError(exc.errors)
        except requests_exception.RequestException as exc:
            # DS unavailability does not need to be notified as an error in Sentry
            logger.warning(
                "[DMS] Connection error when marking %s", log_state, extra={"application_techid": application_techid}
            )
            raise exceptions.DmsGraphQLAPIConnectError(str(exc))
        except Exception:
            logger.exception(
                "[DMS] Unexpected error when marking %s", log_state, extra={"application_techid": application_techid}
            )
            raise exceptions.DmsGraphQLApiException()
        data = response[key]
        errors = data["errors"]
        if errors:
            logger.error(
                "[DMS] Error while marking application %s %s",
                log_state,
                errors,
                extra={"application_techid": application_techid},
            )
            raise exceptions.DmsGraphQLApiError(errors)

        return data["dossier"]

    def make_on_going(
        self,
        application_techid: str,
        instructeur_techid: str,
        disable_notification: bool = False,
        raise_if_already_ongoing: bool = False,
    ) -> dict:
        try:
            return self._execute_mutation(
                MAKE_ON_GOING_MUTATION_NAME,
                key="dossierPasserEnInstruction",
                log_state="on going",
                application_techid=application_techid,
                instructeur_techid=instructeur_techid,
                disable_notification=disable_notification,
            )
        except exceptions.DmsGraphQLApiError as exc:
            if raise_if_already_ongoing is False and exc.message == "Le dossier est déjà en instruction":
                return {}
            raise

    def make_accepted(
        self,
        application_techid: str,
        instructeur_techid: str,
        *,
        motivation: str | None = None,
        disable_notification: bool = False,
        from_draft: bool = False,
    ) -> dict:
        if from_draft:
            # Can be accepted only when on_going ("en instruction")
            self.make_on_going(application_techid, instructeur_techid, disable_notification=True)
        return self._execute_mutation(
            MAKE_ACCEPTED_MUTATION_NAME,
            key="dossierAccepter",
            log_state="accepted",
            application_techid=application_techid,
            instructeur_techid=instructeur_techid,
            motivation=motivation,
            disable_notification=disable_notification,
        )

    def make_refused(
        self,
        application_techid: str,
        instructeur_techid: str,
        motivation: str,
        *,
        disable_notification: bool = False,
        from_draft: bool = False,
    ) -> dict:
        try:
            if from_draft:
                # Can be refused only when on_going ("en instruction")
                self.make_on_going(application_techid, instructeur_techid, disable_notification=True)
            return self._execute_mutation(
                MAKE_REFUSED_MUTATION_NAME,
                key="dossierRefuser",
                log_state="rejected",
                application_techid=application_techid,
                instructeur_techid=instructeur_techid,
                motivation=motivation,
                disable_notification=disable_notification,
            )
        except exceptions.DmsGraphQLApiError as exc:
            if exc.message == "Le dossier est déjà refusé":
                return {}
            raise

    def mark_without_continuation(
        self,
        application_techid: str,
        instructeur_techid: str,
        motivation: str | None,
        *,
        disable_notification: bool = False,
        from_draft: bool = False,
    ) -> Any:
        if from_draft:
            # Can be processed only when on_going ("en instruction")
            self.make_on_going(application_techid, instructeur_techid, disable_notification=True)
        return self._execute_mutation(
            MARK_WITHOUT_CONTINUATION_MUTATION_NAME,
            key="dossierClasserSansSuite",
            log_state="without continuation",
            application_techid=application_techid,
            instructeur_techid=instructeur_techid,
            motivation=motivation,
            disable_notification=disable_notification,
        )

    def archive_application(self, application_techid: str, instructeur_techid: str) -> Any:
        return self._execute_mutation(
            ARCHIVE_APPLICATION_QUERY_NAME,
            key="dossierArchiver",
            log_state="archive",
            application_techid=application_techid,
            instructeur_techid=instructeur_techid,
            disable_notification=None,
        )

    def get_single_application_details(self, application_number: int) -> dms_models.DmsApplicationResponse:
        response = self.execute_query(
            GET_SINGLE_APPLICATION_QUERY_NAME, variables={"applicationNumber": application_number}
        )

        return dms_models.DmsApplicationResponse(**response["dossier"])

    def get_bank_info_status(self, dossier_id: int) -> dict:
        variables = {"dossierNumber": dossier_id}
        return self.execute_query(GET_BANK_INFO_STATUS_QUERY_NAME, variables=variables)

    def update_text_annotation(self, dossier_id: str, instructeur_id: str, annotation_id: str, value: str) -> dict:
        variables = {
            "input": {
                "dossierId": dossier_id,
                "instructeurId": instructeur_id,
                "annotationId": annotation_id,
                "value": value,
            }
        }
        return self.execute_query(UPDATE_TEXT_ANNOTATION_QUERY_NAME, variables=variables)

    def add_label_to_application(self, application_techid: str, label_techid: str) -> None:
        params: dict[str, str] = {
            "dossierId": application_techid,
            "labelId": label_techid,
        }

        try:
            response = self.execute_query(ADD_LABEL, variables={"input": params})
        except gql_exceptions.TransportQueryError as exc:
            raise exceptions.DmsGraphQLApiError(exc.errors)
        except requests_exception.RequestException as exc:
            # DS unavailability does not need to be notified as an error in Sentry
            logger.warning(
                "[DMS] Connection error when adding label to application",
                extra={"application_techid": application_techid, "label_techid": label_techid},
            )
            raise exceptions.DmsGraphQLAPIConnectError(str(exc))
        except Exception as exc:
            logger.warning(
                "[DMS] Unexpected error while adding label to application",
                extra={"application_techid": application_techid, "label_techid": label_techid, "exc": exc},
            )
            raise exceptions.DmsGraphQLApiException()

        data = response["dossierAjouterLabel"]
        errors = data["errors"]
        if errors:
            if len(errors) == 1 and errors[0]["message"] == "Ce label est déjà associé au dossier":
                return
            logger.warning(
                "[DMS] Error while adding label to application: %s",
                errors,
                extra={"application_techid": application_techid, "label_techid": label_techid},
            )
            raise exceptions.DmsGraphQLApiError(errors)

    def get_pro_bank_nodes_states(
        self,
        *,
        procedure_number: int,
        state: dms_models.GraphQLApplicationStates | None = None,
        since: datetime.datetime | None = None,
        page_token: str | None = None,
        archived: bool = False,
    ) -> Generator[dict, None, None]:
        variables: dict[str, int | str] = {
            "demarcheNumber": procedure_number,
            "archived": archived,
        }
        if state:
            variables["state"] = state.value
        if since:
            variables["since"] = since.isoformat()
        if page_token:
            variables["after"] = page_token
        results = self.execute_query(GET_BANK_INFO_APPLICATIONS_QUERY_NAME, variables=variables)
        dossiers = results["demarche"]["dossiers"]
        nodes = dossiers["nodes"]
        logger.info(
            "[DS] Found %s applications for procedure %d (page token: %s)",
            len(nodes),
            procedure_number,
            page_token,
        )
        yield from nodes

        if dossiers["pageInfo"]["hasNextPage"]:
            yield from self.get_pro_bank_nodes_states(
                procedure_number=procedure_number,
                state=state,
                since=since,
                page_token=dossiers["pageInfo"]["endCursor"],
            )

    def get_eac_nodes_siret_states(
        self,
        procedure_number: int,
        state: dms_models.GraphQLApplicationStates | None = None,
        since: datetime.datetime | None = None,
        page_token: str | None = None,
    ) -> Generator[dict, None, None]:
        variables: dict[str, int | str] = {
            "demarcheNumber": procedure_number,
        }
        if state:
            variables["state"] = state.value
        if since:
            variables["since"] = since.isoformat()
        if page_token:
            variables["after"] = page_token
        results = self.execute_query(GET_EAC_APPLICATIONS_STATE_SIRET, variables=variables)
        dossiers = results["demarche"]["dossiers"]
        nodes = dossiers["nodes"]
        logger.info(
            "[DMS] Found %s applications for procedure %d (page token :%s)",
            len(nodes),
            procedure_number,
            page_token,
        )
        yield from nodes

        if dossiers["pageInfo"]["hasNextPage"]:
            yield from self.get_eac_nodes_siret_states(
                procedure_number=procedure_number,
                since=since,
                state=state,
                page_token=dossiers["pageInfo"]["endCursor"],
            )

    def get_beneficiary_account_update_nodes(
        self,
        *,
        procedure_number: int,
        state: dms_models.GraphQLApplicationStates | None = None,
        since: datetime.datetime | None = None,
        page_token: str | None = None,
    ) -> Generator[dict, None, None]:
        variables: dict[str, int | str] = {"demarcheNumber": procedure_number}
        if state:
            variables["state"] = state.value
        if since:
            variables["since"] = since.isoformat()
        if page_token:
            variables["after"] = page_token
        results = self.execute_query(GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables=variables)
        dossiers = results["demarche"]["dossiers"]
        nodes = dossiers["nodes"]
        logger.info(
            "[DS] Found %s applications for procedure %d (page token: %s)",
            len(nodes),
            procedure_number,
            page_token,
        )
        yield from nodes

        if dossiers["pageInfo"]["hasNextPage"]:
            yield from self.get_beneficiary_account_update_nodes(
                procedure_number=procedure_number,
                state=state,
                since=since,
                page_token=dossiers["pageInfo"]["endCursor"],
            )

    def get_instructors(self, *, procedure_number: int) -> dict[str, str]:
        variables: dict[str, int | str] = {
            "demarcheNumber": procedure_number,
        }
        results = self.execute_query(GET_INSTRUCTORS_QUERY_NAME, variables=variables)
        groups = results["demarche"]["groupeInstructeurs"]

        instructor_ids_by_email = {}
        for group in groups:
            for item in group["instructeurs"]:
                instructor_ids_by_email[item["email"]] = item["id"]

        return instructor_ids_by_email


def get_dms_stats(dms_application_id: int | None, api_v4: bool = False) -> DmsStats | None:
    if not dms_application_id:
        return None

    try:
        dms_stats = DMSGraphQLClient(retries=1).get_bank_info_status(dms_application_id)
    except gql_exceptions.TransportQueryError as exc:
        raise exceptions.DmsGraphQLApiError(exc.errors)
    except (gql_exceptions.TransportError, urllib3.exceptions.HTTPError, requests_exception.RequestException) as exc:
        raise exceptions.DmsGraphQLAPIConnectError(str(exc))

    dossier = dms_stats["dossier"]
    state = dossier["state"]
    match state:
        # Be careful, "dateDerniereModification" is updated when the "dossier" is archived; this update should not be
        # considered as the validation date
        case "en_construction":
            date_field = "datePassageEnConstruction"
        case "en_instruction":
            date_field = "datePassageEnInstruction"
        case "accepte" | "refuse" | "sans_suite":
            date_field = "dateTraitement"
        case _:
            # This case should never happen except if a new state is added in GraphQL schema
            # https://www.demarches-simplifiees.fr/graphql/schema/dossierstate.doc.html
            date_field = "dateDerniereModification"

    if api_v4:
        api_url = f"https://www.demarches-simplifiees.fr/procedures/{settings.DMS_VENUE_PROCEDURE_ID_V4}/dossiers/{dms_application_id}"
    else:
        api_url = f"https://www.demarches-simplifiees.fr/procedures/{settings.DS_BANK_ACCOUNT_PROCEDURE_ID}/dossiers/{dms_application_id}"

    return DmsStats(
        status=state,
        subscriptionDate=datetime.datetime.fromisoformat(dossier["dateDepot"]),
        lastChangeDate=datetime.datetime.fromisoformat(dossier[date_field]),
        url=api_url,
    )


def update_demarches_simplifiees_text_annotations(dossier_id: str, annotation_id: str, message: str) -> None:
    client = DMSGraphQLClient()
    result = client.update_text_annotation(dossier_id, settings.DMS_INSTRUCTOR_ID, annotation_id, message)
    errors = result["dossierModifierAnnotationText"].get("errors")
    if errors:
        logger.error(
            "Got error when updating DMS annotation",
            extra={
                "errors": errors,
                "dossier": dossier_id,
            },
        )
