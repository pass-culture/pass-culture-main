from pcapi.models import Offer
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class


def remove_duo_option_for_allocine_offers():
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    offers_to_update = Offer.query.filter_by(lastProviderId=allocine_provider.id).all()

    for offer in offers_to_update:
        offer.isDuo = False
    repository.save(*offers_to_update)
