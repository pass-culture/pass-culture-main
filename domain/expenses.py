from decimal import Decimal

from models import ThingType
from repository.booking_queries import find_all_by_user_id

PHYSICAL_EXPENSES_CAPPED_TYPES = [ThingType.LIVRE_EDITION, ThingType.AUDIOVISUEL, ThingType.MUSIQUE, ThingType.JEUX]
DIGITAL_EXPENSES_CAPPED_TYPES = [ThingType.AUDIOVISUEL, ThingType.JEUX_VIDEO, ThingType.MUSIQUE, ThingType.PRESSE_ABO]

SUBVENTION_TOTAL = Decimal(500)
SUBVENTION_PHYSICAL_THINGS = Decimal(200)
SUBVENTION_DIGITAL_THINGS = Decimal(200)


def get_expenses(bookings):
    total_expenses = _compute_booking_expenses(bookings)
    physical_expenses = _compute_booking_expenses(bookings, _get_bookings_of_physical_things)
    digital_expenses = _compute_booking_expenses(bookings, _get_bookings_of_digital_things)

    return {
        'all': {'max': SUBVENTION_TOTAL, 'actual': total_expenses},
        'physical': {'max': SUBVENTION_PHYSICAL_THINGS, 'actual': physical_expenses},
        'digital': {'max': SUBVENTION_DIGITAL_THINGS, 'actual': digital_expenses}
    }


def _compute_booking_expenses(bookings, get_bookings=lambda b: b):
    bookings_to_sum = filter(lambda b: not b.isCancelled,
                             get_bookings(bookings))
    expenses = map(lambda x: x.amount * x.quantity, bookings_to_sum)
    return Decimal(sum(expenses))


def _get_bookings_of_digital_things(bookings):
    match = []
    for booking in bookings:
        thing = booking.stock.resolvedOffer.thing
        if thing and thing.isDigital and thing.type in map(str, DIGITAL_EXPENSES_CAPPED_TYPES):
            match.append(booking)
    return match


def _get_bookings_of_physical_things(bookings):
    match = []
    for booking in bookings:
        thing = booking.stock.resolvedOffer.thing
        if not thing:
            continue

        if thing.isDigital and thing.type == str(ThingType.LIVRE_EDITION):
            match.append(booking)

        if not thing.isDigital and thing.type in map(str, PHYSICAL_EXPENSES_CAPPED_TYPES):
            match.append(booking)

    return match
