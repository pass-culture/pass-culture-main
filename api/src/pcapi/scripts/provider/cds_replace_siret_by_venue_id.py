from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import db


def cds_replace_siret_by_venue_id(dry_run: bool = True) -> None:
    provider_id = providers_repository.get_provider_by_local_class("CDSStocks").id
    venue_providers = (
        providers_models.VenueProvider.query.filter(providers_models.VenueProvider.providerId == provider_id).join(Venue).all()
    )
    print(f"Début de traitement: {len(venue_providers)} lieux à traiter...")
    nb_offers = 0
    nb_stocks = 0
    processed_venues_count = 0
    for venue_provider in venue_providers:
        venue = venue_provider.venue
        if not venue.siret:
            print("Lieu %d sans SIRET", venue.id)
            continue
        offers = Offer.query.filter_by(venueId=venue.id, lastProviderId=provider_id).join(Stock).all()
        nb_offers += len(offers)
        print(f"Traitement de {len(offers)} offres pour le lieu {venue.id} ...")
        for offer in offers:
            offer.idAtProvider = offer.idAtProvider.replace(f"%{venue.siret}%", f"%{venue.id}%")
            nb_stocks += len(offer.stocks)
            for stock in offer.stocks:
                stock.idAtProviders = stock.idAtProviders.replace(f"%{venue.siret}%", f"%{venue.id}%")
        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()
        processed_venues_count += 1
        print(f"Lieu {venue.id} traité")

    print(
        f"Fin de traitement: {processed_venues_count} lieux traités, {nb_offers} offres traitées, {nb_stocks} stocks traités"
    )
