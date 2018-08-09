from expenses import MAX_SUBVENTION_ALL
from models import Booking


def get_expenses(user):
    actual_expenses_all = _get_user_total_bookings(user)
    return {'all': {'max': MAX_SUBVENTION_ALL, 'actual': actual_expenses_all}}





def _get_user_total_bookings(user):
    query = Booking.query.filter_by(userId=user.id).all()
    amounts = map(lambda x: x.amount, query)
    return sum(amounts)