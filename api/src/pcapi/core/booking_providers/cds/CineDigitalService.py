from pcapi.connectors.cine_digital_service import get_payment_types
from pcapi.connectors.cine_digital_service import get_shows
from pcapi.connectors.cine_digital_service import get_tariffs
from pcapi.connectors.serialization.cine_digital_service_serializers import PaymentTypeCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import TariffCDS
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions


class CineDigitalServiceAPI:
    def __init__(self, cinemaid: str, token: str, apiUrl: str):
        self.token = token
        self.apiUrl = apiUrl
        self.cinemaid = cinemaid

    def get_show(self, show_id: int) -> ShowCDS:
        shows = get_shows(self.cinemaid, self.apiUrl, self.token)
        for show in shows:
            if show.id == show_id:
                return show
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Show #{show_id} not found in Cine Digital Service API for cinemaId={self.cinemaid} & url={self.apiUrl}"
        )

    def get_payment_type(self) -> PaymentTypeCDS:
        payment_types = get_payment_types(self.cinemaid, self.apiUrl, self.token)
        for payment_type in payment_types:
            if payment_type.short_label == "PASSCULTURE":
                return payment_type

        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Pass Culture payment type not found in Cine Digital Service API for cinemaId={self.cinemaid}"
            f" & url={self.apiUrl}"
        )

    def get_tariff(self) -> TariffCDS:
        tariffs = get_tariffs(self.cinemaid, self.apiUrl, self.token)
        for tariff in tariffs:
            if tariff.label == "Pass Culture 5€":
                return tariff
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Tariff Pass Culture not found in Cine Digital Service API for cinemaId={self.cinemaid}"
            f" & url={self.apiUrl}"
        )
