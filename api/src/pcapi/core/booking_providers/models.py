import enum

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class BookingProviderName(enum.Enum):
    CINE_DIGITAL_SERVICE = "Cine_Digital_Service"


class BookingProvider(PcObject, Model):
    id = Column(BigInteger, primary_key=True)

    name = Column(Enum(BookingProviderName), nullable=False)

    apiUrl = Column(String, nullable=False)


class VenueBookingProvider(PcObject, Model):
    id = Column(BigInteger, primary_key=True)

    isActive = Column(Boolean, nullable=False, default=True)

    venueId = Column(BigInteger, ForeignKey("venue.id"), index=True, nullable=False)

    venue = relationship("Venue", foreign_keys=[venueId])

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
