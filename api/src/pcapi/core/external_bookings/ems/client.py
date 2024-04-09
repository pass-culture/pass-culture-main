import datetime
import json
import logging

from flask import current_app

from pcapi.connectors.ems import EMSBookingConnector
from pcapi.connectors.serialization import ems_serializers
from pcapi.core.bookings import models as booking_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.external_bookings import models as external_bookings_models
from pcapi.core.external_bookings.exceptions import ExternalBookingSoldOutError
from pcapi.core.users import models as users_models
from pcapi.models.feature import FeatureToggle
from pcapi.utils.requests import exceptions as requests_exception

from . import constants


logger = logging.getLogger(__name__)


class EMSClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    EMS_FAKE_REMAINING_PLACES = 100

    def __init__(self, cinema_id: str):
        super().__init__(cinema_id=cinema_id)
        self.connector = EMSBookingConnector()

    def get_ticket(self, token: str) -> list[external_bookings_models.Ticket]:
        payload = ems_serializers.GetTicketRequest(num_cine=self.cinema_id, num_cmde=token)
        response = self.connector.do_request(self.connector.get_ticket_endpoint, payload=payload.dict())
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

    def book_ticket(
        self, show_id: int, booking: booking_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        payload = ems_serializers.ReservationPassCultureRequest(
            num_cine=self.cinema_id,
            id_seance=str(show_id),
            qte_place=booking.quantity,
            pass_culture_price=float(booking.amount),
            total_price=float(booking.total_amount),
            email=beneficiary.email,
            num_pass_culture=str(beneficiary.id),
            num_cmde=booking.token,
        )
        try:
            response = self.connector.do_request(self.connector.booking_endpoint, payload=payload.dict())
        except (requests_exception.ReadTimeout, requests_exception.Timeout):
            if FeatureToggle.EMS_CANCEL_PENDING_EXTERNAL_BOOKING.is_active():
                booking_to_cancel = json.dumps(
                    {
                        "cinema_id": self.cinema_id,
                        "token": booking.token,
                        "timestamp": datetime.datetime.utcnow().timestamp(),
                    }
                )

                current_app.redis_client.lpush(constants.EMS_EXTERNAL_BOOKINGS_TO_CANCEL, booking_to_cancel)
            raise

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
        # It appears we only need one metadata about one external_booking to cancel them all
        # Even if metadata are not the same across external_bookings of a same booking. Yes.
        external_booking = external_bookings[0]
        assert external_booking.additional_information is not None
        payload = ems_serializers.AnnulationPassCultureRequest(
            num_cine=external_booking.additional_information["num_cine"],
            num_caisse=external_booking.additional_information["num_caisse"],
            num_trans=external_booking.additional_information["num_trans"],
            num_ope=external_booking.additional_information["num_ope"],
        )
        response = self.connector.do_request(self.connector.cancelation_endpoint, payload=payload.dict())
        self.connector.raise_for_status(response)

        logger.info(
            "Successfully canceled an EMS external bookings",
            extra={"barcodes": [external_booking.barcode for external_booking in external_bookings]},
        )

    def cancel_booking_with_tickets(self, tickets: list[external_bookings_models.Ticket]) -> None:
        # There's no partial cancelling and only one ticket is enough to cancel a duo booking
        ticket = tickets[0]
        assert ticket.additional_information  # helps mypy, additional_information shouldn't be None at this point
        payload = ems_serializers.AnnulationPassCultureRequest(
            num_cine=self.cinema_id,
            num_caisse=ticket.additional_information["num_caisse"],
            num_trans=ticket.additional_information["num_trans"],
            num_ope=ticket.additional_information["num_ope"],
        )
        response = self.connector.do_request(self.connector.cancelation_endpoint, payload=payload.dict())
        self.connector.raise_for_status(response)

        logger.info(
            "Successfully canceled an EMS external bookings after failing booking",
            extra={"barcodes": [ticket.barcode for ticket in tickets]},
        )

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[str, int]:
        raise NotImplementedError()

    @external_bookings_models.cache_external_call(
        key_template=constants.EMS_SHOWTIMES_STOCKS_CACHE_KEY, expire=constants.EMS_SHOWTIMES_STOCKS_CACHE_TIMEOUT
    )
    def get_film_showtimes_stocks(self, film_id: str) -> str:
        payload = ems_serializers.AvailableShowsRequest(num_cine=self.cinema_id, id_film=film_id)
        response = self.connector.do_request(self.connector.shows_availability_endpoint, payload.dict())
        try:
            self.connector.raise_for_status(response)
        except ExternalBookingSoldOutError:
            # Showtimes stocks are sold out, Stock.quantity will be updated to dnBookedQuantity
            # in `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
            return json.dumps({})

        available_shows = ems_serializers.AvailableShowsResponse(**response.json())

        # We use a fake value for remaining places because we don't have access to real remaining places for EMS shows
        # This value will not impact quantity, seen that we update showtime quantity only if remaining places is 0 or 1.
        return json.dumps({int(show): self.EMS_FAKE_REMAINING_PLACES for show in available_shows.seances})
