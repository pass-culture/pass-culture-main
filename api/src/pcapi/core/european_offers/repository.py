import logging

from pcapi.core.european_offers import models


logger = logging.getLogger(__name__)


def get_all_european_offers():
    return models.EuropeanOffer.query.all()


def get_all_european_offers_count():
    return models.EuropeanOffer.query.count()


def delete_all_european_offers():
    deleted_count = models.EuropeanOffer.query.delete()
    logger.info("%d European Offers have been deleted", deleted_count)
