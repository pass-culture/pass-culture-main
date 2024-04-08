import logging
import traceback
import typing

from pydantic.v1 import parse_obj_as

from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational import exceptions
from pcapi.core.educational.adage_backends import serialize
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class AdageHttpClient(AdageClient):
    def __init__(self) -> None:
        super().__init__()
        self.api_key = settings.ADAGE_API_KEY
        self.header_key = "X-omogen-api-key"

    @staticmethod
    def _request(
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: typing.Any = None,
    ) -> requests.Response:
        methods = {
            "GET": requests.get,
            "POST": requests.post,
        }
        try:
            response = methods[method](url, headers=headers, params=params, data=data)  # type: ignore
        except ConnectionError as exc:
            # TODO: use logger.error or logger.critical instead of logger.info ?
            logger.info("could not connect to adage, error: %s", traceback.format_exc())
            msg = "Cannot establish connection to omogen api"
            raise exceptions.AdageException(msg, 502, "Connection Error") from exc
        return response

    def _request_get(
        self,
        url: str,
        msg_404: str,
        exc_404: typing.Type[Exception] = exceptions.CulturalPartnerNotFoundException,
        params: dict | None = None,
    ) -> requests.Response:
        headers = {self.header_key: self.api_key}
        response = self._request("GET", url, headers=headers, params=params)
        status_code = response.status_code
        if status_code == 404:
            raise exc_404(msg_404)
        if status_code != 200:
            msg = "Error getting Adage API"
            raise exceptions.AdageException(msg, status_code, response.text)
        return response

    def _request_post(
        self,
        url: str,
        data: typing.Any,
        ko_msg: str = "Error getting Adage API",
        check_email: bool = False,
    ) -> requests.Response:
        headers = {self.header_key: self.api_key, "Content-Type": "application/json"}
        response = self._request("POST", url, headers=headers, data=data.json())
        status_code = response.status_code
        if check_email:
            detail_msg = "EMAIL_ADDRESS_DOES_NOT_EXIST"
            cond = not (status_code == 404 and dict(response.json()).get("detail") == detail_msg)
        else:
            cond = True
        if status_code != 201 and cond:
            raise exceptions.AdageException(ko_msg, status_code, response.text)
        return response

    def notify_prebooking(self, data: prebooking.EducationalBookingResponse) -> None:
        url = f"{self.base_url}/v1/prereservation"
        ko_msg = "Error posting new prebooking to Adage API."
        self._request_post(url, data, ko_msg=ko_msg, check_email=True)

    def notify_offer_or_stock_edition(self, data: prebooking.EducationalBookingEdition) -> None:
        url = f"{self.base_url}/v1/prereservation-edit"
        ko_msg = "Error posting booking edition notification to Adage API."
        self._request_post(url, data, ko_msg=ko_msg)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        url = f"{self.base_url}/v1/partenaire-culturel/{siren}"
        msg_404 = "Requested siren is not a known cultural partner for Adage"
        response = self._request_get(url, msg_404)
        return parse_obj_as(list[AdageVenue], response.json())

    def notify_booking_cancellation_by_offerer(self, data: prebooking.EducationalBookingResponse) -> None:
        url = f"{self.base_url}/v1/prereservation-annule"
        ko_msg = "Error posting booking cancellation by offerer notification to Adage API."
        self._request_post(url, data, ko_msg=ko_msg)

    def get_cultural_partners(self, timestamp: int | None = None) -> list[dict[str, str | int | float | None]]:
        url = f"{self.base_url}/v1/partenaire-culturel"
        msg_404 = "Requested cultural partners not found for Adage"
        params = {}
        if timestamp:
            params["dateModificationMin"] = timestamp
        response = self._request_get(url, msg_404, params=params)
        return response.json()

    def notify_institution_association(self, data: serialize.AdageCollectiveOffer) -> None:
        url = f"{self.base_url}/v1/offre-assoc"
        self._request_post(url, data, check_email=True)

    def get_cultural_partner(self, siret: str) -> venues_serialize.AdageCulturalPartner:
        url = f"{self.base_url}/v1/etablissement-culturel/{siret}"
        msg_404 = "Requested cultural partner not found for Adage"
        response = self._request_get(url, msg_404)
        response_json = response.json()
        if not response_json:
            msg = "Requested cultural partner not found for Adage"
            raise exceptions.CulturalPartnerNotFoundException(msg)
        return parse_obj_as(venues_serialize.AdageCulturalPartner, response_json[0])

    def get_adage_educational_institutions(self, ansco: str) -> list[serialize.AdageEducationalInstitution]:
        template_url = f"{self.base_url}/v1/etablissement-scolaire?ansco={ansco}&page=%s"
        page = 1
        institutions = []
        while True:
            url = template_url % page
            msg_404 = "Requested Ansco is not a known cultural partner for Adage"
            response = self._request_get(url, msg_404)
            response_json = response.json().get("etablissements", [])
            if not response_json:
                break
            institutions.extend(response_json)
            page += 1

        return parse_obj_as(list[serialize.AdageEducationalInstitution], institutions)

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        url = f"{self.base_url}/v1/redacteurs-projets/{uai}"
        msg_404 = "Requested UAI not found"
        exc_404 = exceptions.EducationalRedactorNotFound
        response = self._request_get(url, msg_404, exc_404=exc_404)
        response_json = response.json()
        redactors = response_json.get("redacteurs", [])
        if redactors is None:
            # The attribute should not be present, or it should be a list.
            # But it seems that we sometimes get `null`.
            logger.error(
                "Got null list of redactors from Adage API /redacteurs-projets endpoint",
                extra={
                    "response": response.content,
                },
            )
        if not redactors:
            msg = "No educational redactor found for the given UAI"
            raise exceptions.EducationalRedactorNotFound(msg)

        return redactors

    def notify_reimburse_collective_booking(self, data: prebooking.AdageReimbursementNotification) -> None:
        url = f"{self.base_url}/v1/reservation-remboursement"
        self._request_post(url, data)

    def notify_redactor_when_collective_request_is_made(self, data: serialize.AdageCollectiveRequest) -> None:
        url = f"{self.base_url}/v1/offre-vitrine"
        self._request_post(url, data, check_email=True)
