from typing import List
from unittest.mock import Mock

from shapely.geometry import Polygon

from pcapi.models import Booking
from pcapi.models.feature import Feature, FeatureToggle
from pcapi.repository import repository


def deactivate_feature(feature_toggle: FeatureToggle):
    feature = Feature.query.filter_by(name=feature_toggle.name).one()
    feature.isActive = False
    repository.save(feature)


def create_mocked_bookings(num_bookings: int,
                           venue_email: str,
                           name: str = 'Offer name') -> List[Booking]:
    bookings = []

    for counter in range(num_bookings):
        booking = Mock(spec=Booking)
        booking.user.email = 'user_email%s' % counter
        booking.user.firstName = 'First %s' % counter
        booking.user.lastName = 'Last %s' % counter
        booking.stock.offer.bookingEmail = venue_email
        booking.stock.offer.product.name = name
        bookings.append(booking)

    return bookings


def fake(object_type):
    class FakeObject(object_type):
        def __eq__(self, other_object):
            return isinstance(other_object, object_type)

    return FakeObject()


POLYGON_TEST = Polygon([(2.195693, 49.994169), (2.195693, 47.894173), (2.595697, 47.894173), (2.595697, 49.994169)])
