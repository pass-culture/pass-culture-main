"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40502 \
  -f NAMESPACE=handle_regul_for_venues_with_rejected_offers \
  -f SCRIPT_ARGUMENTS="--commit --author-id 123";

Liste des venues : https://analytics.data.passculture.team/question/19714-venues-a-soft-delete-sans-offre
"""

import argparse
import csv
import logging
import os
import typing

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_IDS_FILENAME = "venue_ids"
VENUE_ID_HEADER = "venue_id"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _read_venue_ids(filename: str) -> list[int]:
    return [int(row[VENUE_ID_HEADER]) for row in _read_csv_file(filename)]


def _validate_venue(venue: offerers_models.Venue) -> str | None:
    """Check that the venue is: non-permanent, without SIRET, not open to public."""
    if venue.isPermanent:
        return "Venue is permanent"
    if venue.siret:
        return "Venue has a SIRET"
    if venue.isOpenToPublic:
        return "Venue is open to public"
    return None


def _check_no_non_rejected_offers(venue_id: int) -> str | None:
    """Check that there are no non-rejected individual, collective, or collective template offers."""
    has_non_rejected_individual = db.session.scalar(
        sa.select(
            sa.exists()
            .where(offers_models.Offer.venueId == venue_id)
            .where(offers_models.Offer.validation != OfferValidationStatus.REJECTED)
        )
    )
    if has_non_rejected_individual:
        return "Venue has non-rejected individual offers"

    has_non_rejected_collective = db.session.scalar(
        sa.select(
            sa.exists().where(
                educational_models.CollectiveOffer.venueId == venue_id,
                educational_models.CollectiveOffer.validation != OfferValidationStatus.REJECTED,
            )
        )
    )
    if has_non_rejected_collective:
        return "Venue has non-rejected collective offers"

    has_non_rejected_template = db.session.scalar(
        sa.select(
            sa.exists()
            .where(educational_models.CollectiveOfferTemplate.venueId == venue_id)
            .where(educational_models.CollectiveOfferTemplate.validation != OfferValidationStatus.REJECTED)
        )
    )
    if has_non_rejected_template:
        return "Venue has non-rejected collective offer templates"

    return None


def _check_no_bookings(venue_id: int) -> str | None:
    """Check that there are no individual or collective bookings."""
    has_individual_bookings = db.session.scalar(
        sa.select(sa.exists().where(bookings_models.Booking.venueId == venue_id))
    )
    if has_individual_bookings:
        return "Venue has individual bookings"

    has_collective_bookings = db.session.scalar(
        sa.select(sa.exists().where(educational_models.CollectiveBooking.venueId == venue_id))
    )
    if has_collective_bookings:
        return "Venue has collective bookings"

    return None


def _delete_rejected_offers(venue_id: int) -> dict[str, list[int]]:
    """Delete all rejected offers (individual, collective, collective template) for the venue."""
    deleted: dict[str, list[int]] = {"individual": [], "collective": [], "template": []}

    # Delete individual offers and their related objects (stocks, etc.)
    individual_offer_ids = list(
        db.session.scalars(
            sa.select(offers_models.Offer.id)
            .where(offers_models.Offer.venueId == venue_id)
            .where(offers_models.Offer.validation == OfferValidationStatus.REJECTED)
        )
    )
    if individual_offer_ids:
        offers_api.delete_offers_related_objects(individual_offer_ids)
        db.session.execute(sa.delete(offers_models.Offer).where(offers_models.Offer.id.in_(individual_offer_ids)))
        deleted["individual"] = individual_offer_ids

    # Delete collective offers
    collective_offer_ids = list(
        db.session.scalars(
            sa.select(educational_models.CollectiveOffer.id)
            .where(educational_models.CollectiveOffer.venueId == venue_id)
            .where(educational_models.CollectiveOffer.validation == OfferValidationStatus.REJECTED)
        )
    )
    if collective_offer_ids:
        db.session.execute(
            sa.delete(educational_models.CollectiveStock).where(
                educational_models.CollectiveStock.collectiveOfferId.in_(collective_offer_ids)
            )
        )
        db.session.execute(
            sa.delete(educational_models.CollectiveOffer).where(
                educational_models.CollectiveOffer.id.in_(collective_offer_ids)
            )
        )
        deleted["collective"] = collective_offer_ids

    # Delete collective offer templates
    template_ids = list(
        db.session.scalars(
            sa.select(educational_models.CollectiveOfferTemplate.id)
            .where(educational_models.CollectiveOfferTemplate.venueId == venue_id)
            .where(educational_models.CollectiveOfferTemplate.validation == OfferValidationStatus.REJECTED)
        )
    )
    if template_ids:
        # Nullify templateId on linked collective offers
        db.session.execute(
            sa.update(educational_models.CollectiveOffer)
            .where(educational_models.CollectiveOffer.templateId.in_(template_ids))
            .values(templateId=None)
        )
        # Delete related objects
        db.session.execute(
            sa.delete(educational_models.CollectiveOfferTemplateEducationalRedactor).where(
                educational_models.CollectiveOfferTemplateEducationalRedactor.collectiveOfferTemplateId.in_(
                    template_ids
                )
            )
        )
        db.session.execute(
            sa.delete(educational_models.CollectiveOfferRequest).where(
                educational_models.CollectiveOfferRequest.collectiveOfferTemplateId.in_(template_ids)
            )
        )
        db.session.execute(
            sa.delete(educational_models.CollectivePlaylist).where(
                educational_models.CollectivePlaylist.collectiveOfferTemplateId.in_(template_ids)
            )
        )
        # Delete templates
        db.session.execute(
            sa.delete(educational_models.CollectiveOfferTemplate).where(
                educational_models.CollectiveOfferTemplate.id.in_(template_ids)
            )
        )
        deleted["template"] = template_ids

    return deleted


def _soft_delete_venue(venue: offerers_models.Venue, author: users_models.User) -> None:
    venue.isSoftDeleted = True
    db.session.flush()
    history_api.add_action(
        history_models.ActionType.VENUE_SOFT_DELETED,
        author=author,
        venue=venue,
    )


@atomic()
def main(not_dry: bool, author: users_models.User) -> None:
    if not not_dry:
        logger.info("Dry run, will be rollbacked")
        mark_transaction_as_invalid()

    venue_ids = _read_venue_ids(VENUE_IDS_FILENAME)
    logger.info("Loaded venue IDs", extra={"count": len(venue_ids)})

    processed_count = 0
    skipped_count = 0

    for venue_id in venue_ids:
        venue = db.session.scalar(sa.select(offerers_models.Venue).where(offerers_models.Venue.id == venue_id))
        if venue is None:
            logger.warning("Venue not found, skipping", extra={"venue_id": venue_id})
            skipped_count += 1
            continue

        # Validate venue properties
        validation_error = _validate_venue(venue)
        if validation_error:
            logger.warning(
                "Venue validation failed, skipping",
                extra={"venue_id": venue_id, "reason": validation_error},
            )
            skipped_count += 1
            continue

        # Check no non-rejected offers
        offer_error = _check_no_non_rejected_offers(venue_id)
        if offer_error:
            logger.warning(
                "Venue has non-rejected offers, skipping",
                extra={"venue_id": venue_id, "reason": offer_error},
            )
            skipped_count += 1
            continue

        # Check no bookings
        booking_error = _check_no_bookings(venue_id)
        if booking_error:
            logger.warning(
                "Venue has bookings, skipping",
                extra={"venue_id": venue_id, "reason": booking_error},
            )
            skipped_count += 1
            continue

        # Delete rejected offers
        deleted = _delete_rejected_offers(venue_id)
        logger.info(
            "Deleted rejected offers for venue",
            extra={
                "venue_id": venue_id,
                "deleted_individual_offer_ids": deleted["individual"],
                "deleted_collective_offer_ids": deleted["collective"],
                "deleted_template_ids": deleted["template"],
            },
        )

        # Soft delete the venue
        _soft_delete_venue(venue, author)
        logger.info("Venue soft deleted", extra={"venue_id": venue_id})

        processed_count += 1

    logger.info(
        "Script completed",
        extra={"processed": processed_count, "skipped": skipped_count, "total": len(venue_ids)},
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--author-id", type=int, help="Author user ID", required=True)
    args = parser.parse_args()

    author = db.session.scalar(sa.select(users_models.User).where(users_models.User.id == args.author_id))

    main(not_dry=args.commit, author=author)

    if args.commit:
        logger.info("Script terminé avec succès")
    else:
        logger.info("Dry run terminé, rollback des données")
