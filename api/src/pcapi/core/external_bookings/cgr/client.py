import datetime
import logging

from pcapi.connectors.cgr.cgr import annulation_pass_culture
from pcapi.connectors.cgr.cgr import get_seances_pass_culture
from pcapi.connectors.cgr.cgr import reservation_pass_culture
from pcapi.connectors.serialization import cgr_serializers
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.core.providers.repository import get_cgr_cinema_details
import pcapi.core.users.models as users_models
from pcapi.utils.queue import add_to_queue


logger = logging.getLogger(__name__)


class CGRClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_id: str):
        self.cinema_id = cinema_id
        self.cgr_cinema_details = get_cgr_cinema_details(cinema_id)

    def get_films(self) -> list[cgr_serializers.Film]:
        response = get_seances_pass_culture(self.cgr_cinema_details)
        return response.ObjetRetour.Films

    def get_film_showtimes_stocks(self, film_id: int) -> dict[int, int]:
        response = get_seances_pass_culture(self.cgr_cinema_details, allocine_film_id=film_id)
        return {show.IDSeance: show.NbPlacesRestantes for show in response.ObjetRetour.Films[0].Seances}

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
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
        response = reservation_pass_culture(self.cgr_cinema_details, book_show_body)
        logger.info("Booked CGR Ticket", extra={"barcode": response.QrCode, "seat_number": response.Placement})
        add_to_queue(
            REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": response.QrCode,
                "venue_id": booking.venueId,
                "timestamp": datetime.datetime.utcnow().timestamp(),
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
            annulation_pass_culture(self.cgr_cinema_details, barcode)
            logger.info("CGR Booking Cancelled", extra={"barcode": barcode})

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError
