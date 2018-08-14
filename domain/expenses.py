from decimal import Decimal

from repository.booking_queries import find_by_user_id

MAX_SUBVENTION_ALL = Decimal(500)
MAX_SUBVENTION_PHYSICAL = Decimal(100)
MAX_SUBVENTION_DIGITAL = Decimal(200)


def get_expenses(user, find_bookings_by_user_id=find_by_user_id):
    bookings = find_bookings_by_user_id(user.id)

    actual_all = _sum_bookings(bookings)
    actual_physical = _sum_bookings(bookings, _filter_physical_things_bookings)
    actual_digital = _sum_bookings(bookings, _filter_digital_things_bookings)

    return {
        'all': {'max': MAX_SUBVENTION_ALL, 'actual': actual_all},
        'physical': {'max': MAX_SUBVENTION_PHYSICAL, 'actual': actual_physical},
        'digital': {'max': MAX_SUBVENTION_DIGITAL, 'actual': actual_digital}
    }


def _sum_bookings(bookings, filter_bookings=lambda b: b):
    bookings_to_sum = filter_bookings(bookings)
    amounts = map(lambda x: x.amount * x.quantity, bookings_to_sum)
    return Decimal(sum(amounts))


def _filter_digital_things_bookings(bookings):
    booking_for_things = [b for b in bookings if b.stock.resolvedOffer.thing]
    bookings_to_sum = [b for b in booking_for_things if b.stock.resolvedOffer.thing.isDigital]
    return bookings_to_sum


def _filter_physical_things_bookings(bookings):
    booking_for_things = [b for b in bookings if b.stock.resolvedOffer.thing]
    bookings_to_sum = [b for b in booking_for_things if not b.stock.resolvedOffer.thing.isDigital]
    return bookings_to_sum
