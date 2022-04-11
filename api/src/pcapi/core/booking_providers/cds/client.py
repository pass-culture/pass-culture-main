from pydantic.tools import parse_obj_as

from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import get_resource
from pcapi.connectors.cine_digital_service import put_resource
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
from pcapi.core.booking_providers.cds.constants import PASS_CULTURE_PAYMENT_TYPE_CDS
from pcapi.core.booking_providers.cds.constants import PASS_CULTURE_TARIFF_LABEL_CDS
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions


class CineDigitalServiceAPI:
    def __init__(self, cinema_id: str, token: str, api_url: str):
        self.token = token
        self.api_url = api_url
        self.cinema_id = cinema_id

    def get_show(self, show_id: int) -> cds_serializers.ShowCDS:
        data = get_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.SHOWS)
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)
        for show in shows:
            if show.id == show_id:
                return show
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Show #{show_id} not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def get_payment_type(self) -> cds_serializers.PaymentTypeCDS:
        data = get_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.PAYMENT_TYPE)
        payment_types = parse_obj_as(list[cds_serializers.PaymentTypeCDS], data)
        for payment_type in payment_types:
            if payment_type.short_label == PASS_CULTURE_PAYMENT_TYPE_CDS:
                return payment_type

        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Pass Culture payment type not found in Cine Digital Service API for cinemaId={self.cinema_id}"
            f" & url={self.api_url}"
        )

    def get_tariff(self) -> cds_serializers.TariffCDS:
        data = get_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.TARIFFS)
        tariffs = parse_obj_as(list[cds_serializers.TariffCDS], data)

        for tariff in tariffs:
            if tariff.label == PASS_CULTURE_TARIFF_LABEL_CDS:
                return tariff
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Tariff Pass Culture not found in Cine Digital Service API for cinemaId={self.cinema_id}"
            f" & url={self.api_url}"
        )

    def get_screen(self, screen_id: int) -> cds_serializers.ScreenCDS:
        data = get_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.SCREENS)
        screens = parse_obj_as(list[cds_serializers.ScreenCDS], data)

        for screen in screens:
            if screen.id == screen_id:
                return screen
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Screen #{screen_id} not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def cancel_booking(self, barcodes: list[str], paiement_type_id: int) -> None:
        cancel_body = cds_serializers.CancelBookingCDS(barcodes=barcodes, paiementtypeid=paiement_type_id)
        api_response = put_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.CANCEL_BOOKING, cancel_body)

        if api_response:
            cancel_errors = parse_obj_as(cds_serializers.CancelBookingsErrorsCDS, api_response)
            sep = "\n"
            raise cds_exceptions.CineDigitalServiceAPIException(
                f"Error while canceling bookings :{sep}{sep.join([f'{barcode} : {error_msg}' for barcode, error_msg in cancel_errors.__root__.items()])}"
            )
