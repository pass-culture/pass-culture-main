import datetime
import math
from operator import attrgetter

from pydantic.tools import parse_obj_as

from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import get_movie_poster_from_api
from pcapi.connectors.cine_digital_service import get_resource
from pcapi.connectors.cine_digital_service import post_resource
from pcapi.connectors.cine_digital_service import put_resource
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
import pcapi.core.booking_providers.cds.constants as cds_constants
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
import pcapi.core.booking_providers.models as booking_providers_models


CDS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


class CineDigitalServiceAPI(booking_providers_models.BookingProviderClientAPI):
    def __init__(self, cinema_id: str, account_id: str, api_url: str, cinema_api_token: str | None):
        if not cinema_api_token:
            raise ValueError(f"Missing token for {cinema_id}")
        super().__init__(cinema_id, account_id, api_url, cinema_api_token)

    def get_internet_sale_gauge_active(self) -> bool:
        data = get_resource(self.api_url, self.cinema_id, self.token, ResourceCDS.CINEMAS)
        cinemas = parse_obj_as(list[cds_serializers.CinemasCDS], data)
        for cinema in cinemas:
            if cinema.id == self.cinema_id:
                return cinema.is_internet_sale_gauge_active
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Cinema internet_sale_gauge_active not found in Cine Digital Service API "
            f"for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def get_show_remaining_places(self, show_id: int) -> int:
        show = self.get_show(show_id)
        internet_sale_gauge_active = self.get_internet_sale_gauge_active()
        if internet_sale_gauge_active:
            return show.internet_remaining_place
        return show.remaining_place

    def get_shows_remaining_places(self, show_ids: list[int]) -> dict[int, int]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SHOWS)
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)
        if self.get_internet_sale_gauge_active():
            return {show.id: show.internet_remaining_place for show in shows if show.id in show_ids}
        return {show.id: show.remaining_place for show in shows if show.id in show_ids}

    def get_shows(self) -> list[cds_serializers.ShowCDS]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SHOWS)
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)
        if shows:
            return shows

        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Shows not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def get_show(self, show_id: int) -> cds_serializers.ShowCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SHOWS)
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)
        for show in shows:
            if show.id == show_id:
                return show
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Show #{show_id} not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def get_venue_movies(self) -> list[booking_providers_models.Movie]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.MEDIA)
        cds_movies = parse_obj_as(list[cds_serializers.MediaCDS], data)
        return [cds_movie.to_generic_movie() for cds_movie in cds_movies]

    def get_movie_poster(self, image_url: str) -> bytes:
        return get_movie_poster_from_api(image_url)

    def get_voucher_payment_type(self) -> cds_serializers.PaymentTypeCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.PAYMENT_TYPE)
        payment_types = parse_obj_as(list[cds_serializers.PaymentTypeCDS], data)
        for payment_type in payment_types:
            if payment_type.internal_code == cds_constants.VOUCHER_PAYMENT_TYPE_CDS:
                return payment_type

        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Pass Culture payment type not found in Cine Digital Service API for cinemaId={self.cinema_id}"
            f" & url={self.api_url}"
        )

    def get_pc_voucher_types(self) -> list[cds_serializers.VoucherTypeCDS]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.VOUCHER_TYPE)
        voucher_types = parse_obj_as(list[cds_serializers.VoucherTypeCDS], data)
        return [
            voucher_type
            for voucher_type in voucher_types
            if voucher_type.code == cds_constants.PASS_CULTURE_VOUCHER_CODE and voucher_type.tariff
        ]

    def get_tariff(self) -> cds_serializers.TariffCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.TARIFFS)
        tariffs = parse_obj_as(list[cds_serializers.TariffCDS], data)

        for tariff in tariffs:
            if tariff.label == cds_constants.PASS_CULTURE_TARIFF_LABEL_CDS:
                return tariff
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Tariff Pass Culture not found in Cine Digital Service API for cinemaId={self.cinema_id}"
            f" & url={self.api_url}"
        )

    def get_screen(self, screen_id: int) -> cds_serializers.ScreenCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SCREENS)
        screens = parse_obj_as(list[cds_serializers.ScreenCDS], data)

        for screen in screens:
            if screen.id == screen_id:
                return screen
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Screen #{screen_id} not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def get_available_seat(self, show_id: int, screen: cds_serializers.ScreenCDS) -> list[cds_serializers.SeatCDS]:
        seatmap = self.get_seatmap(show_id)
        available_seats_index = [
            (i, j) for i in range(0, seatmap.nb_row) for j in range(0, seatmap.nb_col) if seatmap.map[i][j] % 10 == 1
        ]
        if len(available_seats_index) == 0:
            return []
        best_seat = self._get_closest_seat_to_center((seatmap.nb_row // 2, seatmap.nb_col // 2), available_seats_index)
        return [cds_serializers.SeatCDS(best_seat, screen, seatmap)]

    def get_available_duo_seat(self, show_id: int, screen: cds_serializers.ScreenCDS) -> list[cds_serializers.SeatCDS]:
        seatmap = self.get_seatmap(show_id)
        seatmap_center = ((seatmap.nb_row - 1) / 2, (seatmap.nb_col - 1) / 2)

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
            cds_serializers.SeatCDS(first_seat, screen, seatmap),
            cds_serializers.SeatCDS(second_seat, screen, seatmap),
        ]

    def get_seatmap(self, show_id: int) -> booking_providers_models.SeatMap:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SEATMAP, {"show_id": show_id})
        seatmap_cds = parse_obj_as(cds_serializers.SeatmapCDS, data)
        return booking_providers_models.SeatMap(seatmap_cds.map)

    def _get_closest_seat_to_center(
        self, center: tuple[float, float], seats_index: list[tuple[int, int]]
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
        paiement_type_id = self.get_voucher_payment_type().id
        barcodes_int: list[int] = []
        for barcode in barcodes:
            if not barcode.isdigit():
                raise ValueError(f"Barcode {barcode} contains one or more invalid char (only digit allowed)")
            barcodes_int.append(int(barcode))

        cancel_body = cds_serializers.CancelBookingCDS(barcodes=barcodes_int, paiementtypeid=paiement_type_id)
        api_response = put_resource(self.api_url, self.account_id, self.token, ResourceCDS.CANCEL_BOOKING, cancel_body)

        if api_response:
            cancel_errors = parse_obj_as(cds_serializers.CancelBookingsErrorsCDS, api_response)
            sep = "\n"
            raise cds_exceptions.CineDigitalServiceAPIException(
                f"Error while canceling bookings :{sep}{sep.join([f'{barcode} : {error_msg}' for barcode, error_msg in cancel_errors.__root__.items()])}"
            )

    def book_ticket(self, show_id: int, quantity: int) -> list[booking_providers_models.Ticket]:
        if quantity < 0 or quantity > 2:
            raise cds_exceptions.CineDigitalServiceAPIException(f"Booking quantity={quantity} should be 1 or 2")

        show = self.get_show(show_id)
        screen = self.get_screen(show.screen.id)
        show_voucher_type = self.get_voucher_type_for_show(show)
        if not show_voucher_type:
            raise cds_exceptions.CineDigitalServiceAPIException(f"Unavailable pass culture tariff for show={show.id}")

        ticket_sale_collection = self._create_ticket_sale_dict(show, quantity, screen, show_voucher_type)
        payment = self._create_transaction_payment(show_voucher_type)

        create_transaction_body = cds_serializers.CreateTransactionBodyCDS(
            cinema_id=self.cinema_id,
            is_cancelled=False,
            transaction_date=datetime.datetime.utcnow().strftime(CDS_DATE_FORMAT),
            ticket_sale_collection=ticket_sale_collection,
            payement_collection=[payment],
        )

        json_response = post_resource(
            self.api_url, self.account_id, self.token, ResourceCDS.CREATE_TRANSACTION, create_transaction_body
        )
        create_transaction_response = parse_obj_as(cds_serializers.CreateTransactionResponseCDS, json_response)

        booking_informations = [
            booking_providers_models.Ticket(barcode=ticket.barcode, seat_number=ticket.seat_number)
            for ticket in create_transaction_response.tickets
        ]
        return booking_informations

    def _create_ticket_sale_dict(
        self,
        show: cds_serializers.ShowCDS,
        booking_quantity: int,
        screen: cds_serializers.ScreenCDS,
        show_voucher_type: cds_serializers.VoucherTypeCDS,
    ) -> list[cds_serializers.TicketSaleCDS]:
        seats_to_book = []
        if not show.is_disabled_seatmap:
            seats_to_book = (
                self.get_available_seat(show.id, screen)
                if booking_quantity == 1
                else self.get_available_duo_seat(show.id, screen)
            )

            if not seats_to_book:
                raise cds_exceptions.CineDigitalServiceAPIException(f"Unavailable seats to book for show={show.id}")

        ticket_sale_list = []
        for i in range(booking_quantity):
            ticket_sale = cds_serializers.TicketSaleCDS(
                id=(i + 1) * -1,
                cinema_id=self.cinema_id,
                operation_date=datetime.datetime.utcnow().strftime(CDS_DATE_FORMAT),
                is_cancelled=False,
                seat_col=seats_to_book[i].seatCol if not show.is_disabled_seatmap else None,
                seat_row=seats_to_book[i].seatRow if not show.is_disabled_seatmap else None,
                seat_number=seats_to_book[i].seatNumber if not show.is_disabled_seatmap else None,
                tariff=cds_serializers.IdObjectCDS(id=show_voucher_type.tariff.id),
                show=cds_serializers.IdObjectCDS(id=show.id),
                disabled_person=False,
            )
            ticket_sale_list.append(ticket_sale)

        return ticket_sale_list

    def _create_transaction_payment(
        self, show_voucher_type: cds_serializers.VoucherTypeCDS
    ) -> cds_serializers.TransactionPayementCDS:
        payment_type = self.get_voucher_payment_type()

        return cds_serializers.TransactionPayementCDS(
            id=-1,
            amount=0,
            payement_type=cds_serializers.IdObjectCDS(id=payment_type.id),
            voucher_type=cds_serializers.IdObjectCDS(id=show_voucher_type.id),
        )

    def get_voucher_type_for_show(self, show: cds_serializers.ShowCDS) -> cds_serializers.VoucherTypeCDS | None:
        pc_voucher_types = self.get_pc_voucher_types()

        show_pc_vouchers = []
        for show_tariff in show.shows_tariff_pos_type_collection:
            for voucher in pc_voucher_types:
                if show_tariff.tariff.id == voucher.tariff.id:
                    show_pc_vouchers.append(voucher)

        if not show_pc_vouchers:
            return None
        # In the normal case a show is associated to 0 or 1 pass culture tariff
        # It is possible that by mistake from CDS side several pass culture tariffs are associated with a show
        # In this case we take the tariff with the lower price
        min_price_voucher = min(show_pc_vouchers, key=attrgetter("tariff.price"))
        return min_price_voucher
