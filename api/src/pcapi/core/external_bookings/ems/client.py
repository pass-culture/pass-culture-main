from pcapi.connectors.ems import EMSBookingConnector
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.bookings import models as booking_models
from pcapi.core.external_bookings import models as external_bookings_models
from pcapi.core.users import models as users_models


class EMSClientAPI(external_bookings_models.ExternalBookingsClientAPI):
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

    def get_film_showtimes_stocks(self, film_id: int) -> dict[int, int]:
        raise NotImplementedError()
