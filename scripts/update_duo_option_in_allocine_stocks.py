from models import PcObject, Offer
from repository.provider_queries import get_provider_by_local_class


def update_duo_option_in_allocine_stocks():
    allocine_provider = get_provider_by_local_class('AllocineStocks')
    offers_to_update = Offer.query \
        .filter_by(lastProviderId=allocine_provider.id) \
        .all()

    for offer in offers_to_update:
        offer.isDuo = False
    PcObject.save(*offers_to_update)
