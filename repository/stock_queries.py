from models import Stock, Offerer, User
from utils.human_ids import dehumanize



def _check_offerer_user(query, user):
    return query.filter(
        Offerer.users.any(User.id == user.id)
    ).first_or_404()


def find_stocks_with_possible_filters(filters, user):
    query = Stock.queryNotSoftDeleted()
    if 'offererId' in filters:
        query = query.filter(Stock.offererId == dehumanize(filters['offererId']))
        _check_offerer_user(query.first_or_404().offerer.query, user)
    # PRICE
    if 'hasPrice' in filters and filters['hasPrice'].lower() == 'true':
        query = query.filter(Stock.price != None)
    # RETURN
    return query
