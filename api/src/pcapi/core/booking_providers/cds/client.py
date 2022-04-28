import math
from typing import Optional

from pydantic.tools import parse_obj_as

from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import get_resource
from pcapi.connectors.cine_digital_service import put_resource
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
from pcapi.core.booking_providers.cds.constants import PASS_CULTURE_PAYMENT_TYPE_CDS
from pcapi.core.booking_providers.cds.constants import PASS_CULTURE_TARIFF_LABEL_CDS
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.booking_providers.models import BookingProviderClientAPI
from pcapi.core.booking_providers.models import SeatCDS


class CineDigitalServiceAPI(BookingProviderClientAPI):
    def __init__(self, cinema_id: str, api_url: str, token: Optional[str]):
        if not token:
            raise ValueError(f"Missing token for {cinema_id}")
        super().__init__(cinema_id, api_url, token)

    def get_show_remaining_places(self, show_id: int) -> int:
        show = self.get_show(show_id)
        return show.internet_remaining_place

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

    def get_available_seat(self, show_id: int, screen: cds_serializers.ScreenCDS) -> Optional[SeatCDS]:
        seatmap = self.get_seatmap(show_id)
        available_seats_index = [
            (i, j) for i in range(0, seatmap.nb_row) for j in range(0, seatmap.nb_col) if seatmap.map[i][j] % 10 == 1
        ]
        if len(available_seats_index) == 0:
            return None
        best_seat = self._get_closest_seat_to_center((seatmap.nb_row / 2, seatmap.nb_col / 2), available_seats_index)
        return SeatCDS(best_seat, screen, seatmap)

    def get_available_duo_seat(self, show_id: int, screen: cds_serializers.ScreenCDS) -> list[SeatCDS]:
        seatmap = self.get_seatmap(show_id)
        seatmap_center = ((seatmap.nb_row - 1) / 2.0, (seatmap.nb_col - 1) / 2.0)

        available_seats_index = [
            (i, j) for i in range(0, seatmap.nb_row) for j in range(0, seatmap.nb_col) if seatmap.map[i][j] % 10 == 1
        ]
        if len(available_seats_index) <= 1:
            return []

        available_seats_for_duo = [
            seat for seat in available_seats_index if (seat[0], seat[1] + 1) in available_seats_index
        ]

        if len(available_seats_for_duo) > 0:
            first_seat = self._get_closest_seat_to_center(seatmap_center, available_seats_for_duo)
            second_seat = (first_seat[0], first_seat[1] + 1)
        else:
            first_seat = self._get_closest_seat_to_center(seatmap_center, available_seats_index)
            available_seats_index.remove(first_seat)
            second_seat = self._get_closest_seat_to_center(seatmap_center, available_seats_index)

        return [
            SeatCDS(first_seat, screen, seatmap),
            SeatCDS(second_seat, screen, seatmap),
        ]

    def get_seatmap(self, show_id: int) -> cds_serializers.SeatmapCDS:
        data = get_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.SEATMAP, {"show_id": show_id})
        return parse_obj_as(cds_serializers.SeatmapCDS, data)

    def _get_closest_seat_to_center(
        self, center: tuple[int, int], seats_index: list[tuple[int, int]]
    ) -> tuple[int, int]:
        distances_to_center = list(
            map(
                lambda seat_index: math.sqrt(pow(seat_index[0] - center[0], 2) + pow(seat_index[1] - center[1], 2)),
                seats_index,
            )
        )
        min_distance = min(distances_to_center)
        index_min_distance = distances_to_center.index(min_distance)
        return seats_index[index_min_distance]

    def cancel_booking(self, barcodes: list[str]) -> None:
        paiement_type_id = self.get_payment_type().id
        cancel_body = cds_serializers.CancelBookingCDS(barcodes=barcodes, paiementtypeid=paiement_type_id)
        api_response = put_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.CANCEL_BOOKING, cancel_body)

        if api_response:
            cancel_errors = parse_obj_as(cds_serializers.CancelBookingsErrorsCDS, api_response)
            sep = "\n"
            raise cds_exceptions.CineDigitalServiceAPIException(
                f"Error while canceling bookings :{sep}{sep.join([f'{barcode} : {error_msg}' for barcode, error_msg in cancel_errors.__root__.items()])}"
            )

    def create_booking(self) -> None:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")
