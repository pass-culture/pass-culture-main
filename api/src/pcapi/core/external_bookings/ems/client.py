from pcapi.connectors.ems import EMSBookingConnector
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.bookings import models as booking_models
from pcapi.core.external_bookings import models as external_bookings_models
from pcapi.core.users import models as users_models


class EMSClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    EMS_FAKE_REMAINING_PLACES = 100

    def __init__(self, cinema_id: str):
        self.connector = EMSBookingConnector()
        self.cinema_id = cinema_id

    def book_ticket(
        self, show_id: int, booking: booking_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        payload = ems_serializers.ReservationPassCultureRequest(
            num_cine=self.cinema_id,
            id_seance=str(show_id),
            qte_place=booking.quantity,
            pass_culture_price=booking.amount,
            total_price=booking.total_amount,
            email=beneficiary.email,
            num_pass_culture=str(beneficiary.id),
        )
        response = self.connector.do_request(self.connector.booking_endpoint, payload=payload.dict())
        self.connector.raise_for_status(response)

        content = ems_serializers.ReservationPassCultureResponse(**response.json())
        return [
            external_bookings_models.Ticket(barcode=ticket.code_barre, seat_number=ticket.num_place)
            for ticket in content.billets
        ]

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError()

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError()

    def get_film_showtimes_stocks(self, film_id: str) -> dict[int, int]:
        payload = ems_serializers.AvailableShowsRequest(num_cine=self.cinema_id, id_film=film_id)
        response = self.connector.do_request(self.connector.shows_availability_endpoint, payload.dict())
        self.connector.raise_for_status(response)

        available_shows = ems_serializers.AvailableShowsResponse(**response.json())

        # We use a fake value for remaining places because we don't have access to real remaining places for EMS shows
        # This value will not impact quantity, seen that we update showtime quantity only if remaining places is 0 or 1.
        return {int(show): self.EMS_FAKE_REMAINING_PLACES for show in available_shows.seances}
