"""
If you need to read venue ids from a file, place it in the appropriate bucket like so:
<bucket>/flask/move_offer/venues_to_move.csv

headers should be :
origin_venue_id | destination_venue_id
"""

import csv
import logging
import os
import traceback
import typing
from functools import partial

import click
from sqlalchemy import exc as sa_exc

import pcapi.core.providers.constants as providers_constants
from pcapi import settings
from pcapi.core import search
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import api as offer_api
from pcapi.core.offers import models as offer_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.providers import exceptions as providers_exceptions
from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

ORIGIN_VENUE_ID_HEADER = "origin_venue_id"
DESTINATION_VENUE_ID_HEADER = "destination_venue_id"


def _get_venue_rows(origin: int | None, destination: int | None) -> typing.Iterator[dict]:
    if origin and destination:
        yield from [{ORIGIN_VENUE_ID_HEADER: origin, DESTINATION_VENUE_ID_HEADER: destination}]
    else:
        list_files_recursive(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        namespace_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "flask",
            os.path.dirname(__file__).split("/")[-1],
        )
        try:
            with open(f"{namespace_dir}/venues_to_move.csv", "r", encoding="utf-8") as csv_file:
                csv_rows = csv.DictReader(csv_file, delimiter=",")
                yield from csv_rows
        except FileNotFoundError:
            namespace_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                os.path.dirname(__file__).split("/")[-1],
            )
            with open(f"{namespace_dir}/venues_to_move.csv", "r", encoding="utf-8") as csv_file:
                csv_rows = csv.DictReader(csv_file, delimiter=",")
                yield from csv_rows


def list_files_recursive(path: str) -> None:
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            list_files_recursive(full_path)
        else:
            IGNORED_SUFFIXES = (".pyc", ".py", "__pycache__")
            if not any([full_path.endswith(suffix) for suffix in IGNORED_SUFFIXES]):
                print(full_path)


def _extract_invalid_venues_to_csv(invalid_venues: list[tuple[int, int, str]]) -> None:
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/venues_impossible_to_move.csv"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([ORIGIN_VENUE_ID_HEADER, DESTINATION_VENUE_ID_HEADER, "Reason"])
        writer.writerows(invalid_venues)


def _check_destination_venue_validity(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> str | None:
    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        origin_venue,
        include_without_pricing_points=True,
        only_similar_pricing_points=True,
        filter_same_bank_account=True,
    )
    if not venues_choices:
        logger.info(
            "No compatible venue was found for venue %d. Destination venue was %d",
            origin_venue.id,
            destination_venue.id,
        )
        return "No compatible venue. "
    if destination_venue not in venues_choices:
        logger.info("Destination venue %d is not valid for venue %d", destination_venue.id, origin_venue.id)
        return "Destination venue not valid. "
    return None


def _check_origin_venue_validity(origin_venue: offerers_models.Venue) -> str | None:
    if origin_venue.isPermanent or origin_venue.isOpenToPublic or bool(origin_venue.siret):
        logger.info("Origin venue with id %d permanent, open to public or with SIRET.", origin_venue.id)
        return "Origin venue permanent, open to public or with SIRET. "
    return None


def _check_venues_validity(
    origin_venue: offerers_models.Venue | None,
    origin_venue_id: int,
    destination_venue: offerers_models.Venue | None,
    destination_venue_id: int,
) -> str | None:
    invalidity_reason = ""
    if origin_venue is None:
        logger.info("Origin venue not found. id: %d", origin_venue_id)
        invalidity_reason += "Origin venue not found. "
    else:
        origin_venue_is_invalid = _check_origin_venue_validity(origin_venue)
        if origin_venue_is_invalid:
            invalidity_reason += origin_venue_is_invalid

    if destination_venue is None:
        logger.info("Destination venue not found. id: %d", destination_venue_id)
        invalidity_reason += "Destination venue not found. "
    elif origin_venue:
        destination_venue_is_invalid = _check_destination_venue_validity(origin_venue, destination_venue)
        if destination_venue_is_invalid:
            invalidity_reason += destination_venue_is_invalid
    return invalidity_reason


def _move_individual_offers(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    offer_ids = []
    offer_list = list(origin_venue.offers)
    for offer in offer_list:
        offer_api.move_offer(offer, destination_venue)
        offer_ids.append(offer.id)
        db.session.flush()
    logger.info(
        "Individual offers' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "offer_ids": offer_ids,
            "offers_type": "individual",
        },
        technical_message_id="offer.move",
    )


def _move_collective_offers(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    collective_offer_ids = []
    collective_offer_list = list(origin_venue.collectiveOffers)
    for collective_offer in collective_offer_list:
        educational_api.move_collective_offer_for_regularization(collective_offer, destination_venue)
        collective_offer_ids.append(collective_offer.id)
    logger.info(
        "Collective offers' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "collective_offer_ids": collective_offer_ids,
            "offers_type": "collective",
        },
        technical_message_id="collective_offer.move",
    )


def _move_collective_offer_template(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> None:
    collective_offer_templates = db.session.query(educational_models.CollectiveOfferTemplate).filter(
        educational_models.CollectiveOfferTemplate.venueId == origin_venue.id
    )
    collective_offer_templates.update({"venueId": destination_venue.id}, synchronize_session=False)
    collective_offer_template_ids = [
        collective_offer_template.id for collective_offer_template in collective_offer_templates.all()
    ]
    logger.info(
        "Collective offer templates' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "collective_offer_template_ids": collective_offer_template_ids,
            "offers_type": "collective",
        },
        technical_message_id="collective_offer_template.move",
    )


def _move_collective_offer_playlist(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> None:
    collective_offer_playlists = db.session.query(educational_models.CollectivePlaylist).filter(
        educational_models.CollectivePlaylist.venueId == origin_venue.id
    )
    collective_offer_playlists.update({"venueId": destination_venue.id}, synchronize_session=False)
    collective_offer_playlist_ids = [
        collective_offer_playlist.id for collective_offer_playlist in collective_offer_playlists.all()
    ]
    logger.info(
        "Collective offer playlists' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "collective_offer_playlist_ids": collective_offer_playlist_ids,
            "offers_type": "collective",
        },
        technical_message_id="collective_offer_playlist.move",
    )


def _move_price_category_label(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    origin_price_category_labels = (
        db.session.query(offer_models.PriceCategoryLabel)
        .filter(offer_models.PriceCategoryLabel.venueId == origin_venue.id)
        .all()
    )
    for origin_price_category_label in origin_price_category_labels:
        existing_price_category_label = (
            db.session.query(offer_models.PriceCategoryLabel)
            .filter(
                offer_models.PriceCategoryLabel.venueId == destination_venue.id,
                offer_models.PriceCategoryLabel.label == origin_price_category_label.label,
            )
            .one_or_none()
        )
        if existing_price_category_label:
            db.session.query(offer_models.PriceCategory).filter(
                offer_models.PriceCategory.priceCategoryLabelId == origin_price_category_label.id
            ).update(
                {"priceCategoryLabelId": existing_price_category_label.id},
                synchronize_session=False,
            )
        else:
            origin_price_category_label.venueId = destination_venue.id
            db.session.add(origin_price_category_label)


def _move_finance_incident(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    db.session.query(finance_models.FinanceIncident).filter(
        finance_models.FinanceIncident.venueId == origin_venue.id
    ).update({"venueId": destination_venue.id}, synchronize_session=False)


def _update_destination_venue_to_permanent(destination_venue: offerers_models.Venue) -> bool:
    if not destination_venue.isPermanent:
        destination_venue.isPermanent = True
        db.session.add(destination_venue)
        logger.info("Destination venue %d updated to permanent", destination_venue.id)
        return True
    return False


def _create_action_history(
    origin_venue_id: int, destination_venue_id: int, destination_venue_updated_to_permanent: bool
) -> None:
    db.session.add(
        history_models.ActionHistory(
            venueId=origin_venue_id,
            actionType=history_models.ActionType.VENUE_REGULARIZATION,
            extraData={"destination_venue_id": destination_venue_id},
        )
    )
    db.session.add(
        history_models.ActionHistory(
            venueId=origin_venue_id,
            actionType=history_models.ActionType.VENUE_SOFT_DELETED,
        )
    )
    if destination_venue_updated_to_permanent:
        db.session.add(
            history_models.ActionHistory(
                venueId=destination_venue_id,
                actionType=history_models.ActionType.VENUE_REGULARIZATION,
                extraData={
                    "origin_venue_id": origin_venue_id,
                    "modified_info": {"isPermanent": {"old_info": False, "new_info": True}},
                },
            )
        )


def _soft_delete_origin_venue(origin_venue: offerers_models.Venue) -> None:
    origin_venue.isSoftDeleted = True
    db.session.add(origin_venue)


@atomic()
def _connect_venue_to_cinema_provider(
    venue: offerers_models.Venue,
    provider: providers_models.Provider,
    payload: providers_models.VenueProviderCreationPayload,
) -> providers_models.VenueProvider:
    # Rewriting those methods as they are still using repository.save() in repo
    provider_pivot = providers_repository.get_cinema_provider_pivot_for_venue(venue)

    if not provider_pivot:
        raise providers_exceptions.NoCinemaProviderPivot()

    venue_provider = providers_models.VenueProvider()
    venue_provider.isActive = False
    venue_provider.venue = venue
    venue_provider.provider = provider
    venue_provider.isDuoOffers = payload.isDuo if payload.isDuo else False
    venue_provider.venueIdAtOfferProvider = provider_pivot.idAtProvider

    db.session.add(venue_provider)
    logger.info("Connect cinema provider %s to venue %s", provider, venue)
    return venue_provider


@atomic()
def _connect_venue_to_provider(
    venue: offerers_models.Venue,
    venue_provider: providers_models.VenueProvider,
) -> providers_models.VenueProvider:
    # Rewriting those methods as they are still using repository.save() in repo
    new_venue_provider = providers_models.VenueProvider()
    new_venue_provider.isActive = False
    new_venue_provider.venue = venue
    new_venue_provider.provider = venue_provider.provider
    new_venue_provider.venueIdAtOfferProvider = venue_provider.venueIdAtOfferProvider

    db.session.add(new_venue_provider)
    logger.info("Connect provider %s to venue %s", new_venue_provider.provider, venue)
    return new_venue_provider


@atomic()
def _move_cinema_pivot_to_destination_venue(
    origin_venue: offerers_models.Venue,
    destination_venue: offerers_models.Venue,
    venue_provider: providers_models.VenueProvider,
) -> None:
    if venue_provider.provider.localClass in providers_constants.CINEMA_PROVIDER_NAMES:
        cinema_pivot_source = providers_repository.get_cinema_provider_pivot_for_venue(venue=origin_venue)
        cinema_pivot_destination = providers_repository.get_cinema_provider_pivot_for_venue(venue=destination_venue)
        if cinema_pivot_destination:
            logger.info(
                "Venue source: %s. Cinema pivot %s already exists on destination venue %s",
                origin_venue.id,
                cinema_pivot_destination,
                destination_venue.id,
            )
        elif cinema_pivot_source:
            cinema_pivot_source.venue = destination_venue
            db.session.flush()
            logger.info(
                "Moving Cinéma pivot from venue %s to venue %s",
                origin_venue.id,
                destination_venue.id,
            )


@atomic()
def _create_destination_venue_provider(
    origin_venue: offerers_models.Venue,
    destination_venue: offerers_models.Venue,
    venue_provider_source: providers_models.VenueProvider,
) -> providers_models.VenueProvider | None:
    _move_cinema_pivot_to_destination_venue(origin_venue, destination_venue, venue_provider_source)
    provider = venue_provider_source.provider
    if provider.localClass in providers_constants.CINEMA_PROVIDER_NAMES:
        payload = providers_models.VenueProviderCreationPayload(
            isDuo=venue_provider_source.isDuoOffers or False,
        )
        new_venue_provider = _connect_venue_to_cinema_provider(destination_venue, provider, payload)
    else:
        new_venue_provider = _connect_venue_to_provider(destination_venue, venue_provider_source)
    db.session.add(new_venue_provider)

    history_api.add_action(
        history_models.ActionType.SYNC_VENUE_TO_PROVIDER,
        author=None,
        venue=destination_venue,
        provider_name=provider.name,
    )
    return new_venue_provider


def _disable_origin_venue_providers(origin_venue_active_providers: list[providers_models.VenueProvider]) -> None:
    for venue_provider in origin_venue_active_providers:
        venue_provider.isActive = False
        db.session.add(venue_provider)
        history_api.add_action(
            history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED,
            author=None,
            venue=venue_provider.venue,
            provider_id=venue_provider.providerId,
            provider_name=venue_provider.provider.name,
            modified_info={"isActive": {"old_info": True, "new_info": False}},
        )
        db.session.flush()
        logger.info(
            "La synchronisation d'offre %d a été désactivée",
            venue_provider.id,
            extra={"venue_id": venue_provider.venueId, "provider_id": venue_provider.providerId},
            technical_message_id="deactivated",
        )


def _enable_destination_venue_provider(
    destination_venue_providers: list[providers_models.VenueProvider | None],
) -> None:
    for venue_provider in destination_venue_providers:
        assert venue_provider  # helps mypy
        venue_provider.isActive = True
        db.session.add(venue_provider)
        db.session.flush()
        logger.info(
            "La synchronisation d'offre a été activée",
            extra={"venue_id": venue_provider.venueId, "provider_id": venue_provider.providerId},
            technical_message_id="offer.sync.activated",
        )


def _move_providers(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> list[providers_models.VenueProvider | None]:
    if len(origin_venue.venueProviders) == 0:
        return []
    destination_venue_providers = []
    origin_venue_active_providers = (
        db.session.query(providers_models.VenueProvider)
        .filter(
            providers_models.VenueProvider.venueId == origin_venue.id,
            providers_models.VenueProvider.isActive == True,
        )
        .all()
    )
    _disable_origin_venue_providers(origin_venue_active_providers)

    for venue_provider in origin_venue_active_providers:
        provider_already_sync_with_destination = db.session.query(
            db.session.query(providers_models.VenueProvider)
            .filter(
                providers_models.VenueProvider.venueId == destination_venue.id,
                providers_models.VenueProvider.providerId == venue_provider.providerId,
            )
            .exists()
        ).scalar()
        if provider_already_sync_with_destination:
            logger.info("%s is already synchronized with %s", destination_venue, venue_provider.provider)
            continue
        destination_venue_provider = _create_destination_venue_provider(origin_venue, destination_venue, venue_provider)
        destination_venue_providers.append(destination_venue_provider)
    return destination_venue_providers


@atomic()
def _move_all_venue_offers(dry_run: bool, origin: int | None, destination: int | None) -> None:
    invalid_venues = []
    if dry_run:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()
    for row in _get_venue_rows(origin, destination):
        origin_venue_id = int(row[ORIGIN_VENUE_ID_HEADER])
        destination_venue_id = int(row[DESTINATION_VENUE_ID_HEADER])
        logger.info(
            "Starting to move offers from venue (origin): %d to venue (destination): %d",
            origin_venue_id,
            destination_venue_id,
        )

        origin_venue = (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == origin_venue_id).one_or_none()
        )
        destination_venue = (
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.id == destination_venue_id)
            .one_or_none()
        )

        invalidity_reason = _check_venues_validity(
            origin_venue, origin_venue_id, destination_venue, destination_venue_id
        )

        if invalidity_reason:
            invalid_venues.append((origin_venue_id, destination_venue_id, invalidity_reason))
        else:
            try:
                with atomic():
                    offers_repository.lock_stocks_for_venue(origin_venue_id)
                    db.session.flush()
                    destination_venue_providers = _move_providers(origin_venue, destination_venue)
                    _move_individual_offers(origin_venue, destination_venue)
                    _move_collective_offers(origin_venue, destination_venue)
                    _move_collective_offer_template(origin_venue, destination_venue)
                    _move_collective_offer_playlist(origin_venue, destination_venue)
                    _move_price_category_label(origin_venue, destination_venue)
                    _move_finance_incident(origin_venue, destination_venue)
                    destination_venue_updated_to_permanent = _update_destination_venue_to_permanent(destination_venue)
                    _soft_delete_origin_venue(origin_venue)
                    if destination_venue_providers:
                        _enable_destination_venue_provider(destination_venue_providers)
                    _create_action_history(
                        origin_venue_id, destination_venue_id, destination_venue_updated_to_permanent
                    )
                    db.session.flush()

                    if not dry_run:
                        on_commit(partial(search.reindex_venue_ids, [origin_venue_id]))
                    logger.info("Transfer done for venue %d to venue %d", origin_venue_id, destination_venue_id)
            except sa_exc.SQLAlchemyError:
                print(traceback.format_exc())
                invalid_venues.append((origin_venue.id, destination_venue.id, "SQL error: " + traceback.format_exc()))
            except Exception:
                print(traceback.format_exc())
                invalid_venues.append(
                    (origin_venue.id, destination_venue.id, "Python exception: " + traceback.format_exc())
                )
    _extract_invalid_venues_to_csv(invalid_venues)


@blueprint.cli.command("move_batch_offer")
@click.option("--not-dry", is_flag=True)
@click.option("--origin", type=int, required=False)
@click.option("--destination", type=int, required=False)
def move_batch_offer(not_dry: bool, origin: int | None, destination: int | None) -> None:
    dry_run = not not_dry
    db.session.execute("SET SESSION statement_timeout = '1200s'")  # 20 minutes
    _move_all_venue_offers(dry_run=dry_run, origin=origin, destination=destination)
    db.session.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")

    if not dry_run:
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
