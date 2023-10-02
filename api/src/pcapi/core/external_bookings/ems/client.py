import logging

from pcapi.connectors.ems import EMSBookingConnector
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.bookings import models as booking_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.external_bookings import models as external_bookings_models
from pcapi.core.external_bookings.exceptions import ExternalBookingSoldOutError
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


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
            pass_culture_price=booking.amount,  # type: ignore [arg-type]
            total_price=booking.total_amount,  # type: ignore [arg-type]
            email=beneficiary.email,
            num_pass_culture=str(beneficiary.id),
        )
        response = self.connector.do_request(self.connector.booking_endpoint, payload=payload.dict())
        self.connector.raise_for_status(response)

        content = ems_serializers.ReservationPassCultureResponse(**response.json())
        return [
            external_bookings_models.Ticket(
                barcode=ticket.code_barre,
                seat_number=ticket.num_place,
                additional_information={
                    "num_cine": content.num_cine,
                    "num_caisse": ticket.num_caisse,
                    "num_trans": ticket.num_trans,
                    "num_ope": ticket.num_ope,
                },
            )
            for ticket in content.billets
        ]

    def cancel_booking(self, barcodes: list[str]) -> None:
        external_bookings = bookings_repository.get_external_bookings_by_cinema_id_and_barcodes(
            self.cinema_id, barcodes
        )
        for booking in external_bookings:
            assert booking.additional_information is not None
            payload = ems_serializers.AnnulationPassCultureRequest(
                num_cine=booking.additional_information["num_cine"],
                num_caisse=booking.additional_information["num_caisse"],
                num_trans=booking.additional_information["num_trans"],
                num_ope=booking.additional_information["num_ope"],
            )
            response = self.connector.do_request(self.connector.cancelation_endpoint, payload=payload.dict())
            self.connector.raise_for_status(response)

            logger.info("Successfully canceled an EMS external booking", extra={"barcode": booking.barcode})

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError()

    def get_film_showtimes_stocks(self, film_id: str) -> dict[int, int]:
        payload = ems_serializers.AvailableShowsRequest(num_cine=self.cinema_id, id_film=film_id)
        response = self.connector.do_request(self.connector.shows_availability_endpoint, payload.dict())
        try:
            self.connector.raise_for_status(response)
        except ExternalBookingSoldOutError:
            # Showtimes stocks are sold out, Stock.quantity will be updated to dnBookedQuantity
            # in `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
            return {}

        available_shows = ems_serializers.AvailableShowsResponse(**response.json())

        # We use a fake value for remaining places because we don't have access to real remaining places for EMS shows
        # This value will not impact quantity, seen that we update showtime quantity only if remaining places is 0 or 1.
        return {int(show): self.EMS_FAKE_REMAINING_PLACES for show in available_shows.seances}
