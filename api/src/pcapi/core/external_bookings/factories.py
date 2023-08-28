import factory

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.testing import BaseFactory


class ExternalBookingFactory(BaseFactory):
    class Meta:
        model = ExternalBooking

    booking = factory.SubFactory(BookingFactory)
    barcode = factory.Sequence(lambda n: f"{n:13}")
    seat = factory.Sequence("A_{}".format)
    additional_information = factory.DictFactory()
