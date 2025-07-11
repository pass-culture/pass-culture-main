"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-35670-hard-delete-venues-without-offers/api/src/pcapi/scripts/hard_delete_venues_without_offers/main.py

"""

import argparse
import csv
import datetime
import logging
import os
import typing

from sqlalchemy import exc as sa_exc
from sqlalchemy import or_

from pcapi.app import app
from pcapi.core.criteria import models as criteria_models
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.offerers import exceptions
from pcapi.core.offerers.api import delete_venue
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "Venue ID"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _check_if_venue_has_criterion_categories_that_are_not_playlist(venue_id: int) -> bool:
    subquery = (
        (
            db.session.query(criteria_models.VenueCriterion.venueId)
            .join(criteria_models.Criterion, criteria_models.VenueCriterion.criterionId == criteria_models.Criterion.id)
            .outerjoin(
                criteria_models.CriterionCategoryMapping,
                criteria_models.Criterion.id == criteria_models.CriterionCategoryMapping.criterionId,
            )
            .outerjoin(
                criteria_models.CriterionCategory,
                criteria_models.CriterionCategoryMapping.categoryId == criteria_models.CriterionCategory.id,
            )
        )
        .filter(
            criteria_models.VenueCriterion.venueId == venue_id,
            or_(
                criteria_models.CriterionCategory.label.is_(None),
                criteria_models.CriterionCategory.label != "Playlist lieux et offres",
            ),
        )
        .exists()
    )

    result = db.session.query(subquery).scalar()
    return bool(result)


def _check_venue_can_be_hard_deleted(
    venue_id: int,
    invalid_venues: list[tuple[int, str]],
) -> bool:
    venue: Venue = db.session.query(Venue).filter_by(id=venue_id).one_or_none()
    if not venue:
        invalid_venues.append((venue_id, "Venue can't be deleted: Venue not found"))
        return False

    six_month_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30 * 6)

    has_criterion = _check_if_venue_has_criterion_categories_that_are_not_playlist(venue.id)

    conditions = [
        (venue.isPermanent, "Venue is permanent"),
        (venue.isOpenToPublic, "Venue is open to public"),
        (venue.siret, "Venue has a SIRET number"),
        (venue.has_collective_offers, "Venue has collective offers"),
        (venue.collective_playlists, "Venue has collective offer playlist(s)"),
        (venue.collectiveOfferTemplates, "Venue has collective offer template(s)"),
        (venue.hasOffers, "Venue has offers"),
        (venue.dateCreated >= six_month_ago, "Venue was created less than six months ago"),
        (bool(venue.venueProviders), "Venue has providers"),
        (venue.adageId, "Venue has an ADAGE ID"),
        (
            has_criterion,
            "Venue has tags whose category are not 'Playlist lieux et offres' ",
        ),
    ]

    for condition, message in conditions:
        if condition:
            invalid_venues.append((venue_id, f"Venue can't be deleted: {message}"))
            return False
    return True


def _write_modifications(modifications: list[tuple[int, str]], filename: str) -> None:
    # csv output to check what has been done and what failed
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/{filename}"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([VENUE_ID_HEADER, "Modification"])
        writer.writerows(modifications)


def _delete_venues_from_csv(filename: str) -> list[str]:
    invalid_venues: list[tuple[int, str]] = []
    deleted_venues: list[tuple[int, str]] = []
    venue_booking_emails = list()
    venue_query = db.session.query(Venue)
    rows = _read_csv_file(filename)
    logger.info("Reading file %s", filename)
    for row in rows:
        venue_id = int(row[VENUE_ID_HEADER])
        print(f"Processing venue {venue_id}")
        if _check_venue_can_be_hard_deleted(venue_id, invalid_venues):
            venue_booking_email = venue_query.filter_by(id=venue_id).with_entities(Venue.bookingEmail).scalar()
            try:
                with atomic():
                    delete_venue(venue_id)
                    venue_booking_emails.append(venue_booking_email)
                    deleted_venues.append((venue_id, "Cette venue à été supprimée pour toujours. 🪦"))
            except sa_exc.SQLAlchemyError as error:
                invalid_venues.append((venue_id, f"Erreur SQL: {error}"))
            except exceptions.CannotDeleteVenueWithBookingsException:
                invalid_venues.append((venue_id, "Cette venue a des réservations"))
            except exceptions.CannotDeleteVenueUsedAsPricingPointException:
                invalid_venues.append((venue_id, "Cette venue est utilisée comme point de valo"))
            except exceptions.CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule:
                invalid_venues.append((venue_id, "Cette venue a des règles de remboursement spécifiques"))
    _write_modifications(invalid_venues, "hard_delete_venue_fails.csv")
    _write_modifications(deleted_venues, "hard_delete_venue_succedeed.csv")
    return venue_booking_emails


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    filename = "venues_to_delete"

    with atomic():
        venue_booking_emails = _delete_venues_from_csv(filename)
        if args.not_dry:
            for email in venue_booking_emails:
                external_attributes_api.update_external_pro(email)
            logger.info("Finished")
            db.session.flush()
        else:
            logger.info("Finished dry run, rollback")
            mark_transaction_as_invalid()
