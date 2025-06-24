import datetime
import logging
import traceback
import typing

from pydantic.v1 import parse_obj_as

from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational import exceptions
from pcapi.core.educational import schemas as educational_schemas
from pcapi.core.educational.adage_backends import serialize
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.utils import requests


logger = logging.getLogger(__name__)

STATUS_CODE_FOR_INSTITUTION_WITHOUT_EMAIL = 404
ERROR_CODE_FOR_INSTITUTION_WITHOUT_EMAIL = "EMAIL_ADDRESS_DOES_NOT_EXIST"

# this is an SMTP error code forwarded to us by Adage
# this means an email was valid but an error occurred when the mail was sent
STATUS_CODE_FOR_INVALID_INSTITUTION_EMAIL = 450


def is_adage_institution_without_email(api_response: requests.Response) -> bool:
    return (
        api_response.status_code == STATUS_CODE_FOR_INSTITUTION_WITHOUT_EMAIL
        and dict(api_response.json()).get("detail") == ERROR_CODE_FOR_INSTITUTION_WITHOUT_EMAIL
    )


def is_adage_institution_email_invalid(api_response: requests.Response) -> bool:
    return api_response.status_code == STATUS_CODE_FOR_INVALID_INSTITUTION_EMAIL


class AdageHttpClient(AdageClient):
    def __init__(self) -> None:
        self.api_key = settings.ADAGE_API_KEY
        self.header_key = "X-omogen-api-key"
        super().__init__()

    @staticmethod
    def _get_api_adage_exception(
        api_response: requests.Response,
        message: str,
        exception_class: type[exceptions.AdageException] = exceptions.AdageException,
    ) -> exceptions.AdageException:
        try:
            json_response = api_response.json()
        except requests.exceptions.JSONDecodeError:
            return exceptions.AdageException(
                message=f"Error while reading Adage API json response - status code: {api_response.status_code}",
                status_code=api_response.status_code,
                response_text=api_response.text,
            )

        detail = dict(json_response).get("detail", "")

        full_message = f"{message} - status code: {api_response.status_code}"
        if detail:
            full_message = f"{full_message} - error code: {detail}"

        return exception_class(
            message=full_message, status_code=api_response.status_code, response_text=api_response.text
        )

    @staticmethod
    def _get_connection_error_adage_exception() -> exceptions.AdageException:
        return exceptions.AdageException(
            status_code=502,
            response_text="Connection Error",
            message="Cannot establish connection to omogen api",
        )

    def _make_get_request(self, url: str, params: dict[str, typing.Any] | None = None) -> requests.Response:
        try:
            api_response = requests.get(url=url, headers={self.header_key: self.api_key}, params=params)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())

            raise self._get_connection_error_adage_exception() from exp

        return api_response

    def _make_post_request(self, url: str, data: typing.Any | None = None) -> requests.Response:
        try:
            api_response = requests.post(
                url=url, headers={self.header_key: self.api_key, "Content-Type": "application/json"}, data=data
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())

            raise self._get_connection_error_adage_exception() from exp

        return api_response

    def notify_prebooking(self, data: educational_schemas.EducationalBookingResponse) -> None:
        api_response = self._make_post_request(url=f"{self.base_url}/v1/prereservation", data=data.json())

        if api_response.status_code != 201 and not is_adage_institution_without_email(api_response):
            raise self._get_api_adage_exception(api_response, "Error posting new prebooking to Adage API")

    def notify_offer_or_stock_edition(self, data: educational_schemas.EducationalBookingEdition) -> None:
        api_response = self._make_post_request(url=f"{self.base_url}/v1/prereservation-edit", data=data.json())

        if api_response.status_code != 201:
            raise self._get_api_adage_exception(api_response, "Error posting booking edition notification to Adage API")

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        api_response = self._make_get_request(url=f"{self.base_url}/v1/partenaire-culturel/{siren}")

        if api_response.status_code == 404:
            raise exceptions.CulturalPartnerNotFoundException(
                "Requested siren is not a known cultural partner for Adage"
            )
        if api_response.status_code != 200:
            raise self._get_api_adage_exception(api_response, "Error getting Adage API")

        return parse_obj_as(list[AdageVenue], api_response.json())

    def notify_booking_cancellation_by_offerer(self, data: educational_schemas.EducationalBookingResponse) -> None:
        api_response = self._make_post_request(url=f"{self.base_url}/v1/prereservation-annule", data=data.json())

        if api_response.status_code != 201:
            raise self._get_api_adage_exception(
                api_response, "Error posting booking cancellation by offerer notification to Adage API"
            )

    def get_cultural_partners(
        self, since_date: datetime.datetime | None = None
    ) -> list[dict[str, str | int | float | None]]:
        params = {}
        if since_date:
            params["dateModificationMin"] = since_date.strftime("%Y-%m-%d %H:%M:%S")

        api_response = self._make_get_request(url=f"{self.base_url}/v1/partenaire-culturel", params=params)

        if api_response.status_code == 404:
            raise exceptions.CulturalPartnerNotFoundException("Requested cultural partners not found for Adage")
        if api_response.status_code != 200:
            raise self._get_api_adage_exception(api_response, "Error getting Adage API")

        return api_response.json()

    def notify_institution_association(self, data: serialize.AdageCollectiveOffer) -> None:
        api_response = self._make_post_request(url=f"{self.base_url}/v1/offre-assoc", data=data.json())

        if api_response.status_code != 201:
            if is_adage_institution_email_invalid(api_response):
                logger.warning("Invalid email sent in adage offre-assoc call for offer %s", data.id)
                raise self._get_api_adage_exception(
                    api_response,
                    "Error getting Adage API because of invalid email",
                    exception_class=exceptions.AdageInvalidEmailException,
                )

            if not is_adage_institution_without_email(api_response):
                raise self._get_api_adage_exception(api_response, "Error getting Adage API")

    def get_cultural_partner(self, siret: str) -> educational_schemas.AdageCulturalPartner:
        api_response = self._make_get_request(url=f"{self.base_url}/v1/etablissement-culturel/{siret}")

        if api_response.status_code == 404:
            raise exceptions.CulturalPartnerNotFoundException("Requested cultural partner not found for Adage")
        if api_response.status_code != 200:
            raise self._get_api_adage_exception(api_response, "Error getting Adage API")

        response_content = api_response.json()

        if len(response_content) == 0:
            raise exceptions.CulturalPartnerNotFoundException("Requested cultural partner not found for Adage")

        return parse_obj_as(educational_schemas.AdageCulturalPartner, response_content[0])

    def get_adage_educational_institutions(self, ansco: str) -> list[serialize.AdageEducationalInstitution]:
        template_url = f"{self.base_url}/v1/etablissement-scolaire?ansco={ansco}&page=%s"
        page = 1
        institutions = []
        while True:
            api_response = self._make_get_request(url=template_url % page)

            if api_response.status_code == 404:
                raise exceptions.CulturalPartnerNotFoundException(
                    "Requested Ansco is not a known cultural partner for Adage"
                )
            if api_response.status_code != 200:
                raise self._get_api_adage_exception(api_response, "Error getting Adage API")

            response_json = api_response.json().get("etablissements", [])
            if not response_json:
                break

            institutions.extend(response_json)
            page += 1

        return parse_obj_as(list[serialize.AdageEducationalInstitution], institutions)

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        api_response = self._make_get_request(url=f"{self.base_url}/v1/redacteurs-projets/{uai}")

        if api_response.status_code == 404:
            raise exceptions.EducationalRedactorNotFound("Requested UAI not found")
        if api_response.status_code != 200:
            raise self._get_api_adage_exception(api_response, "Error getting Adage API")

        response_content = api_response.json()
        redactors = response_content.get("redacteurs", [])

        if not redactors:
            if redactors is None:
                # The attribute should not be present or it should be
                # a list. But it seems that we sometimes get `null`.
                logger.error(
                    "Got null list of redactors from Adage API /redacteurs-projets endpoint",
                    extra={
                        "response": api_response.content,
                    },
                )
            raise exceptions.EducationalRedactorNotFound("No educational redactor found for the given UAI")

        return redactors

    def notify_reimburse_collective_booking(self, data: educational_schemas.AdageReimbursementNotification) -> None:
        api_response = self._make_post_request(url=f"{self.base_url}/v1/reservation-remboursement", data=data.json())

        if api_response.status_code != 201:
            raise self._get_api_adage_exception(api_response, "Error getting Adage API")

    def notify_redactor_when_collective_request_is_made(self, data: serialize.AdageCollectiveRequest) -> None:
        api_response = self._make_post_request(url=f"{self.base_url}/v1/offre-vitrine", data=data.json())

        if api_response.status_code != 201 and not is_adage_institution_without_email(api_response):
            raise self._get_api_adage_exception(api_response, "Error getting Adage API")
