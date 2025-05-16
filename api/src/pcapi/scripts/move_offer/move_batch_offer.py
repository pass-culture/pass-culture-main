import csv
import logging
import os
import typing
from functools import partial

import click

from pcapi.core import search
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import api as offer_api
from pcapi.core.offers import models as offer_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.repository.session_management import on_commit
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

ORIGIN_VENUE_ID_HEADER = "origin_venue_id"
DESTINATION_VENUE_ID_HEADER = "destination_venue_id"


def _get_venue_rows(origin: int | None, destination: int | None) -> typing.Iterator[dict]:
    if origin and destination:
        yield from [{ORIGIN_VENUE_ID_HEADER: origin, DESTINATION_VENUE_ID_HEADER: destination}]
    else:
        namespace_dir = os.path.dirname(os.path.abspath(__file__))
        with open(f"{namespace_dir}/venues_to_move.csv", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=",")
            yield from csv_rows


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


def check_origin_venue_validity(origin_venue: offerers_models.Venue) -> str | None:
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
        origin_venue_is_invalid = check_origin_venue_validity(origin_venue)
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
    for offer in origin_venue.offers:
        offer_api.move_offer(offer, destination_venue)
        offer_ids.append(offer.id)
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
    for collective_offer in origin_venue.collectiveOffers:
        educational_api.move_collective_offer_venue(collective_offer, destination_venue, with_restrictions=False)
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


def _create_action_history(origin_venue_id: int, destination_venue_id: int) -> None:
    db.session.add(
        history_models.ActionHistory(
            venueId=origin_venue_id,
            actionType=history_models.ActionType.VENUE_REGULARIZATION,
            extraData={"destination_venue_id": destination_venue_id},
        )
    )
    db.session.add(
        history_models.ActionHistory(
            venueId=destination_venue_id,
            actionType=history_models.ActionType.VENUE_REGULARIZATION,
            extraData={"origin_venue_id": origin_venue_id},
        )
    )


def _soft_delete_origin_venue(origin_venue: offerers_models.Venue) -> None:
    origin_venue.isSoftDeleted = True
    db.session.add(origin_venue)


@atomic()
def _move_all_venue_offers(not_dry: bool, origin: int | None, destination: int | None) -> None:
    invalid_venues = []
    for row in _get_venue_rows(origin, destination):
        logger.info("Starting to move offers from venue (origin): %d to venue (destination): %d", origin, destination)
        origin_venue_id = int(row[ORIGIN_VENUE_ID_HEADER])
        destination_venue_id = int(row[DESTINATION_VENUE_ID_HEADER])

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
            _move_individual_offers(origin_venue, destination_venue)
            _move_collective_offers(origin_venue, destination_venue)
            _move_collective_offer_template(origin_venue, destination_venue)
            _move_collective_offer_playlist(origin_venue, destination_venue)
            _move_price_category_label(origin_venue, destination_venue)
            _move_finance_incident(origin_venue, destination_venue)
            destination_venue_updated_to_permanent = _update_destination_venue_to_permanent(destination_venue)
            _soft_delete_origin_venue(origin_venue)
            _create_action_history(origin_venue_id, destination_venue_id)

            if not_dry:
                venue_ids_to_reindex = [origin_venue_id]
                if destination_venue_updated_to_permanent:
                    venue_ids_to_reindex.append(destination_venue_id)
                on_commit(partial(search.reindex_venue_ids, venue_ids_to_reindex))
                logger.info("Transfer done for venue %d to venue %d", origin_venue_id, destination_venue_id)
            else:
                db.session.flush()
                mark_transaction_as_invalid()
    _extract_invalid_venues_to_csv(invalid_venues)


@blueprint.cli.command("move_batch_offer")
@click.option("--not-dry", is_flag=True)
@click.option("--origin", type=int, required=False)
@click.option("--destination", type=int, required=False)
def move_batch_offer(not_dry: bool, origin: int | None, destination: int | None) -> None:
    _move_all_venue_offers(not_dry=not_dry, origin=origin, destination=destination)
    if not_dry:
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
