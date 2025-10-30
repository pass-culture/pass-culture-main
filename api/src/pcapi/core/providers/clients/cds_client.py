import json
import logging
import math
import typing
from functools import lru_cache
from operator import attrgetter

from pydantic.v1.tools import parse_obj_as

import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
from pcapi.core.bookings.constants import RedisExternalBookingType
from pcapi.core.external_bookings.decorators import catch_cinema_provider_request_timeout
from pcapi.core.providers.clients import cinema_client
from pcapi.utils import date as date_utils
from pcapi.utils import requests
from pcapi.utils.queue import add_to_queue

from . import cds_serializers


logger = logging.getLogger(__name__)

CDS_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
PASS_CULTURE_VOUCHER_CODE = "PSCULTURE"
VOUCHER_PAYMENT_TYPE_CDS = "VCH"
SEATMAP_HARDCODED_LABELS_SCREENID = "SEATMAP_HARDCODED_LABELS_SCREENID_"
CDS_TICKET_ALREADY_CANCELED_ERROR_MESSAGE = "TICKET_ALREADY_CANCELED"


class CineDigitalServiceAPIException(external_bookings_exceptions.ExternalBookingException):
    pass


def _log_external_call(
    client: cinema_client.CinemaAPIClient,
    method: str,
    response: dict | list[dict] | list,
) -> None:
    client_name = client.__class__.__name__
    cinema_id = client.cinema_id
    logger.debug(
        "[CINEMA] Call to external API",
        extra={"api_client": client_name, "cinema_id": cinema_id, "method": method, "response": response},
    )


def _extract_reason_from_response(response: requests.Response) -> str:
    # from requests.Response.raise_for_status()
    reason = response.reason

    if isinstance(reason, bytes):
        try:
            reason = reason.decode("utf-8")
        except UnicodeDecodeError:
            reason = reason.decode("iso-8859-1")

    return reason


def _raise_for_status(response: requests.Response, cinema_api_token: str | None, request_detail: str) -> None:
    """
    Raise `CineDigitalServiceAPIException` is status >= 400
    """
    if response.status_code >= 400:
        reason = _extract_reason_from_response(response)
        if cinema_api_token:
            reason = reason.replace(cinema_api_token, "")  # filter out token
        raise CineDigitalServiceAPIException(f"Error on CDS API on {request_detail} : {reason}")


class CineDigitalServiceAPIClient(cinema_client.CinemaAPIClient):
    def __init__(
        self,
        cinema_id: str,
        account_id: str,
        cinema_api_token: str | None,
        *,
        request_timeout: int | None = None,
    ):
        super().__init__(cinema_id=cinema_id, request_timeout=request_timeout)
        if not cinema_api_token:
            raise ValueError(f"Missing token for {cinema_id}")
        self.token = cinema_api_token
        self.base_url = f"https://{account_id}.{settings.CDS_API_URL}"

    def _authenticated_get(self, url: str) -> dict:
        """
        Make an authenticated GET by adding an `api_token` in query params

        This method logs response at debug level.

        :raise: CineDigitalServiceAPIException
        """
        response = requests.get(url, params={"api_token": self.token}, timeout=self.request_timeout)
        _raise_for_status(response, self.token, f"GET {url}")
        data = response.json()

        _log_external_call(self, method=f"GET {url}", response=data)

        return data

    def _authenticated_put(self, url: str, payload: dict) -> dict | list[dict] | list | None:
        """
        Make an authenticated PUT by adding an `api_token` in query params.

        If an error occurred, it returns the JSON body explaining the error.

        :raise: CineDigitalServiceAPIException
        """
        response = requests.put(
            url,
            params={"api_token": self.token},
            headers={"Content-Type": "application/json"},
            data=payload,
            timeout=self.request_timeout,
        )

        _raise_for_status(response, self.token, f"PUT {url}")

        response_headers = response.headers.get("Content-Type")

        if response_headers and "application/json" in response_headers:
            return response.json()

        return None

    def _authenticated_post(self, url: str, payload: str) -> dict | list[dict] | list | None:
        """
        Make an authenticated POST by adding an `api_token` in query params.

        :raise: CineDigitalServiceAPIException
        """
        response = requests.post(
            url,
            params={"api_token": self.token},
            headers={"Content-Type": "application/json"},
            data=payload,
            timeout=self.request_timeout,
        )

        _raise_for_status(response, self.token, f"POST {url}")

        return response.json()

    def get_film_showtimes_stocks(self, film_id: str) -> dict:
        return {}

    @lru_cache
    def get_internet_sale_gauge_active(self) -> bool:
        """
        lru_cache is a feature in Python that can significantly improve the performance of functions
        by caching their results based on their input arguments, thus avoiding costly recomputations.
        """
        data = self._authenticated_get(f"{self.base_url}cinemas")
        cinemas = parse_obj_as(list[cds_serializers.CinemaCDS], data)
        for cinema in cinemas:
            if cinema.id == self.cinema_id:
                return cinema.is_internet_sale_gauge_active
        raise CineDigitalServiceAPIException(
            f"Cinema internet_sale_gauge_active not found in Cine Digital Service API "
            f"for cinemaId={self.cinema_id} & url={self.base_url}"
        )

    def get_shows(self) -> list[cds_serializers.ShowCDS]:
        data = self._authenticated_get(f"{self.base_url}shows")
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)

        if not shows:
            logger.warning("[CDS] Api call returned no show", extra={"cinemaId": self.cinema_id, "url": self.base_url})

        return shows

    def get_show(self, show_id: int) -> cds_serializers.ShowCDS:
        """
        Fetch all shows and filter them using `show_id`

        :raise: `ExternalBookingShowDoesNotExistError` if no show has the given `show_id`
        """
        data = self._authenticated_get(f"{self.base_url}shows")
        shows = parse_obj_as(list[cds_serializers.ShowCDS], data)
        for show in shows:
            if show.id == show_id:
                return show
        raise external_bookings_exceptions.ExternalBookingShowDoesNotExistError()

    def get_venue_movies(self) -> list[cds_serializers.MediaCDS]:
        data = self._authenticated_get(f"{self.base_url}media")
        return parse_obj_as(list[cds_serializers.MediaCDS], data)

    def get_rating(self) -> dict:  # method used by BO to check authentication is working
        return self._authenticated_get(f"{self.base_url}rating")

    def get_voucher_payment_type(self) -> cds_serializers.PaymentTypeCDS:
        data = self._authenticated_get(f"{self.base_url}paiementtype")
        payment_types = parse_obj_as(list[cds_serializers.PaymentTypeCDS], data)
        for payment_type in payment_types:
            if payment_type.internal_code == VOUCHER_PAYMENT_TYPE_CDS:
                return payment_type

        raise CineDigitalServiceAPIException(
            f"Pass Culture payment type not found in Cine Digital Service API for cinemaId={self.cinema_id}"
            f" & url={self.base_url}"
        )

    @lru_cache
    def get_pc_voucher_types(self) -> list[cds_serializers.VoucherTypeCDS]:
        data = self._authenticated_get(f"{self.base_url}vouchertype")
        voucher_types = parse_obj_as(list[cds_serializers.VoucherTypeCDS], data)
        return [
            voucher_type
            for voucher_type in voucher_types
            if voucher_type.code == PASS_CULTURE_VOUCHER_CODE and voucher_type.tariff
        ]

    def get_screen(self, screen_id: int) -> cds_serializers.ScreenCDS:
        data = self._authenticated_get(f"{self.base_url}screens")
        screens = parse_obj_as(list[cds_serializers.ScreenCDS], data)
        for screen in screens:
            if screen.id == screen_id:
                return screen
        raise CineDigitalServiceAPIException(
            f"Screen #{screen_id} not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.base_url}"
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
            if parameter.key == SEATMAP_HARDCODED_LABELS_SCREENID + str(show.screen.id):
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
        data = self._authenticated_get(f"{self.base_url}shows/{show_id}/seatmap")
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
        barcodes_cast_to_int: list[int] = []
        for barcode in barcodes:
            barcodes_cast_to_int.append(int(barcode))

        api_response = self._authenticated_put(
            f"{self.base_url}transaction/cancel",
            payload={"paiementtypeid": paiement_type_id, "barcodes": barcodes_cast_to_int},
        )

        if api_response:
            cancel_errors = parse_obj_as(cds_serializers.CancelBookingsErrorsCDS, api_response)
            if {CDS_TICKET_ALREADY_CANCELED_ERROR_MESSAGE} == set(cancel_errors.__root__.values()):
                return  # We don't raise if the tickets have already been cancelled
            sep = "\n"
            raise CineDigitalServiceAPIException(
                f"Error while canceling bookings :{sep}{sep.join([f'{barcode} : {error_msg}' for barcode, error_msg in cancel_errors.__root__.items()])}"
            )

    @catch_cinema_provider_request_timeout
    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[cinema_client.Ticket]:
        quantity = booking.quantity
        if quantity < 0 or quantity > 2:
            raise CineDigitalServiceAPIException(f"Booking quantity={quantity} should be 1 or 2")

        show = self.get_show(show_id)
        screen = self.get_screen(show.screen.id)
        show_voucher_type = self.get_voucher_type_for_show(show)
        if not show_voucher_type:
            raise CineDigitalServiceAPIException(f"Unavailable pass culture tariff for show={show.id}")

        ticket_sale_collection = self._create_ticket_sale_dict(show, quantity, screen, show_voucher_type)
        payement_collection = self._create_transaction_payment(quantity, show_voucher_type)

        create_transaction_body = cds_serializers.CreateTransactionBodyCDS(  # type: ignore[call-arg]
            cinema_id=self.cinema_id,
            is_cancelled=False,
            transaction_date=date_utils.get_naive_utc_now().strftime(CDS_DATE_FORMAT),
            ticket_sale_collection=ticket_sale_collection,
            payement_collection=payement_collection,
        ).json(by_alias=True)

        json_response = self._authenticated_post(f"{self.base_url}transaction/create", payload=create_transaction_body)

        create_transaction_response = parse_obj_as(cds_serializers.CreateTransactionResponseCDS, json_response)

        for ticket in create_transaction_response.tickets:
            add_to_queue(
                REDIS_EXTERNAL_BOOKINGS_NAME,
                {
                    "barcode": ticket.barcode,
                    "venue_id": booking.venueId,
                    "timestamp": date_utils.get_naive_utc_now().timestamp(),
                    "booking_type": RedisExternalBookingType.CINEMA,
                },
            )

        booking_informations = [
            cinema_client.Ticket(barcode=ticket.barcode, seat_number=ticket.seat_number)
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
                raise external_bookings_exceptions.ExternalBookingNotEnoughSeatsError(remainingQuantity=0)

        assert show_voucher_type.tariff

        ticket_sale_list = []
        for i in range(booking_quantity):
            ticket_sale = cds_serializers.TicketSaleCDS(  # type: ignore[call-arg]
                id=(i + 1) * -1,
                cinema_id=self.cinema_id,
                operation_date=date_utils.get_naive_utc_now().strftime(CDS_DATE_FORMAT),
                is_cancelled=False,
                seat_col=seats_to_book[i].seatCol if bool(seats_to_book) else None,
                seat_row=seats_to_book[i].seatRow if bool(seats_to_book) else None,
                seat_number=seats_to_book[i].seatNumber if bool(seats_to_book) else None,
                tariff=cds_serializers.IdObjectCDS(id=show_voucher_type.tariff.id),
                show=cds_serializers.IdObjectCDS(id=show.id),
                voucher_type=PASS_CULTURE_VOUCHER_CODE,
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

    # TODO: (tcoudray-pass, 14/10/25) Move this method in `CineDigitalServiceETLProcess`
    # when `CDSStocks` is removed
    def get_voucher_type_for_show(
        self,
        show: cds_serializers.ShowCDS,
        pc_voucher_types: list[cds_serializers.VoucherTypeCDS] | None = None,
    ) -> cds_serializers.VoucherTypeCDS | None:
        pc_voucher_types = pc_voucher_types or self.get_pc_voucher_types()

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
        data = self._authenticated_get(f"{self.base_url}cinemas")
        cinemas = parse_obj_as(list[cds_serializers.CinemaCDS], data)
        for cinema in cinemas:
            if cinema.id == self.cinema_id:
                return cinema
        raise CineDigitalServiceAPIException(
            f"Cinema not found in Cine Digital Service API for cinemaId={self.cinema_id} & url={self.base_url}"
        )

    @lru_cache
    def get_media_options(self) -> dict[int, str]:
        data = self._authenticated_get(f"{self.base_url}mediaoptions")
        media_options = parse_obj_as(list[cds_serializers.MediaOptionCDS], data)
        return {media_option.id: media_option.ticketlabel for media_option in media_options if media_option.ticketlabel}
