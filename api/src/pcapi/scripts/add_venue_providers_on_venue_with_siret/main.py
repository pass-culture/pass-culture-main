"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-36399-add-venue-providers-on-venue-with-siret/api/src/pcapi/scripts/add_venue_providers_on_venue_with_siret/main.py

"""

import argparse
import csv
import logging
import os

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm

import pcapi.core.providers.constants as providers_constants
from pcapi.app import app
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import exceptions as providers_exceptions
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.exceptions import ProviderException
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "venue_id"
MIGRATION_AUTHOR_ID = 2568200


def _write_modifications(modifications: list[tuple[int, str]], filename: str) -> None:
    # csv output to check what has been done and what failed
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/{filename}"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([VENUE_ID_HEADER, "Modification"])
        writer.writerows(modifications)


@atomic()
def _connect_venue_to_allocine(
    venue: Venue,
    provider_id: int,
    payload: providers_models.VenueProviderCreationPayload,
) -> providers_models.AllocineVenueProvider:
    # Rewriting those methods as they are still using repository.save() in repo
    if not payload.price:
        raise providers_exceptions.NoPriceSpecified()
    if payload.isDuo is None:  # see PostVenueProviderBody
        raise ValueError("`isDuo` is required")

    pivot = providers_repository.get_allocine_pivot(venue)
    if not pivot:
        theater = providers_repository.get_allocine_theater(venue)
        if not theater:
            raise providers_exceptions.NoMatchingAllocineTheater()
        pivot = providers_models.AllocinePivot(
            venue=venue,
            theaterId=theater.theaterId,
            internalId=theater.internalId,
        )
        db.session.add(pivot)
        db.session.flush()

    venue_provider = providers_models.AllocineVenueProvider(
        venue=venue,
        providerId=provider_id,
        venueIdAtOfferProvider=pivot.theaterId,
        isDuo=payload.isDuo,
        quantity=payload.quantity,
        internalId=pivot.internalId,
        price=payload.price,
    )
    db.session.add(venue_provider)
    db.session.flush()

    return venue_provider


@atomic()
def _connect_venue_to_cinema_provider(
    venue: Venue,
    provider: providers_models.Provider,
    payload: providers_models.VenueProviderCreationPayload,
) -> providers_models.VenueProvider:
    # Rewriting those methods as they are still using repository.save() in repo
    provider_pivot = providers_repository.get_cinema_provider_pivot_for_venue(venue)

    if not provider_pivot:
        raise providers_exceptions.NoCinemaProviderPivot()

    venue_provider = providers_models.VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.isDuoOffers = payload.isDuo if payload.isDuo else False
    venue_provider.venueIdAtOfferProvider = provider_pivot.idAtProvider

    db.session.add(venue_provider)
    db.session.flush()
    return venue_provider


@atomic()
def _connect_venue_to_provider(
    venue: Venue,
    provider: providers_models.Provider,
) -> providers_models.VenueProvider:
    # Rewriting those methods as they are still using repository.save() in repo
    venue_provider = providers_models.VenueProvider()
    venue_provider.venue = venue
    venue_provider.provider = provider

    db.session.add(venue_provider)
    db.session.flush()

    return venue_provider


@atomic()
def _create_cinema_pivot(
    venue_source: Venue, venue_destination: Venue, venue_provider: providers_models.VenueProvider
) -> None:
    if venue_provider.provider.localClass == "AllocineStocks":
        allocine_pivot_source = providers_repository.get_allocine_pivot(venue_source)
        allocine_pivot_destination = providers_repository.get_allocine_pivot(venue_destination)
        if allocine_pivot_source and not allocine_pivot_destination:
            allocine_pivot_destination = providers_models.AllocinePivot(
                venue=venue_destination,
                theaterId=allocine_pivot_source.theaterId,
                internalId=allocine_pivot_source.internalId,
            )
            db.session.add(allocine_pivot_destination)
            try:
                with atomic():
                    db.session.flush()
            except sa_exc.IntegrityError:
                logger.error(
                    "IntegrityError: cinema pivot %s already exists on venue %s",
                    allocine_pivot_source,
                    venue_destination,
                )
                return
            logger.info(
                "Created Allociné pivot with provider %s on venue %s",
                venue_destination.id,
                venue_provider.provider.id,
            )

    elif venue_provider.provider.localClass in providers_constants.CINEMA_PROVIDER_NAMES:
        cinema_pivot_source = providers_repository.get_cinema_provider_pivot_for_venue(venue=venue_source)
        cinema_pivot_destination = providers_repository.get_cinema_provider_pivot_for_venue(venue=venue_destination)
        if cinema_pivot_source:
            cinema_pivot_destination = providers_models.CinemaProviderPivot(
                venue=venue_destination,
                provider=cinema_pivot_source.provider,
                idAtProvider=cinema_pivot_source.idAtProvider,
            )
            db.session.add(cinema_pivot_destination)
            try:
                with atomic():
                    db.session.flush()
            except sa_exc.IntegrityError:
                logger.error(
                    "IntegrityError: cinema pivot %s already exists on venue %s", cinema_pivot_source, venue_destination
                )
                return
            logger.info(
                "Created Cinema pivot with provider %s on venue %s",
                venue_destination.id,
                venue_provider.provider.id,
            )


@atomic()
def _create_venue_provider(
    venue_source: Venue,
    venue_destination: Venue,
    venue_provider_source: providers_models.VenueProvider | providers_models.AllocineVenueProvider,
    user: User,
) -> providers_models.VenueProvider | None:
    _create_cinema_pivot(venue_source, venue_destination, venue_provider_source)

    provider = venue_provider_source.provider
    if provider.localClass == "AllocineStocks":
        payload = providers_models.VenueProviderCreationPayload(
            isDuo=venue_provider_source.isDuoOffers if venue_provider_source.isDuoOffers else False,
            quantity=venue_provider_source.quantity,
            venueIdAtOfferProvider=venue_provider_source.venueIdAtOfferProvider,
            price=venue_provider_source.price,
        )
        new_venue_provider = _connect_venue_to_allocine(venue_destination, provider.id, payload)
    elif provider.localClass in providers_constants.CINEMA_PROVIDER_NAMES:
        payload = providers_models.VenueProviderCreationPayload(
            isDuo=venue_provider_source.isDuoOffers if venue_provider_source.isDuoOffers else False,
        )
        new_venue_provider = _connect_venue_to_cinema_provider(venue_destination, provider, payload)
    else:
        new_venue_provider = _connect_venue_to_provider(venue_destination, provider)
    db.session.add(new_venue_provider)

    history_api.add_action(
        history_models.ActionType.SYNC_VENUE_TO_PROVIDER,
        author=user,
        venue=venue_destination,
        provider_name=provider.name,
    )

    db.session.flush()

    logger.info(
        "La synchronisation d'offre a été activée",
        extra={"venue_id": venue_destination.id, "provider_id": provider.id},
        technical_message_id="offer.sync.activated",
    )
    return new_venue_provider


def _get_venues_without_siret_and_not_permanent_with_providers() -> list[Venue]:
    subquery = (
        db.session.query(Venue.managingOffererId)
        .filter(Venue.siret.is_not(None))
        .group_by(Venue.managingOffererId)
        .having(sa.func.count(Venue.id) == 1)
        .subquery()
    )
    return (
        db.session.query(Venue)
        .join(providers_models.VenueProvider)
        .join(subquery, Venue.managingOffererId == subquery.c.managingOffererId)
        .filter(Venue.siret.is_(None), Venue.isPermanent.is_(True))
        .options(sa_orm.load_only(Venue.id, Venue.siret, Venue.managingOffererId))
        .all()
    )


def _get_unique_venues_with_siret_by_offerer() -> list[Venue]:
    VenueAlias = sa_orm.aliased(Venue)
    subquery = (
        db.session.query(Venue.managingOffererId)
        .filter(Venue.siret.is_not(None))
        .group_by(Venue.managingOffererId)
        .having(sa.func.count(Venue.id) == 1)
        .subquery()
    )
    return (
        db.session.query(Venue)
        .join(subquery, Venue.managingOffererId == subquery.c.managingOffererId)
        .filter(Venue.siret.is_not(None))
        .filter(
            sa.not_(
                db.session.query(VenueAlias)
                .filter(
                    VenueAlias.managingOffererId == Venue.managingOffererId,
                    VenueAlias.id != Venue.id,
                    VenueAlias.siret.is_not(None),
                )
                .exists()
            )
        )
        .all()
    )


@atomic()
def main(not_dry: bool) -> None:
    log_modifications: list[tuple[int, str]] = []
    log_fails: list[tuple[int, str]] = []
    venues_without_siret_with_providers = _get_venues_without_siret_and_not_permanent_with_providers()
    venues_with_siret_by_offerer = _get_unique_venues_with_siret_by_offerer()
    user = User.query.get(MIGRATION_AUTHOR_ID)
    venue_with_siret = {venue.managingOffererId: venue for venue in venues_with_siret_by_offerer}
    for venue_source in venues_without_siret_with_providers:
        venue_destination = venue_with_siret.get(venue_source.managingOffererId)
        if not venue_destination:
            log_fails.append((venue_source.id, f"Pas de siret sur cet offerer {venue_source.managingOffererId}"))
            continue

        for venue_provider in venue_source.venueProviders:
            try:
                with atomic():
                    _create_venue_provider(venue_source, venue_destination, venue_provider, user)
                    log_modifications.append(
                        (
                            venue_source,
                            f"Ajout du provider {venue_provider.provider} sur la venue {venue_destination}",
                        )
                    )
                    logger.info(
                        "Adding provider %s on venue %s",
                        venue_provider.providerId,
                        venue_destination.id,
                    )
            except sa_exc.IntegrityError:
                logger.error("IntegrityError: %s is already synch. with %s", venue_destination, venue_provider.provider)
                log_fails.append(
                    (venue_source.id, f"Cette venue est déjà synchro avec le provider {venue_provider.provider}.")
                )
                continue
            except ProviderException:
                logger.error(
                    "Provider exception: could not move provider %s to venue %s",
                    venue_provider.provider,
                    venue_destination,
                )
                log_fails.append(
                    (
                        venue_source.id,
                        f"Impossible de configurer le Provider {venue_provider.provider} avec cette venue",
                    )
                )
                continue

    _write_modifications(log_modifications, "add_providers.csv")
    _write_modifications(log_fails, "add_providers_fails.csv")

    if not not_dry:
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
