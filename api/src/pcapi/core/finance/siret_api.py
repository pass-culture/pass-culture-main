from collections import defaultdict
import datetime
from decimal import Decimal

import sqlalchemy as sa

import pcapi.core.history.models as history_models
from pcapi.core.offerers import api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
import pcapi.utils.db as db_utils

from . import models


# Revenue above which we refuse to do any change without an explicit
# validation from the accounting department.
YEARLY_REVENUE_THRESHOLD = 10_000


class CheckError(Exception):
    pass


def get_yearly_revenue(venue_id: int) -> Decimal:
    # Calculate yearly revenue of a venue
    query = """
      select sum(booking.amount * booking.quantity) as "chiffre d'affaires"
      from booking
      where
        "venueId" = :venue_id
        and "dateUsed" is not null
        -- Add 1 hour for UTC -> CET conversion
        and date_part('year', "dateUsed" + interval '1 hour') = date_part('year', now() + interval '1 hour');
    """
    rows = db.session.execute(query, {"venue_id": venue_id}).fetchone()
    return rows[0]


def check_can_move_siret(
    source: offerers_models.Venue, target: offerers_models.Venue, siret: str, override_revenue_check: bool
) -> None:
    if source.managingOffererId != target.managingOffererId:
        raise CheckError(f"Source {source.id} and target {target.id} do not have the same offerer")
    offerer = target.managingOfferer
    if offerer.siren != siret[:9]:
        raise CheckError(f"SIRET {siret} does not match offerer SIREN {offerer.siren}")
    if source.siret != siret:
        raise CheckError(f"Source venue {source.id} has SIRET {source.siret}, not requested SIRET {siret}")
    if target.siret is not None:
        raise CheckError(f"Target venue {target.id} already has a siret: {target.siret}")

    if not override_revenue_check:
        revenue = get_yearly_revenue(target.id)
        if revenue and revenue >= YEARLY_REVENUE_THRESHOLD:
            raise CheckError(f"Target venue has an unexpectedly high yearly revenue: {revenue}")


def move_siret(
    source_venue: offerers_models.Venue,
    target_venue: offerers_models.Venue,
    siret: str,
    comment: str,
    override_revenue_check: bool = False,
    author_user_id: int | None = None,
) -> None:
    check_can_move_siret(
        source=source_venue,
        target=target_venue,
        siret=siret,
        override_revenue_check=override_revenue_check,
    )

    db.session.rollback()  # discard any previous transaction to start a fresh new one.
    queries = [
        """
        update finance_event
        set "pricingPointId" = :target_id
        where "pricingPointId" = :source_id
        """,
        """
        update pricing
        set "pricingPointId" = :target_id
        where "pricingPointId" = :source_id
        """,
        """
        update venue_pricing_point_link
        set "pricingPointId" = :target_id
        where "pricingPointId" = :source_id
        """,
        """
        update venue
        set siret = NULL, comment = :comment
        where id = :source_id and siret = :siret
        """,
        """
        update venue
        set siret = :siret, comment = NULL
        where id = :target_id and siret IS NULL
        """,
        """
        insert into venue_pricing_point_link ("venueId", "pricingPointId", timespan)
        values (
          :target_id,
          :target_id,
          tsrange(now()::timestamp, NULL, '[)')
        )
        -- If the pricing point of the target venue was the source venue before our changes,
        -- the update above will have changed the existing row. Thus the source venue
        -- now points to itself, which means that we don't need to execute this insert
        -- (and it would raise an integrity error). Hence the "do nothing" below.
        on conflict do nothing
        """,
    ]

    try:
        db.session.begin()
        for query in queries:
            db.session.execute(
                query,
                {
                    "source_id": source_venue.id,
                    "target_id": target_venue.id,
                    "siret": siret,
                    "comment": comment,
                },
            )

        # Add actions in the history for both venues to track who/when it was changed
        db.session.add(
            history_models.ActionHistory(
                actionType=history_models.ActionType.INFO_MODIFIED,
                authorUserId=author_user_id,
                offererId=source_venue.managingOffererId,
                venueId=source_venue.id,
                comment=comment,
                extraData={
                    "modified_info": {
                        "siret": {"old_info": siret, "new_info": None},
                    }
                },
            )
        )
        db.session.add(
            history_models.ActionHistory(
                actionType=history_models.ActionType.INFO_MODIFIED,
                authorUserId=author_user_id,
                offererId=target_venue.managingOffererId,
                venueId=target_venue.id,
                comment=comment,
                extraData={
                    "modified_info": {
                        "siret": {"old_info": None, "new_info": siret},
                    }
                },
            )
        )
    except Exception:
        db.session.rollback()
        raise

    db.session.commit()


def has_pending_pricings(pricing_point: offerers_models.Venue) -> bool:
    return db.session.query(
        models.Pricing.query.filter_by(
            pricingPoint=pricing_point,
            status=models.PricingStatus.PENDING,
        ).exists()
    ).scalar()


def _delete_ongoing_pricings(venue: offerers_models.Venue) -> None:
    queries = (
        # Delete all ongoing pricings (and related pricing lines),
        # except pending ones. The corresponding bookings will be
        # priced again once a new pricing point has been selected for
        # their venues.
        """
        update finance_event
        set
          "pricingPointId" = NULL,
          "pricingOrderingDate" = NULL,
          status = :pending_finance_event_status
        where
          "pricingPointId" = :venue_id
          and id in (
            select "eventId" from pricing
            where "pricingPointId" = :venue_id and status = :validated_pricing_status
          )
        """,
        """
        delete from pricing_line
        where "pricingId" in (
          select id from pricing
          where "pricingPointId" = :venue_id and status = :validated_pricing_status
        )
        """,
        """
        delete from pricing
        where "pricingPointId" = :venue_id and status = :validated_pricing_status
        """,
    )

    for query in queries:
        db.session.execute(
            query,
            {
                "venue_id": venue.id,
                "pending_finance_event_status": models.FinanceEventStatus.PENDING.value,
                "validated_pricing_status": models.PricingStatus.VALIDATED.value,
            },
        )


def check_can_remove_siret(
    venue: offerers_models.Venue,
    comment: str,
    override_revenue_check: bool = False,
    check_offerer_has_other_siret: bool = False,
) -> None:
    if not venue.siret:
        raise CheckError("Ce lieu n'a pas de SIRET")

    if check_offerer_has_other_siret:
        if not any(
            offerer_venue.siret
            for offerer_venue in venue.managingOfferer.managedVenues
            if offerer_venue.siret and offerer_venue.id != venue.id
        ):
            raise CheckError("La structure gérant ce lieu n'a pas d'autre lieu avec SIRET")

    if not comment:
        raise CheckError("Le commentaire est obligatoire")

    # Deleting the SIRET implies deleting non-final pricings (see
    # `remove_siret()`). If the venue has pending pricings, it means
    # we want to block them from being reimbursed. If those pricings
    # were deleted, they would be recreated under the "validated"
    # status and they would not be blocked anymore.
    if has_pending_pricings(venue):
        raise CheckError("Ce lieu a des valorisations en attente")

    if not override_revenue_check:
        revenue = get_yearly_revenue(venue.id)
        if revenue and revenue >= YEARLY_REVENUE_THRESHOLD:
            raise CheckError(f"Ce lieu a un chiffre d'affaires de l'année élevé : {revenue}")


def remove_siret(
    venue: offerers_models.Venue,
    comment: str,
    apply_changes: bool = False,
    override_revenue_check: bool = False,
    new_pricing_point_id: int | None = None,
    author_user_id: int | None = None,
    new_db_session: bool = True,
) -> None:
    check_can_remove_siret(venue, comment, override_revenue_check)
    old_siret = venue.siret
    now = datetime.datetime.utcnow()

    new_siret: str | None = None
    if new_pricing_point_id:
        new_pricing_point_venue: offerers_models.Venue = offerers_models.Venue.query.filter(
            offerers_models.Venue.id == new_pricing_point_id,
            offerers_models.Venue.managingOffererId == venue.managingOffererId,
            offerers_models.Venue.siret.is_not(None),
        ).one_or_none()
        if not new_pricing_point_venue:
            raise CheckError("Le nouveau point de valorisation doit être un lieu avec SIRET sur la même structure")
        new_siret = new_pricing_point_venue.siret

    with db.session.no_autoflush:  # do not flush anything before commit
        if new_db_session:
            db.session.rollback()  # discard any previous transaction to start a fresh new one.
            db.session.begin()

        try:
            modified_info_by_venue: dict[int, dict[str, dict]] = defaultdict(dict)

            venue.siret = None
            venue.comment = comment
            db.session.add(venue)
            modified_info_by_venue[venue.id]["siret"] = {"old_info": old_siret, "new_info": None}

            # must be called before link_venue_to_pricing_point() so that new pricing point is set properly
            _delete_ongoing_pricings(venue)

            # End all active links to this pricing point
            pricing_point_links = (
                offerers_models.VenuePricingPointLink.query.filter(
                    offerers_models.VenuePricingPointLink.pricingPointId == venue.id,
                    offerers_models.VenuePricingPointLink.timespan.contains(now),
                )
                .options(sa.orm.joinedload(offerers_models.VenuePricingPointLink.venue))
                .all()
            )
            for pricing_point_link in pricing_point_links:
                # Replace with new pricing point (when provided), only for the venue which lost its SIRET
                if new_pricing_point_id and pricing_point_link.venueId == venue.id:
                    offerers_api.link_venue_to_pricing_point(
                        pricing_point_link.venue, new_pricing_point_id, force_link=True, commit=False
                    )
                    modified_info_by_venue[pricing_point_link.venueId]["pricingPointSiret"] = {
                        "old_info": old_siret,
                        "new_info": new_siret,
                    }
                else:
                    pricing_point_link.timespan = db_utils.make_timerange(pricing_point_link.timespan.lower, end=now)
                    db.session.add(pricing_point_link)
                    modified_info_by_venue[pricing_point_link.venueId]["pricingPointSiret"] = {
                        "old_info": old_siret,
                        "new_info": None,
                    }

            for modified_venue_id, modified_info in modified_info_by_venue.items():
                db.session.add(
                    history_models.ActionHistory(
                        actionType=history_models.ActionType.INFO_MODIFIED,
                        authorUserId=author_user_id,
                        offererId=venue.managingOffererId,
                        venueId=modified_venue_id,
                        comment=comment,
                        extraData={"modified_info": modified_info},
                    )
                )

        except Exception:
            db.session.rollback()
            raise

        if apply_changes:
            db.session.commit()
        else:
            db.session.rollback()


def check_can_remove_pricing_point(
    venue: offerers_models.Venue,
    override_revenue_check: bool = False,
) -> None:
    if venue.siret:
        raise CheckError("Vous ne pouvez supprimer le point de valorisation d'un lieu avec SIRET")

    if not venue.current_pricing_point:
        raise CheckError("Ce lieu n'a pas de point de valorisation actif")

    # Same conditions as in `check_can_remove_siret`
    if has_pending_pricings(venue):
        raise CheckError("Ce lieu a des valorisations en attente")
    if not override_revenue_check:
        revenue = get_yearly_revenue(venue.id)
        if revenue and revenue >= YEARLY_REVENUE_THRESHOLD:
            raise CheckError(f"Ce lieu a un chiffre d'affaires de l'année élevé : {revenue}")


def remove_pricing_point_link(
    venue: offerers_models.Venue,
    comment: str,
    apply_changes: bool = False,
    override_revenue_check: bool = False,
    author_user_id: int | None = None,
) -> None:
    check_can_remove_pricing_point(venue, override_revenue_check)

    now = datetime.datetime.utcnow()

    with db.session.no_autoflush:  # do not flush anything before commit
        try:
            # End this pricing point
            pricing_point_link = venue.current_pricing_point_link
            assert pricing_point_link
            pricing_point_link.timespan = db_utils.make_timerange(pricing_point_link.timespan.lower, end=now)
            db.session.add(pricing_point_link)
            modified_info = {"pricingPointSiret": {"old_info": pricing_point_link.pricingPoint.siret, "new_info": None}}

            _delete_ongoing_pricings(venue)

            db.session.add(
                history_models.ActionHistory(
                    actionType=history_models.ActionType.INFO_MODIFIED,
                    authorUserId=author_user_id,
                    offererId=venue.managingOffererId,
                    venueId=venue.id,
                    comment=comment,
                    extraData={"modified_info": modified_info},
                )
            )

        except Exception:
            db.session.rollback()
            raise

        if apply_changes:
            db.session.commit()
        else:
            db.session.rollback()
