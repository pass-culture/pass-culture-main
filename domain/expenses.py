from decimal import Decimal

from repository.booking_queries import find_all_by_user_id

SUBVENTION_TOTAL = Decimal(500)
SUBVENTION_PHYSICAL_THINGS = Decimal(200)
SUBVENTION_DIGITAL_THINGS = Decimal(200)


def get_expenses(user, find_bookings_by_user_id=find_all_by_user_id):
    bookings = find_bookings_by_user_id(user.id)

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
    booking_for_things = [b for b in bookings if b.stock.resolvedOffer.thing]
    bookings_to_sum = [b for b in booking_for_things if b.stock.resolvedOffer.thing.isDigital]
    return bookings_to_sum


def _get_bookings_of_physical_things(bookings):
    booking_for_things = [b for b in bookings if b.stock.resolvedOffer.thing]
    bookings_to_sum = [b for b in booking_for_things if not b.stock.resolvedOffer.thing.isDigital]
    return bookings_to_sum
