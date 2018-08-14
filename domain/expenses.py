from domain import MAX_SUBVENTION_ALL
from repository.booking_queries import find_by_user_id


def get_expenses(user, find_bookings_by_user_id=find_by_user_id):
    query = find_bookings_by_user_id(user.id)
    amounts = map(lambda x: x.amount, query)
    actual_expenses_all = sum(amounts)
    return {'all': {'max': MAX_SUBVENTION_ALL, 'actual': float(actual_expenses_all)}}
