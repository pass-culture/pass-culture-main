import factory

from pcapi.core.booking_providers.models import BookingProvider
from pcapi.core.booking_providers.models import BookingProviderName
from pcapi.core.booking_providers.models import VenueBookingProvider
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.models import ExternalBooking
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.testing import BaseFactory
from pcapi.utils.token import random_token


class BookingProviderFactory(BaseFactory):
    class Meta:
        model = BookingProvider

    name = BookingProviderName.CINE_DIGITAL_SERVICE
    apiUrl = factory.Sequence("ApiURL{}".format)


class VenueBookingProviderFactory(BaseFactory):
    class Meta:
        model = VenueBookingProvider

    venue = factory.SubFactory(VenueFactory)
    bookingProvider = factory.SubFactory(BookingProviderFactory)
    idAtProvider = factory.Sequence("idProvider{}".format)
    token = factory.LazyFunction(random_token)


class ExternalBookingFactory(BaseFactory):
    class Meta:
        model = ExternalBooking

    booking = factory.SubFactory(IndividualBookingFactory)
    barcode = factory.Sequence(lambda n: f"{n:13}")
    seat = factory.Sequence("A_{}".format)
