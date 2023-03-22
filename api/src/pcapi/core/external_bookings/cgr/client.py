import logging

from pcapi.connectors.cgr.cgr import get_seances_pass_culture
from pcapi.connectors.cgr.cgr import reservation_pass_culture
from pcapi.connectors.serialization import cgr_serializers
import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.core.providers.repository import get_cgr_cinema_details
import pcapi.core.users.models as users_models


logger = logging.getLogger(__name__)


class CGRClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_id: str):
        self.cinema_id = cinema_id
        self.cgr_cinema_details = get_cgr_cinema_details(cinema_id)

    def get_films(self) -> list[cgr_serializers.Film]:
        response = get_seances_pass_culture(self.cgr_cinema_details)
        return response.ObjetRetour.Films

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        book_show_body = cgr_serializers.ReservationPassCultureBody(
            pIDSeances=show_id,
            pNumCinema=self.cgr_cinema_details.numCinema,
            pPUTTC=booking.amount,
            pNBPlaces=booking.quantity,
            pNom=beneficiary.lastName if beneficiary.lastName else "",
            pPrenom=beneficiary.firstName if beneficiary.firstName else "",
            pEmail=beneficiary.email,
            pToken=booking.token,
        )
        response = reservation_pass_culture(self.cgr_cinema_details, book_show_body)
        logger.info("Booked CGR Ticket", extra={"barcode": response.QrCode, "seat_number": response.Placement})
        if booking.quantity == 2:
            tickets = [
                external_bookings_models.Ticket(barcode=response.QrCode, seat_number=response.Placement.split(",")[0]),
                external_bookings_models.Ticket(barcode=response.QrCode, seat_number=response.Placement.split(",")[1]),
            ]
        else:
            tickets = [external_bookings_models.Ticket(barcode=response.QrCode, seat_number=response.Placement)]
        return tickets

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError
