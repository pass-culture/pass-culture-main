import logging
import traceback

from pydantic import parse_obj_as

from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational import exceptions
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.adage_backends.serialize import AdageEducationalInstitution
from pcapi.routes.adage.v1.serialization import collective_offer_request
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import requests


logger = logging.getLogger(__name__)
STATUS_CODE_FOR_INSTITUTION_WITHOUT_EMAIL = 404
ERROR_CODE_FOR_INSTITUTION_WITHOUT_EMAIL = "EMAIL_ADDRESS_DOES_NOT_EXIST"


def is_adage_institution_without_email(api_response: requests.Response) -> bool:
    return (
        api_response.status_code == STATUS_CODE_FOR_INSTITUTION_WITHOUT_EMAIL
        and dict(api_response.json()).get("detail") == ERROR_CODE_FOR_INSTITUTION_WITHOUT_EMAIL
    )


class AdageHttpClient(AdageClient):
    def __init__(self) -> None:
        self.api_key = settings.ADAGE_API_KEY
        self.header_key = "X-omogen-api-key"
        super().__init__()

    def notify_prebooking(self, data: prebooking.EducationalBookingResponse) -> None:
        api_url = f"{self.base_url}/v1/prereservation"
        try:
            api_response = requests.post(
                api_url,
                headers={self.header_key: self.api_key, "Content-Type": "application/json"},
                data=data.json(),
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code != 201 and not is_adage_institution_without_email(api_response):
            raise exceptions.AdageException(
                "Error posting new prebooking to Adage API.", api_response.status_code, api_response.text
            )

    def notify_offer_or_stock_edition(self, data: prebooking.EducationalBookingEdition) -> None:
        api_url = f"{self.base_url}/v1/prereservation-edit"
        try:
            api_response = requests.post(
                api_url,
                headers={self.header_key: self.api_key, "Content-Type": "application/json"},
                data=data.json(),
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code != 201:
            raise exceptions.AdageException(
                "Error posting booking edition notification to Adage API.",
                api_response.status_code,
                api_response.text,
            )

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        api_url = f"{self.base_url}/v1/partenaire-culturel/{siren}"

        try:
            api_response = requests.get(
                api_url,
                headers={self.header_key: self.api_key},
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code == 404:
            raise exceptions.CulturalPartnerNotFoundException(
                "Requested siren is not a known cultural partner for Adage"
            )
        if api_response.status_code != 200:
            raise exceptions.AdageException("Error getting Adage API", api_response.status_code, api_response.text)

        return parse_obj_as(list[AdageVenue], api_response.json())

    def notify_booking_cancellation_by_offerer(self, data: prebooking.EducationalBookingResponse) -> None:
        api_url = f"{self.base_url}/v1/prereservation-annule"
        try:
            api_response = requests.post(
                api_url,
                headers={self.header_key: self.api_key, "Content-Type": "application/json"},
                data=data.json(),
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code != 201:
            raise exceptions.AdageException(
                "Error posting booking cancellation by offerer notification to Adage API.",
                api_response.status_code,
                api_response.text,
            )

    def get_cultural_partners(self) -> list[dict[str, str | int | float | None]]:
        api_url = f"{self.base_url}/v1/partenaire-culturel"
        try:
            api_response = requests.get(
                api_url,
                headers={self.header_key: self.api_key},
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code == 404:
            raise exceptions.CulturalPartnerNotFoundException("Requested cultural partners not found for Adage")
        if api_response.status_code != 200:
            raise exceptions.AdageException("Error getting Adage API", api_response.status_code, api_response.text)

        return api_response.json()

    def notify_institution_association(self, data: AdageCollectiveOffer) -> None:
        api_url = f"{self.base_url}/v1/offre-assoc"
        try:
            api_response = requests.post(
                api_url, headers={self.header_key: self.api_key, "Content-Type": "application/json"}, data=data.json()
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code != 201 and not is_adage_institution_without_email(api_response):
            raise exceptions.AdageException("Error getting Adage API", api_response.status_code, api_response.text)

    def get_cultural_partner(self, siret: str) -> venues_serialize.AdageCulturalPartner:
        api_url = f"{self.base_url}/v1/etablissement-culturel/{siret}"
        try:
            api_response = requests.get(
                api_url,
                headers={self.header_key: self.api_key},
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code == 404:
            raise exceptions.CulturalPartnerNotFoundException("Requested cultural partner not found for Adage")
        if api_response.status_code != 200:
            raise exceptions.AdageException("Error getting Adage API", api_response.status_code, api_response.text)

        response_content = api_response.json()

        if len(response_content) == 0:
            raise exceptions.CulturalPartnerNotFoundException("Requested cultural partner not found for Adage")

        return parse_obj_as(venues_serialize.AdageCulturalPartner, response_content[0])

    def get_adage_educational_institutions(self, ansco: str) -> list[AdageEducationalInstitution]:
        template_url = f"{self.base_url}/v1/etablissement-scolaire?ansco={ansco}&page=%s"
        page = 1
        institutions = []
        while True:
            api_url = template_url % page
            api_response = requests.get(
                api_url,
                headers={self.header_key: self.api_key},
            )

            if api_response.status_code == 404:
                raise exceptions.CulturalPartnerNotFoundException(
                    "Requested Ansco is not a known cultural partner for Adage"
                )
            if api_response.status_code != 200:
                raise exceptions.AdageException("Error getting Adage API", api_response.status_code, api_response.text)

            response_json = api_response.json().get("etablissements", [])
            if not response_json:
                break

            institutions.extend(response_json)
            page += 1

        return parse_obj_as(list[AdageEducationalInstitution], institutions)

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        api_url = f"{self.base_url}/v1/redacteurs-projets/{uai}"
        try:
            api_response = requests.get(
                api_url,
                headers={self.header_key: self.api_key},
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code == 404:
            raise exceptions.EducationalRedactorNotFound("Requested UAI not found")
        if api_response.status_code != 200:
            raise exceptions.AdageException("Error getting Adage API", api_response.status_code, api_response.text)

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

    def notify_collective_request_to_cultural_partner(
        self, data: collective_offer_request.CollectiveOfferRequestResponse
    ) -> None:
        api_url = f"{self.base_url}/v1/offer-request-received"
        try:
            api_response = requests.post(
                api_url,
                headers={self.header_key: self.api_key, "Content-Type": "application/json"},
                data=data.json(),
            )
        except ConnectionError as exp:
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            raise exceptions.AdageException(
                status_code=502,
                response_text="Connection Error",
                message="Cannot establish connection to omogen api",
            ) from exp

        if api_response.status_code != 201:
            raise exceptions.AdageException(
                "Error posting booking cancellation by offerer notification to Adage API.",
                api_response.status_code,
                api_response.text,
            )
