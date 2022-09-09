from dataclasses import dataclass
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class BookingProviderName(enum.Enum):
    CINE_DIGITAL_SERVICE = "Cine_Digital_Service"


class BookingProvider(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    name: BookingProviderName = Column(Enum(BookingProviderName), nullable=False)

    apiUrl: str = Column(String, nullable=False)


class VenueBookingProvider(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    isActive: bool = Column(Boolean, nullable=False, default=True)

    venueId: int = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId])  # type: ignore [misc]

    bookingProviderId: int = Column(BigInteger, ForeignKey("booking_provider.id"), nullable=False)

    bookingProvider = relationship("BookingProvider", foreign_keys=[bookingProviderId])  # type: ignore [misc]

    idAtProvider: str = Column(String(70), nullable=False)

    token = Column(String)

    __table_args__ = (
        UniqueConstraint(
            "venueId",
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
class Movie:
    id: str
    title: str
    duration: int  # duration in minutes
    description: str
    posterpath: str | None
    visa: str


@dataclass
class Ticket:
    barcode: str
    seat_number: str


class BookingProviderClientAPI:
    def __init__(self, cinema_id: str, account_id: str, api_url: str, token: str | None):
        self.token = token
        self.api_url = api_url
        self.cinema_id = cinema_id
        self.account_id = account_id

    def get_show_remaining_places(self, show_id: int) -> int:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[int, int]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def get_venue_movies(self) -> list[Movie]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def get_seatmap(self, show_id: int) -> SeatMap:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def book_ticket(self, show_id: int, quantity: int) -> list[Ticket]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")
