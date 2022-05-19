from dataclasses import dataclass
import enum
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from pcapi.connectors.serialization.cine_digital_service_serializers import ScreenCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import SeatmapCDS
from pcapi.core.providers.models import VenueProvider
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class BookingProviderName(enum.Enum):
    CINE_DIGITAL_SERVICE = "Cine_Digital_Service"


class BookingProvider(PcObject, Model):  # type: ignore [valid-type, misc]
    id = Column(BigInteger, primary_key=True)

    name = Column(Enum(BookingProviderName), nullable=False)

    apiUrl = Column(String, nullable=False)


class VenueBookingProvider(VenueProvider):
    venueProviderId = Column(BigInteger, ForeignKey("venue_provider.id"), primary_key=True, nullable=False)

    bookingProviderId = Column(BigInteger, ForeignKey("booking_provider.id"), nullable=False)

    bookingProvider = relationship("BookingProvider", foreign_keys=[bookingProviderId])

    token = Column(String)

    isDuo = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint(
            "venueProviderId",
            "bookingProviderId",
            name="unique_venue_booking_provider",
        ),
    )


class SeatMap:
    def __init__(self, seatmap: list[list[int]]):
        self.map = seatmap
        self.nb_row = len(self.map)
        self.nb_col = len(self.map[0]) if len(self.map[0]) > 0 else 0


@dataclass
class Ticket:
    barcode: str
    seat_number: str


class BookingProviderClientAPI:
    def __init__(self, cinema_id: str, api_url: str, token: Optional[str]):
        self.token = token
        self.api_url = api_url
        self.cinema_id = cinema_id

    def get_show_remaining_places(self, show_id: int) -> int:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def get_seatmap(self, show_id: int) -> SeatMap:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def book_ticket(self, show_id: int, quantity: int) -> list[Ticket]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")


class SeatCDS:
    def __init__(self, seat_location_indices: tuple[int, int], screen_infos: ScreenCDS, seat_map: SeatmapCDS):
        self.seatRow = seat_location_indices[0] + 1
        self.seatCol = seat_location_indices[1] + 1
        if not screen_infos.seatmap_front_to_back:
            self.seatRow = seat_map.nb_row - seat_location_indices[0]
        if not screen_infos.seatmap_left_to_right:
            self.seatCol = seat_map.nb_col - seat_location_indices[1]

        if screen_infos.seatmap_skip_missing_seats:
            seat_row_array = seat_map.map[seat_location_indices[0]]
            previous_seats = (
                seat_row_array[: seat_location_indices[1]]
                if screen_infos.seatmap_left_to_right
                else seat_row_array[seat_location_indices[1] :]
            )
            skipped_seat = sum(1 for seat_value in previous_seats if seat_value == 0)
            self.seatCol -= skipped_seat

        seat_letter = chr(ord("A") + self.seatRow - 1)
        self.seatNumber = f"{seat_letter}_{self.seatCol}"
