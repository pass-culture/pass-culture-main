import datetime
import json
import logging

import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.users.models as users_models
from pcapi.connectors.cgr.cgr import annulation_pass_culture
from pcapi.connectors.cgr.cgr import get_seances_pass_culture
from pcapi.connectors.cgr.cgr import reservation_pass_culture
from pcapi.connectors.serialization import cgr_serializers
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
from pcapi.core.bookings.constants import RedisExternalBookingType
from pcapi.core.providers.repository import get_cgr_cinema_details
from pcapi.utils.queue import add_to_queue

from . import constants


logger = logging.getLogger(__name__)


class CGRClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_id: str, request_timeout: None | int = None):
        super().__init__(cinema_id=cinema_id, request_timeout=request_timeout)
        self.cgr_cinema_details = get_cgr_cinema_details(cinema_id)

    def get_films(self) -> list[cgr_serializers.Film]:
        logger.info("Fetching CGR movies", extra={"cinema_id": self.cinema_id})
        response = get_seances_pass_culture(self.cgr_cinema_details)
        return response.ObjetRetour.Films

    @external_bookings_models.cache_external_call(
        key_template=constants.CGR_SHOWTIMES_STOCKS_CACHE_KEY, expire=constants.CGR_SHOWTIMES_STOCKS_CACHE_TIMEOUT
    )
    def get_film_showtimes_stocks(self, film_id: str) -> str:
        logger.info("Fetching CGR showtimes", extra={"cinema_id": self.cinema_id})
        response = get_seances_pass_culture(
            self.cgr_cinema_details,
            allocine_film_id=int(film_id),
            request_timeout=self.request_timeout,
        )

        try:
            film = response.ObjetRetour.Films[0]
        except IndexError:
            # Showtimes stocks are sold out, Stock.quantity will be updated to dnBookedQuantity
            # in `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
            return json.dumps({})
        return json.dumps({show.IDSeance: show.NbPlacesRestantes for show in film.Seances})

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        logger.info(
            "Booking CGR external ticket",
            extra={"show_id": show_id, "cinema_id": self.cinema_id, "booking_token": booking.token},
        )
        assert booking.cancellationLimitDate  # for typing; a movie screening is always an event
        book_show_body = cgr_serializers.ReservationPassCultureBody(
            pIDSeances=show_id,
            pNumCinema=self.cgr_cinema_details.numCinema,
            pPUTTC=booking.amount,
            pNBPlaces=booking.quantity,
            pNom=beneficiary.lastName if beneficiary.lastName else "",
            pPrenom=beneficiary.firstName if beneficiary.firstName else "",
            pEmail=beneficiary.email,
            pToken=booking.token,
            pDateLimiteAnnul=booking.cancellationLimitDate.isoformat(),
        )
        response = reservation_pass_culture(
            self.cgr_cinema_details,
            book_show_body,
            request_timeout=self.request_timeout,
        )
        logger.info(
            "Booked CGR Ticket",
            extra={
                "barcode": response.QrCode,
                "seat_number": response.Placement,
                "booking_id": booking.id,
                "booking_token": booking.token,
            },
        )
        add_to_queue(
            REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": response.QrCode,
                "venue_id": booking.venueId,
                "timestamp": datetime.datetime.utcnow().timestamp(),
                "booking_type": RedisExternalBookingType.CINEMA,
            },
        )
        if booking.quantity == 2:
            tickets = [
                external_bookings_models.Ticket(
                    barcode=response.QrCode,
                    seat_number=response.Placement.split(",")[0] if "," in response.Placement else None,
                ),
                external_bookings_models.Ticket(
                    barcode=response.QrCode,
                    seat_number=response.Placement.split(",")[1] if "," in response.Placement else None,
                ),
            ]
        else:
            tickets = [
                external_bookings_models.Ticket(
                    barcode=response.QrCode, seat_number=response.Placement if response.Placement else None
                )
            ]
        return tickets

    def cancel_booking(self, barcodes: list[str]) -> None:
        barcodes_set = set(barcodes)
        for barcode in barcodes_set:
            logger.info("Cancelling CGR external booking", extra={"barcode": barcode, "cinema_id": self.cinema_id})
            annulation_pass_culture(self.cgr_cinema_details, barcode, request_timeout=self.request_timeout)
            logger.info("CGR Booking Cancelled", extra={"barcode": barcode})

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[str, int]:
        raise NotImplementedError
