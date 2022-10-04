import factory

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.testing import BaseFactory


class ExternalBookingFactory(BaseFactory):
    class Meta:
        model = ExternalBooking

    booking = factory.SubFactory(IndividualBookingFactory)
    barcode = factory.Sequence(lambda n: f"{n:13}")
    seat = factory.Sequence("A_{}".format)
