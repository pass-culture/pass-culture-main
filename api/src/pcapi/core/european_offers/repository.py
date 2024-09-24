from . import models


def get_all_european_offers():
    return models.EuropeanOffer.query.all()
