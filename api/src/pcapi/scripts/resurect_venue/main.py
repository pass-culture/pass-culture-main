import argparse
import csv
import json
import logging
import os
from collections.abc import Iterable
from functools import partial

import click
import sqlalchemy as sa

# ruff: noqa: I001
import pcapi.core.offerers.api  # noqa: F401 to avoid circular import
import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.api.offer as educational_api
import pcapi.core.educational.models as educational_models
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.api as offer_api
import pcapi.core.offers.models as offer_models
import pcapi.core.offers.repository as offers_repository
from pcapi import settings
from pcapi.core import search
from pcapi.models import db
from pcapi.scripts.move_offer import move_batch_offer
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)


class ObjectsToMove:
    offers: list[int]
    collective_offers: list[int]
    collective_offer_templates: list[int]

    def __init__(
        self,
        offers: list[int] | None = None,
        collective_offers: list[int] | None = None,
        collective_offer_templates: list[int] | None = None,
    ) -> None:
        self.offers = offers or []
        self.collective_offers = collective_offers or []
        self.collective_offer_templates = collective_offer_templates or []


def read_migration_log() -> Iterable[dict[str, str]]:
    namespace_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "flask",
        os.path.dirname(__file__).split("/")[-1],
    )
    try:
        with open(f"{namespace_dir}/full_log.csv", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=",")
            for row in csv_rows:
                yield row
    except FileNotFoundError:
        namespace_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            os.path.dirname(__file__).split("/")[-1],
        )
        with open(f"{namespace_dir}/full_log.csv", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=",")
            yield from csv_rows


def get_objects_to_move(rows: Iterable[dict[str, str]], venue_id: int) -> ObjectsToMove:
    objects_to_move = ObjectsToMove()
    for row in rows:
        if row["jsonPayload.extra.origin_venue_id"] != str(venue_id):
            continue
        if row["jsonPayload.extra.offer_ids"]:
            objects_to_move.offers = json.loads(row["jsonPayload.extra.offer_ids"])
        if row["jsonPayload.extra.collective_offer_ids"]:
            objects_to_move.collective_offers = json.loads(row["jsonPayload.extra.collective_offer_ids"])
        if row["jsonPayload.extra.collective_offer_template_ids"]:
            objects_to_move.collective_offer_templates = json.loads(
                row["jsonPayload.extra.collective_offer_template_ids"]
            )
    return objects_to_move


def _move_price_categories(
    objects_to_move: ObjectsToMove, destination_venue: offerers_models.Venue, origin_venue: offerers_models.Venue
) -> None:
    # Deal with existing price category labels on the destination venue
    existing_price_category_labels = (
        db.session.query(offer_models.PriceCategoryLabel)
        .filter(offer_models.PriceCategoryLabel.venueId == destination_venue.id)
        .all()
    )
    for price_category_label in existing_price_category_labels:
        # reconnect price categories with the same label and whose venue don't match
        price_category_ids = (
            (
                db.session.query(offer_models.PriceCategory)
                .join(offer_models.PriceCategory.offer)
                .join(offer_models.PriceCategory.priceCategoryLabel)
                .join(offer_models.PriceCategoryLabel.venue)
                .filter(
                    offer_models.PriceCategory.offerId.in_(objects_to_move.offers),
                    offer_models.PriceCategoryLabel.label == price_category_label.label,
                    offer_models.PriceCategoryLabel.venueId == origin_venue.id,
                )
            )
            .with_entities(offer_models.PriceCategory.id)
            .all()
        )
        db.session.query(offer_models.PriceCategory).filter(
            offer_models.PriceCategory.id.in_(price_category_ids)
        ).update({"priceCategoryLabelId": price_category_label.id}, synchronize_session=False)

    # Deal with price categories label that have been moved
    price_category_label_ids = (
        db.session.query(offer_models.PriceCategoryLabel)
        .join(offer_models.PriceCategoryLabel.priceCategories)
        .join(offer_models.PriceCategory.offer)
        .filter(
            offer_models.PriceCategory.offerId.in_(objects_to_move.offers),
            offer_models.PriceCategoryLabel.venueId != offer_models.Offer.venueId,
        )
        .with_entities(offer_models.PriceCategory.id)
        .all()
    )
    db.session.query(offer_models.PriceCategoryLabel).filter(
        offer_models.PriceCategoryLabel.id.in_(price_category_label_ids)
    ).update({"venueId": destination_venue.id}, synchronize_session=False)


@atomic()
def resurrect_venue(dry_run: bool, origin_id: int, destination_id: int, objects_to_move: ObjectsToMove) -> None:
    if dry_run:
        mark_transaction_as_invalid()

    origin_venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == origin_id).one()
    destination_venue = (
        db.session.query(offerers_models.Venue)
        .execution_options(include_deleted=True)
        .filter(offerers_models.Venue.id == destination_id)
        .one()
    )

    # remove the soft delete to make sure the checks work
    assert destination_venue.isSoftDeleted
    destination_venue.isSoftDeleted = False
    db.session.flush()

    logger.info(
        "Starting to move offers from venue (origin): %d to venue (destination): %d",
        origin_id,
        destination_id,
    )

    invalidity_reason = move_batch_offer._check_venues_validity(
        origin_venue, origin_id, destination_venue, destination_id
    )
    if invalidity_reason and invalidity_reason != "Origin venue permanent, open to public or with SIRET. ":
        logger.error(
            "Cannot move offers from venue (origin): %d to venue (destination): %d, reason: %s",
            origin_id,
            destination_id,
            invalidity_reason,
        )
        # Raising an error here will rollback the transaction
        raise ValueError(invalidity_reason)

    # Now the core of the process
    db.session.execute(sa.text("SET SESSION statement_timeout = '1200s'"))  # 20 minutes

    offers_repository.lock_stocks_for_venue(origin_id)
    db.session.flush()

    # Individual offers
    offer_ids = []
    for offer in db.session.query(offer_models.Offer).filter(offer_models.Offer.id.in_(objects_to_move.offers)).all():
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

    # Collective offers
    collective_offer_ids = []
    for collective_offer in db.session.query(educational_models.CollectiveOffer).filter(
        educational_models.CollectiveOffer.id.in_(objects_to_move.collective_offers)
    ):
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

    # Collective offer templates
    collective_offer_template_query = db.session.query(educational_models.CollectiveOfferTemplate).filter(
        educational_models.CollectiveOfferTemplate.id.in_(objects_to_move.collective_offer_templates)
    )
    collective_offer_template_query.update({"venueId": destination_venue.id}, synchronize_session=False)
    collective_offer_template_ids = [
        collective_offer_template.id for collective_offer_template in collective_offer_template_query.all()
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

    _move_price_categories(objects_to_move, destination_venue, origin_venue)

    # Finance incident
    individual_finance_incident_ids = (
        db.session.query(finance_models.FinanceIncident)
        .join(
            finance_models.FinanceIncident.booking_finance_incidents,
        )
        .join(
            finance_models.BookingFinanceIncident.booking,
        )
        .filter(
            finance_models.FinanceIncident.venueId == origin_id,
            bookings_models.Booking.venueId == destination_id,
        )
        .with_entities(finance_models.FinanceIncident.id)
    )
    db.session.query(finance_models.FinanceIncident).filter(
        finance_models.FinanceIncident.id.in_(individual_finance_incident_ids)
    ).update(
        {"venueId": destination_venue.id},
        synchronize_session=False,
    )
    collective_finance_incident_ids = (
        db.session.query(finance_models.FinanceIncident)
        .join(
            finance_models.FinanceIncident.booking_finance_incidents,
        )
        .join(
            finance_models.BookingFinanceIncident.collectiveBooking,
        )
        .filter(
            finance_models.FinanceIncident.venueId == origin_id,
            educational_models.CollectiveBooking.venueId == destination_id,
        )
        .with_entities(finance_models.FinanceIncident.id)
    )
    db.session.query(finance_models.FinanceIncident).filter(
        finance_models.FinanceIncident.id.in_(collective_finance_incident_ids)
    ).update(
        {"venueId": destination_venue.id},
        synchronize_session=False,
    )

    move_batch_offer._create_action_history(origin_id, destination_id, False)
    db.session.flush()

    db.session.execute(sa.text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))

    if not dry_run:
        on_commit(partial(search.reindex_venue_ids, [origin_id]))
    logger.info("Transfer done for venue %d to venue %d", origin_id, destination_id)


@blueprint.cli.command("resurect_venue")
@click.option("--not-dry", is_flag=True)
@click.option("--origin", type=int, required=True)
@click.option("--destination", type=int, required=True)
def resurrect_venue_command(not_dry: bool, origin: int, destination: int) -> None:
    rows = read_migration_log()
    objects_to_move = get_objects_to_move(rows, destination)
    resurrect_venue(not not_dry, origin, destination, objects_to_move)
    if not_dry:
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")


# Script version
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mais qui va lire ça ?")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--origin", type=int, help="Origin venue", required=True)
    parser.add_argument("--destination", type=int, help="Destination venue", required=True)
    args = parser.parse_args()

    from pcapi.app import app

    app.app_context().push()

    try:
        rows = read_migration_log()
        objects_to_move = get_objects_to_move(rows, args.destination)
        resurrect_venue(args.dry_run, args.origin, args.destination, objects_to_move)
    except:
        db.session.rollback()
        raise
    else:
        if args.dry_run:
            db.session.rollback()
        else:
            db.session.commit()
