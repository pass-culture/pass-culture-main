from typing import List

from sqlalchemy.orm import joinedload

from pcapi.core.offers.models import Offer
from pcapi.models import Venue
from pcapi.repository import repository


BATCH_SIZE = 100


def update_offer_and_stock_id_at_providers(venue_id: int) -> None:
    venue = Venue.query.get(venue_id)
    current_siret = venue.siret

    titelive_offers_to_update = _get_titelive_offers_with_old_id_at_providers(venue, current_siret)

    offers_to_update = []
    stocks_to_update = []

    for offer_to_update in titelive_offers_to_update:
        offer_to_update.idAtProviders = _correct_id_at_providers(offer_to_update.idAtProviders, current_siret)
        for stock_to_update in offer_to_update.stocks:
            stock_to_update.idAtProviders = _correct_id_at_providers(stock_to_update.idAtProviders, current_siret)
            stocks_to_update.append(stock_to_update)

        offers_to_update.append(offer_to_update)

        if len(offers_to_update) >= BATCH_SIZE:
            repository.save(*offers_to_update)
            repository.save(*stocks_to_update)
            offers_to_update = []
            stocks_to_update = []

    repository.save(*offers_to_update)
    repository.save(*stocks_to_update)


def _get_titelive_offers_with_old_id_at_providers(venue: Venue, current_siret: str) -> List[Offer]:
    return (
        Offer.query.filter(Offer.venueId == venue.id)
        .filter(~Offer.idAtProviders.endswith(current_siret))
        .options(joinedload(Offer.stocks))
        .all()
    )


def _correct_id_at_providers(id_at_providers: str, current_siret: str) -> str:
    return id_at_providers.split("@")[0] + "@" + current_siret
