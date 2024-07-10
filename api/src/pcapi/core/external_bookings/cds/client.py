import datetime
from functools import lru_cache
import json
import logging
import math
from operator import attrgetter
import typing

from pydantic.v1.tools import parse_obj_as

from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import get_movie_poster_from_api
from pcapi.connectors.cine_digital_service import get_resource
from pcapi.connectors.cine_digital_service import post_resource
from pcapi.connectors.cine_digital_service import put_resource
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
from pcapi.core.bookings.constants import RedisExternalBookingType
import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.cds.constants as cds_constants
import pcapi.core.external_bookings.cds.exceptions as cds_exceptions
import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.core.external_bookings.models import Ticket
import pcapi.core.users.models as users_models
from pcapi.utils.queue import add_to_queue

from . import constants


logger = logging.getLogger(__name__)
CDS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


class CineDigitalServiceAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_id: str, account_id: str, api_url: str, cinema_api_token: str | None):
        super().__init__(cinema_id=cinema_id)
        if not cinema_api_token:
            raise ValueError(f"Missing token for {cinema_id}")
        self.token = cinema_api_token
        self.api_url = api_url
        self.account_id = account_id
        super()

    def get_film_showtimes_stocks(self, film_id: str) -> dict:
        return {}

    @lru_cache
    def get_internet_sale_gauge_active(self) -> bool:
        """
        lru_cache is a feature in Python that can significantly improve the performance of functions
        by caching their results based on their input arguments, thus avoiding costly recomputations.
        """
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.CINEMAS)
        cinemas = parse_obj_as(list[cds_serializers.CinemaCDS], data)
        for cinema in cinemas:
            if cinema.id == self.cinema_id:
                return cinema.is_internet_sale_gauge_active
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Cinema internet_sale_gauge_active not found in Cine Digital Service API "
            f"for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    @external_bookings_models.cache_external_call(
        key_template=constants.CDS_SHOWTIMES_STOCKS_CACHE_KEY, expire=cds_constants.CDS_SHOWTIMES_STOCKS_CACHE_TIMEOUT
    )
    def get_shows_remaining_places(self, show_ids: list[int]) -> str:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SHOWS)
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)
        if self.get_internet_sale_gauge_active():
            return json.dumps({show.id: show.internet_remaining_place for show in shows if show.id in show_ids})
        return json.dumps({show.id: show.remaining_place for show in shows if show.id in show_ids})

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

    def get_venue_movies(self) -> list[cds_serializers.MediaCDS]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.MEDIA)
        return parse_obj_as(list[cds_serializers.MediaCDS], data)

    def get_movie_poster(self, image_url: str) -> bytes:
        try:
            return get_movie_poster_from_api(image_url)
        except cds_exceptions.CineDigitalServiceAPIException:
            logger.info(
                "Could not fetch movie poster",
                extra={
                    "provider": "cds",
                    "url": image_url,
                },
            )
            return bytes()

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

    @lru_cache
    def get_pc_voucher_types(self) -> list[cds_serializers.VoucherTypeCDS]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.VOUCHER_TYPE)
        voucher_types = parse_obj_as(list[cds_serializers.VoucherTypeCDS], data)
        return [
            voucher_type
            for voucher_type in voucher_types
            if voucher_type.code == cds_constants.PASS_CULTURE_VOUCHER_CODE and voucher_type.tariff
        ]

    def get_screen(self, screen_id: int) -> cds_serializers.ScreenCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SCREENS)
        screens = parse_obj_as(list[cds_serializers.ScreenCDS], data)

        for screen in screens:
            if screen.id == screen_id:
                return screen
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Screen #{screen_id} not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    def get_hardcoded_seatmap(
        self,
        show: cds_serializers.ShowCDS,
    ) -> list[list[str | typing.Literal[0]]]:
        """Return a matrix (a list of lists) of values, where each
        value is a seat number as a string (e.g. "A7" or "123"), or
        zero as an integer when there is no seat.
        """
        cinema = self.get_cinema_infos()
        encoded_seatmap = None
        for parameter in cinema.cinema_parameters:
            if parameter.key == cds_constants.SEATMAP_HARDCODED_LABELS_SCREENID + str(show.screen.id):
                encoded_seatmap = parameter.value
        if not encoded_seatmap:
            return []
        seatmap = json.loads(encoded_seatmap)
        assert isinstance(seatmap, list)
        return seatmap

    def get_available_seat(
        self, show: cds_serializers.ShowCDS, screen: cds_serializers.ScreenCDS
    ) -> list[cds_serializers.SeatCDS]:
        seatmap = self.get_seatmap(show.id)
        available_seats_index = [
            (i, j) for i in range(0, seatmap.nb_row) for j in range(0, seatmap.nb_col) if seatmap.map[i][j] == 1
        ]
        if len(available_seats_index) == 0:
            return []
        best_seat = self._get_closest_seat_to_center((seatmap.nb_row // 2, seatmap.nb_col // 2), available_seats_index)

        hardcoded_seatmap = self.get_hardcoded_seatmap(show)
        return [cds_serializers.SeatCDS(best_seat, screen, seatmap, hardcoded_seatmap)]

    def get_available_duo_seat(
        self, show: cds_serializers.ShowCDS, screen: cds_serializers.ScreenCDS
    ) -> list[cds_serializers.SeatCDS]:
        seatmap = self.get_seatmap(show.id)
        seatmap_center = ((seatmap.nb_row - 1) / 2, (seatmap.nb_col - 1) / 2)

        available_seats_index = [
            (i, j) for i in range(0, seatmap.nb_row) for j in range(0, seatmap.nb_col) if seatmap.map[i][j] == 1
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

        hardcoded_seatmap = self.get_hardcoded_seatmap(show)

        return [
            cds_serializers.SeatCDS(first_seat, screen, seatmap, hardcoded_seatmap),
            cds_serializers.SeatCDS(second_seat, screen, seatmap, hardcoded_seatmap),
        ]

    def get_seatmap(self, show_id: int) -> cds_serializers.SeatmapCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.SEATMAP, {"show_id": show_id})
        seatmap_cds = parse_obj_as(cds_serializers.SeatmapCDS, data)
        return seatmap_cds

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

        cancel_body = cds_serializers.CancelBookingCDS(barcodes=barcodes_int, paiement_type_id=paiement_type_id)  # type: ignore[call-arg]
        api_response = put_resource(self.api_url, self.account_id, self.token, ResourceCDS.CANCEL_BOOKING, cancel_body)

        if api_response:
            cancel_errors = parse_obj_as(cds_serializers.CancelBookingsErrorsCDS, api_response)
            if {cds_constants.CDS_TICKET_ALREADY_CANCELED_ERROR_MESSAGE} == set(cancel_errors.__root__.values()):
                return  # We don't raise if the tickets have already been cancelled
            sep = "\n"
            raise cds_exceptions.CineDigitalServiceAPIException(
                f"Error while canceling bookings :{sep}{sep.join([f'{barcode} : {error_msg}' for barcode, error_msg in cancel_errors.__root__.items()])}"
            )

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[Ticket]:
        quantity = booking.quantity
        if quantity < 0 or quantity > 2:
            raise cds_exceptions.CineDigitalServiceAPIException(f"Booking quantity={quantity} should be 1 or 2")

        show = self.get_show(show_id)
        screen = self.get_screen(show.screen.id)
        show_voucher_type = self.get_voucher_type_for_show(show)
        if not show_voucher_type:
            raise cds_exceptions.CineDigitalServiceAPIException(f"Unavailable pass culture tariff for show={show.id}")

        ticket_sale_collection = self._create_ticket_sale_dict(show, quantity, screen, show_voucher_type)
        payement_collection = self._create_transaction_payment(quantity, show_voucher_type)

        create_transaction_body = cds_serializers.CreateTransactionBodyCDS(  # type: ignore[call-arg]
            cinema_id=self.cinema_id,
            is_cancelled=False,
            transaction_date=datetime.datetime.utcnow().strftime(CDS_DATE_FORMAT),
            ticket_sale_collection=ticket_sale_collection,
            payement_collection=payement_collection,
        )

        json_response = post_resource(
            self.api_url, self.account_id, self.token, ResourceCDS.CREATE_TRANSACTION, create_transaction_body
        )
        create_transaction_response = parse_obj_as(cds_serializers.CreateTransactionResponseCDS, json_response)

        for ticket in create_transaction_response.tickets:
            add_to_queue(
                REDIS_EXTERNAL_BOOKINGS_NAME,
                {
                    "barcode": ticket.barcode,
                    "venue_id": booking.venueId,
                    "timestamp": datetime.datetime.utcnow().timestamp(),
                    "booking_type": RedisExternalBookingType.CINEMA,
                },
            )

        booking_informations = [
            Ticket(barcode=ticket.barcode, seat_number=ticket.seat_number)
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
        if not show.is_disabled_seatmap and not show.is_empty_seatmap:
            seats_to_book = (
                self.get_available_seat(show, screen)
                if booking_quantity == 1
                else self.get_available_duo_seat(show, screen)
            )

            if not seats_to_book:
                raise cds_exceptions.CineDigitalServiceAPIException(f"Unavailable seats to book for show={show.id}")

        assert show_voucher_type.tariff

        ticket_sale_list = []
        for i in range(booking_quantity):
            ticket_sale = cds_serializers.TicketSaleCDS(  # type: ignore[call-arg]
                id=(i + 1) * -1,
                cinema_id=self.cinema_id,
                operation_date=datetime.datetime.utcnow().strftime(CDS_DATE_FORMAT),
                is_cancelled=False,
                seat_col=seats_to_book[i].seatCol if bool(seats_to_book) else None,
                seat_row=seats_to_book[i].seatRow if bool(seats_to_book) else None,
                seat_number=seats_to_book[i].seatNumber if bool(seats_to_book) else None,
                tariff=cds_serializers.IdObjectCDS(id=show_voucher_type.tariff.id),
                show=cds_serializers.IdObjectCDS(id=show.id),
                voucher_type=cds_constants.PASS_CULTURE_VOUCHER_CODE,
                disabled_person=False,
            )
            ticket_sale_list.append(ticket_sale)

        return ticket_sale_list

    def _create_transaction_payment(
        self, booking_quantity: int, show_voucher_type: cds_serializers.VoucherTypeCDS
    ) -> list[cds_serializers.TransactionPayementCDS]:
        payment_type = self.get_voucher_payment_type()

        assert show_voucher_type.tariff
        payement_collection = []
        for i in range(booking_quantity):
            payment = cds_serializers.TransactionPayementCDS(  # type: ignore[call-arg]
                id=(i + 1) * -1,
                amount=show_voucher_type.tariff.price,
                payement_type=cds_serializers.IdObjectCDS(id=payment_type.id),
                voucher_type=cds_serializers.IdObjectCDS(id=show_voucher_type.id),
            )
            payement_collection.append(payment)

        return payement_collection

    def get_voucher_type_for_show(self, show: cds_serializers.ShowCDS) -> cds_serializers.VoucherTypeCDS | None:
        pc_voucher_types = self.get_pc_voucher_types()

        show_pc_vouchers = []
        for show_tariff in show.shows_tariff_pos_type_collection:
            for voucher in pc_voucher_types:
                if voucher.tariff and show_tariff.tariff.id == voucher.tariff.id:
                    show_pc_vouchers.append(voucher)

        if not show_pc_vouchers:
            return None
        # In the normal case a show is associated to 0 or 1 pass culture tariff
        # It is possible that by mistake from CDS side several pass culture tariffs are associated with a show
        # In this case we take the tariff with the lower price
        min_price_voucher = min(show_pc_vouchers, key=attrgetter("tariff.price"))
        return min_price_voucher

    def get_cinema_infos(self) -> cds_serializers.CinemaCDS:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.CINEMAS)
        cinemas = parse_obj_as(list[cds_serializers.CinemaCDS], data)
        for cinema in cinemas:
            if cinema.id == self.cinema_id:
                return cinema
        raise cds_exceptions.CineDigitalServiceAPIException(
            f"Cinema not found in Cine Digital Service API " f"for cinemaId={self.cinema_id} & url={self.api_url}"
        )

    @lru_cache
    def get_media_options(self) -> dict[int, str]:
        data = get_resource(self.api_url, self.account_id, self.token, ResourceCDS.MEDIA_OPTIONS)
        media_options = parse_obj_as(list[cds_serializers.MediaOptionCDS], data)
        return {media_option.id: media_option.ticketlabel for media_option in media_options if media_option.ticketlabel}
