from typing import List
from unittest.mock import Mock

from shapely.geometry import Polygon

from models import Booking
from models.feature import Feature, FeatureToggle
from repository import repository


def get_occurrence_short_name(concatened_names_with_a_date):
    splitted_names = concatened_names_with_a_date.split(' / ')

    if len(splitted_names) > 0:
        return splitted_names[0]

    return None


def get_price_by_short_name(occurrence_short_name=None):
    if occurrence_short_name is None:
        return 0

    return sum(map(ord, occurrence_short_name)) % 50


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
        booking.stock.resolvedOffer.bookingEmail = venue_email
        booking.stock.resolvedOffer.product.name = name
        bookings.append(booking)

    return bookings


def fake(object_type):
    class FakeObject(object_type):
        def __eq__(self, other_object):
            return isinstance(other_object, object_type)

    return FakeObject()


POLYGON_TEST = Polygon([(2.195693, 49.994169), (2.195693, 47.894173), (2.595697, 47.894173), (2.595697, 49.994169)])