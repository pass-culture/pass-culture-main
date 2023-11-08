import csv

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.models import db
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job


def activate_boost_sync(file_path: str, boost_username: str, boost_password: str) -> None:
    boost_provider = get_provider_by_local_class("BoostStocks")
    with open(file_path, mode="r", encoding="utf-8") as input_file:
        csv_reader = csv.DictReader(input_file, delimiter=";")
        total_cinemas = 0
        created_venue_providers_count = 0
        for row in csv_reader:
            api_url = row["URL API"]
            venue_id = row["PC ID"]
            cinema_name = row["Cinema - Ville"]
            total_cinemas += 1
            if not venue_id or not venue_id.isdigit():
                print(f"Identifiant de lieu non existant ou mal formaté cinema : {row['Cinema - Ville']}")
                continue
            venue_id = int(venue_id)
            venue = (
                offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
                .join(offerers_models.Venue.venueProviders, isouter=True)
                .join(providers_models.VenueProvider.provider, isouter=True)
                .one_or_none()
            )
            if not venue:
                print(f"Lieu non existant avec ID : {venue_id}")
                continue

            if (
                venue.venueProviders
                and venue.venueProviders[0]
                and venue.venueProviders[0].provider.localClass == "AllocineStocks"
            ):
                venue_provider = venue.venueProviders[0]
                update_venue_synchronized_offers_active_status_job.delay(
                    venue_provider.venueId, venue_provider.providerId, False
                )
                for price_rule in venue_provider.priceRules:
                    db.session.delete(price_rule)

                db.session.add(
                    history_api.log_action(
                        history_models.ActionType.LINK_VENUE_PROVIDER_DELETED,
                        author=None,
                        venue=venue_provider.venue,
                        save=False,
                        provider_id=venue_provider.providerId,
                        provider_name=venue_provider.provider.name,
                    )
                )
                db.session.delete(venue_provider)
            elif (
                venue.venueProviders
                and venue.venueProviders[0]
                and venue.venueProviders[0].provider.localClass != "BoostStocks"
            ):
                print(f"Lieu {venue.id} synchronisé avec le provider : {venue.venueProviders[0].provider.name}")
                continue
            pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=venue.id).one_or_none()
            if pivot:
                print(f"Pivot existe déjà pour lieu {venue.id}, cinema {cinema_name}")
                boost_details = providers_models.BoostCinemaDetails.query.filter_by(
                    cinemaProviderPivotId=pivot.id
                ).one_or_none()
                if not boost_details:
                    print(f"Lieu {venue.id} avec un pivot cinéma différent de boost details +++")
                    continue
                print(f"Mettre à jour pivot Boost pour lieu {venue.id} - cinema {cinema_name}")
                boost_details.cinemaUrl = api_url
                boost_details.username = boost_username
                db.session.add(boost_details)
            else:
                print(f"Création d'objets pivots pour {cinema_name} - {api_url}")
                pivot = providers_models.CinemaProviderPivot(
                    venue=venue, provider=boost_provider, idAtProvider=cinema_name
                )
                boost_details = providers_models.BoostCinemaDetails(
                    cinemaProviderPivot=pivot, cinemaUrl=api_url, username=boost_username, password=boost_password
                )
                venue_provider = providers_models.VenueProvider(
                    venue=venue, provider=boost_provider, venueIdAtOfferProvider=pivot.idAtProvider, isDuoOffers=True
                )
                db.session.add_all([pivot, boost_details, venue_provider])
                created_venue_providers_count += 1

        db.session.commit()
