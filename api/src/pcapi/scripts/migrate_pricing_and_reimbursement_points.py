# isort: off
# fmt: off
from pcapi.flask_app import app; app.app_context().push()  # pylint: disable=multiple-statements
# fmt: on
# isort: on

import datetime
import sys
import typing

import sentry_sdk

from pcapi import settings
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


def disable_sentry() -> None:
    # pylint: disable=abstract-class-instantiated
    sentry_sdk.init(dsn="https://disabled@localhost/0")


if settings.IS_STAGING:
    disable_sentry()


def get_latest_business_unit_links() -> dict[tuple[int, int], typing.Any]:
    """Return a mapping between all (venue id, business unit id) couples
    and their latest link.

    This venue only look at the `business_unit_venue_link` table, not
    at `Venue.businessUnitId`.
    """
    result = db.session.execute(
        """
        SELECT DISTINCT ON ("venueId", "businessUnitId")
            "venueId" AS venue_id,
            "businessUnitId" AS business_unit_id,
            siret AS business_unit_siret,
            timespan
        FROM business_unit_venue_link
        JOIN business_unit ON business_unit.id = business_unit_venue_link."businessUnitId"
        ORDER BY "venueId", "businessUnitId", lower(timespan) DESC
        """
    )
    rows = result.fetchall()
    return {(row.venue_id, row.business_unit_id): row for row in rows}


def get_business_unit_bearing_venue_by_id() -> dict[int, int]:
    """Return a mapping between a business unit id and the id of the venue
    that has the same SIRET.

    There are rare business units whose SIRET is not a SIRET of any
    venue. These business units are not returned by this function.
    """
    query = finance_models.BusinessUnit.query.join(
        offerers_models.Venue, offerers_models.Venue.siret == finance_models.BusinessUnit.siret
    ).with_entities(
        finance_models.BusinessUnit.id.label("business_unit_id"),
        offerers_models.Venue.id.label("venue_id"),
    )
    return {row.business_unit_id: row.venue_id for row in query}


def get_venue_ids_with_pricing_point_links() -> set[int]:
    """Return a set of venue ids that already have a pricing point
    link history.
    """
    return {
        venue_id
        for venue_id, in offerers_models.VenuePricingPointLink.query.with_entities(
            offerers_models.VenuePricingPointLink.venueId
        )
    }


def get_venue_ids_with_reimbursement_point_links() -> set[int]:
    """Return a set of venue ids that already have a reimbursement point
    link history.
    """
    return {
        venue_id
        for venue_id, in offerers_models.VenueReimbursementPointLink.query.with_entities(
            offerers_models.VenueReimbursementPointLink.venueId
        )
    }


def get_pricing_sirets_to_migrate() -> set[str]:
    """Return all SIRET that we have to migrate in Pricing."""
    return {
        siret
        for siret, in finance_models.Pricing.query.filter(
            finance_models.Pricing.pricingPointId.is_(None),
        )
        .with_entities(finance_models.Pricing.siret)
        .distinct()
    }


def get_cashflow_business_units_to_migrate() -> set[int]:
    """Return all business unit ids that we have to migrate in Cashflow."""
    return {
        business_unit_id
        for business_unit_id, in finance_models.Cashflow.query.filter(
            finance_models.Cashflow.reimbursementPointId.is_(None),
        )
        .with_entities(finance_models.Cashflow.businessUnitId)
        .distinct()
    }


def get_invoice_business_units_to_migrate() -> set[int]:
    """Return all business unit ids that we have to migrate in Invoice."""
    return {
        business_unit_id
        for business_unit_id, in finance_models.Invoice.query.filter(
            finance_models.Invoice.reimbursementPointId.is_(None),
        )
        .with_entities(finance_models.Invoice.businessUnitId)
        .distinct()
    }


def get_venues_by_siret() -> dict[str, int]:
    """Return a mapping between a SIRET and its venue id."""
    return dict(
        offerers_models.Venue.query.filter(offerers_models.Venue.siret.isnot(None)).with_entities(
            offerers_models.Venue.siret,
            offerers_models.Venue.id,
        )
    )


def create_pricing_point_links(apply_changes: bool) -> None:
    print("Starting creation of VenuePricingPointLink...")
    venues = offerers_models.Venue.query.order_by(offerers_models.Venue.id).with_entities(
        offerers_models.Venue.id,
        offerers_models.Venue.businessUnitId,
        offerers_models.Venue.siret,
    )
    latest_business_unit_links = get_latest_business_unit_links()
    bearing_venue_ids = get_business_unit_bearing_venue_by_id()
    venues_ids_with_pricing_point_links = get_venue_ids_with_pricing_point_links()

    links_to_add = []
    now = datetime.datetime.utcnow()
    for venue in venues:
        if venue.id in venues_ids_with_pricing_point_links:  # already migrated
            continue

        if venue.siret:
            # If the venue has a SIRET, its pricing point is itself.
            # Use the date of the latest BusinessUnitVenueLink to
            # continue using the same date when pricing.
            latest_bu_link = latest_business_unit_links.get((venue.id, venue.businessUnitId))
            if latest_bu_link:
                link_timespan = [latest_bu_link.timespan.lower, latest_bu_link.timespan.upper]
                if latest_bu_link.timespan.upper is not None:
                    print(
                        f"WARN: venue {venue.id}: Link with business unit {venue.businessUnitId} is inactive: incoherent data?"
                    )
            else:
                link_timespan = [now, None]
            links_to_add.append(
                offerers_models.VenuePricingPointLink(
                    venueId=venue.id,
                    pricingPointId=venue.id,
                    timespan=link_timespan,
                )
            )

        # If the venue does NOT have any SIRET, its pricing point is
        # its current business unit (if any)
        elif not venue.businessUnitId:
            continue
        else:
            latest_bu_link = latest_business_unit_links.get((venue.id, venue.businessUnitId))
            if latest_bu_link:
                link_timespan = [latest_bu_link.timespan.lower, latest_bu_link.timespan.upper]
                if latest_bu_link.timespan.upper is not None:
                    print(
                        f"WARN: venue {venue.id}: Link with business unit {venue.businessUnitId} is inactive: incoherent data?"
                    )
            else:
                print(
                    f"WARN: venue {venue.id}: Found no business unit link with {venue.businessUnitId}, used now as the start date."
                )
                link_timespan = [now, None]
            pricing_point_id = bearing_venue_ids.get(venue.businessUnitId)
            if not pricing_point_id:
                print(f"ERR: venue {venue.id}: No bearing venue for business unit {venue.businessUnitId}")
                continue
            links_to_add.append(
                offerers_models.VenuePricingPointLink(
                    venueId=venue.id,
                    pricingPointId=pricing_point_id,
                    timespan=link_timespan,
                )
            )

    if apply_changes:
        print(f"Inserting (SQL) VenuePricingPointLink ({len(links_to_add)} inserts)...")
        db.session.add_all(links_to_add)
        db.session.commit()


def migrate_pricings(apply_changes: bool) -> None:
    """Populate `Pricing.pricingPointId`."""
    print("Starting population of Pricing.pricingPointId...")
    venue_ids = get_venues_by_siret()
    sirets = get_pricing_sirets_to_migrate()

    updates = {}  # key = siret ; value = pricing point id to set

    for siret in sorted(sirets):
        venue_id = venue_ids.get(siret)
        if venue_id:
            updates[siret] = venue_id
        else:
            print(f"ERR: Some pricing have unknown SIRET {siret}")

    if apply_changes:
        print(f"Updating (SQL) Pricing.pricingPointId ({len(updates)} updates)...")
        for siret, pricing_point_id in updates.items():
            finance_models.Pricing.query.filter_by(siret=siret).update(
                {"pricingPointId": pricing_point_id},
                synchronize_session=False,
            )
        db.session.commit()


def create_reimbursement_point_links(apply_changes: bool) -> None:
    print("Starting creation of VenueReimbursementPointLink...")
    venues = offerers_models.Venue.query.order_by(offerers_models.Venue.id).with_entities(
        offerers_models.Venue.id,
        offerers_models.Venue.businessUnitId,
    )
    latest_business_unit_links = get_latest_business_unit_links()
    bearing_venue_ids = get_business_unit_bearing_venue_by_id()
    venues_ids_with_reimbursement_point_links = get_venue_ids_with_reimbursement_point_links()

    links_to_add = []
    now = datetime.datetime.utcnow()
    for venue in venues:
        if venue.id in venues_ids_with_reimbursement_point_links:  # already migrated
            continue

        if not venue.businessUnitId:
            continue

        reimbursement_point_id = bearing_venue_ids.get(venue.businessUnitId)
        if not reimbursement_point_id:
            print(f"ERR: venue {venue.id}: No bearing venue for business unit {venue.businessUnitId}")
            continue

        # There should be a link but we have inconsistent data. If
        # there is no link, assume that `Venue.businessUnitId` is the
        # truth and declare that the reimbursement point has been
        # linked today. It's not as important as the link with the
        # *pricing* point.
        latest_bu_link = latest_business_unit_links.get((venue.id, venue.businessUnitId))
        if latest_bu_link:
            link_timespan = [latest_bu_link.timespan.lower, latest_bu_link.timespan.upper]
            if latest_bu_link.timespan.upper is not None:
                print(
                    f"WARN: venue {venue.id}: Link with business unit {venue.businessUnitId} is inactive: incoherent data?"
                )
        else:
            print(f"WARN: venue {venue.id}: Found no business unit link, used now as the start date.")
            link_timespan = [now, None]

        links_to_add.append(
            offerers_models.VenueReimbursementPointLink(
                venueId=venue.id,
                reimbursementPointId=reimbursement_point_id,
                timespan=link_timespan,
            )
        )

    if apply_changes:
        print(f"Inserting (SQL) VenueReimbursementPointLink ({len(links_to_add)} inserts)...")
        db.session.add_all(links_to_add)
        db.session.commit()


def migrate_cashflows_and_invoices(apply_changes: bool) -> None:
    """Populate `Cashflow.reimbursementPointId` and
    `Invoice.reimbursementPointId`.
    """
    bearing_venue_ids = get_business_unit_bearing_venue_by_id()
    for model, business_units_getter in (
        (finance_models.Cashflow, get_cashflow_business_units_to_migrate),
        (finance_models.Invoice, get_invoice_business_units_to_migrate),
    ):
        model_name = model._sa_class_manager.class_.__name__  # type: ignore [attr-defined]
        updates = {}
        business_unit_ids = business_units_getter()
        print(f"Starting population of {model_name}.reimbursementPointId...")
        for business_unit_id in business_unit_ids:
            venue_id = bearing_venue_ids.get(business_unit_id)
            if venue_id:
                updates[business_unit_id] = venue_id
            else:
                print(
                    f"ERR: Some {model_name} have a business unit {business_unit_id} with no venue with the same SIRET"
                )

        if apply_changes:
            print(f"Updating (SQL) {model_name}.reimbursementPointId ({len(updates)} updates)...")
            for business_unit_id, reimbursement_point_id in updates.items():
                model.query.filter_by(businessUnitId=business_unit_id).update(  # type: ignore [attr-defined]
                    {"reimbursementPointId": reimbursement_point_id},
                    synchronize_session=False,
                )
            db.session.commit()


def main() -> None:
    apply_changes = "--apply-changes" in sys.argv[1:]
    if "--pricing-points" in sys.argv[1:]:
        print("Migrating pricing point-related data...")
        create_pricing_point_links(apply_changes=apply_changes)
        migrate_pricings(apply_changes=apply_changes)
    elif "--reimbursement-points" in sys.argv[1:]:
        print("Migrating reimbursement point-related data...")
        create_reimbursement_point_links(apply_changes=apply_changes)
        migrate_cashflows_and_invoices(apply_changes=apply_changes)
    else:
        print("Unknown command")
    print("done")


main()
