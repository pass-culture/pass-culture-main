import csv
import logging
import os
import typing

import click

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import api as offer_api
from pcapi.core.offers import models as offer_models
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)

ORIGIN_VENUE_ID_HEADER = "origin_venue_id"
DESTINATION_VENUE_ID_HEADER = "destination_venue_id"


def _get_venues_to_move_from_csv_file() -> typing.Iterator[dict[str, str]]:
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
        offerers_api.create_action_history_when_move_offers(
            origin_venue.id, destination_venue.id, offer_ids, offers_type="individual"
        )


def _move_collective_offers(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    collective_offer_ids = []
    for collective_offer in origin_venue.collectiveOffers:
        educational_api.move_collective_offer_venue(collective_offer, destination_venue, with_restrictions=False)
        collective_offer_ids.append(collective_offer.id)
        offerers_api.create_action_history_when_move_offers(
            origin_venue.id, destination_venue.id, collective_offer_ids, offers_type="collective"
        )


def _move_collective_offer_template(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> None:
    db.session.query(educational_models.CollectiveOfferTemplate).filter(
        educational_models.CollectiveOfferTemplate.venueId == origin_venue.id
    ).update({"venueId": destination_venue.id}, synchronize_session=False)


def _move_collective_offer_playlist(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> None:
    db.session.query(educational_models.CollectivePlaylist).filter(
        educational_models.CollectivePlaylist.venueId == origin_venue.id
    ).update({"venueId": destination_venue.id}, synchronize_session=False)


def _move_price_category_label(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    db.session.query(offer_models.PriceCategoryLabel).filter(
        offer_models.PriceCategoryLabel.venueId == origin_venue.id
    ).update({"venueId": destination_venue.id}, synchronize_session=False)


def _move_offer_from_csv_file(commit_by_venue: bool) -> None:
    invalid_venues = []
    for row in _get_venues_to_move_from_csv_file():
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
            if commit_by_venue:
                db.session.commit()
                logger.info("Transfert done for venue %d to venue %d", origin_venue_id, destination_venue_id)
            else:
                db.session.flush()
    _extract_invalid_venues_to_csv(invalid_venues)


@blueprint.cli.command("move_batch_offer")
@click.option("--dry-run", type=bool, default=True)
@click.option("--commit-by-venue", type=bool, default=True)
def move_batch_offer(dry_run: bool = True, commit_by_venue: bool = True) -> None:
    _move_offer_from_csv_file(commit_by_venue=commit_by_venue and not dry_run)
    if not dry_run:
        db.session.commit()
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
