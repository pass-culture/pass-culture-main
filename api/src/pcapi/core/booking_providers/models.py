import enum

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
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class BookingProviderName(enum.Enum):
    CINE_DIGITAL_SERVICE = "Cine_Digital_Service"


class BookingProvider(PcObject, Model):  # type: ignore [valid-type, misc]
    id = Column(BigInteger, primary_key=True)

    name = Column(Enum(BookingProviderName), nullable=False)

    apiUrl = Column(String, nullable=False)


class VenueBookingProvider(PcObject, Model):  # type: ignore [valid-type, misc]
    id = Column(BigInteger, primary_key=True)

    isActive = Column(Boolean, nullable=False, default=True)

    venueId = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId])  # type: ignore [misc]

    bookingProviderId = Column(BigInteger, ForeignKey("booking_provider.id"), nullable=False)

    bookingProvider = relationship("BookingProvider", foreign_keys=[bookingProviderId])

    idAtProvider = Column(String(70), nullable=False)

    token = Column(String)

    __table_args__ = (
        UniqueConstraint(
            "venueId",
            "bookingProviderId",
            "idAtProvider",
            name="unique_venue_booking_provider",
        ),
    )


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
