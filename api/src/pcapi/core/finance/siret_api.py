from decimal import Decimal

import pcapi.core.history.models as history_models
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db

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
    apply_changes: bool = False,
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

    if apply_changes:
        db.session.commit()
    else:
        db.session.rollback()


def has_pending_pricings(pricing_point: offerers_models.Venue) -> bool:
    return db.session.query(
        models.Pricing.query.filter_by(
            pricingPoint=pricing_point,
            status=models.PricingStatus.PENDING,
        ).exists()
    ).scalar()


def check_can_remove_siret(
    venue: offerers_models.Venue,
    comment: str,
    override_revenue_check: bool = False,
) -> None:
    if not comment:
        raise CheckError("Comment is required")
    # Deleting the SIRET implies deleting non-final pricings (see
    # `remove_siret()`). If the venue has pending pricings, it means
    # we want to block them from being reimbursed. If those pricings
    # were deleted, they would be recreated under the "validated"
    # status and they would not be blocked anymore.
    if has_pending_pricings(venue):
        raise CheckError("Venue has pending pricings")
    if not override_revenue_check:
        revenue = get_yearly_revenue(venue.id)
        if revenue and revenue >= YEARLY_REVENUE_THRESHOLD:
            raise CheckError(f"Venue has an unexpectedly high yearly revenue: {revenue}")


def remove_siret(
    venue: offerers_models.Venue,
    comment: str,
    apply_changes: bool = False,
    override_revenue_check: bool = False,
    author_user_id: int | None = None,
) -> None:
    if not venue.siret:
        return
    check_can_remove_siret(venue, comment, override_revenue_check)
    old_siret = venue.siret

    db.session.rollback()  # discard any previous transaction to start a fresh new one.

    queries = (
        """
        update venue
        set siret = NULL, comment = :comment
        where id = :venue_id
        """,
        # End all links to this pricing point
        """
        update venue_pricing_point_link
        set timespan = tsrange(lower(timespan), now()::timestamp, '[)')
        where "pricingPointId" = :venue_id
        """,
        # Delete all ongoing pricings (and related pricing lines),
        # except pending ones. The corresponding bookings will be
        # priced again once a new pricing point has been selected for
        # their venues.
        """
        update finance_event
        set
          "pricingPointId" = NULL,
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
    try:
        db.session.begin()
        for query in queries:
            db.session.execute(
                query,
                {
                    "venue_id": venue.id,
                    "comment": comment,
                    "pending_finance_event_status": models.FinanceEventStatus.PENDING.value,
                    "validated_pricing_status": models.PricingStatus.VALIDATED.value,
                },
            )

        db.session.add(
            history_models.ActionHistory(
                actionType=history_models.ActionType.INFO_MODIFIED,
                authorUserId=author_user_id,
                offererId=venue.managingOffererId,
                venueId=venue.id,
                comment=comment,
                extraData={
                    "modified_info": {
                        "siret": {"old_info": old_siret, "new_info": None},
                    }
                },
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

    old_pricing_point_siret = venue.current_pricing_point.siret  # type: ignore [union-attr]
    old_reimbursement_point_siret = (
        venue.current_reimbursement_point.siret if venue.current_reimbursement_point else None
    )

    queries = (
        # End this pricing point
        """
        update venue_pricing_point_link
        set timespan = tsrange(lower(timespan), now()::timestamp, '[)')
        where "venueId" = :venue_id and "pricingPointId" = :current_pricing_point_id
        and timespan @> now()::timestamp
        """,
        # End the reimbursement point
        """
        update venue_reimbursement_point_link
        set timespan = tsrange(lower(timespan), now()::timestamp, '[)')
        where "venueId" = :venue_id and timespan @> now()::timestamp
        """,
        # Delete all ongoing pricings (and related pricing lines),
        # except pending ones. The corresponding bookings will be
        # priced again once a new pricing point has been selected for
        # their venues.
        """
        update finance_event
        set
          "pricingPointId" = NULL,
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
    try:
        for query in queries:
            db.session.execute(
                query,
                {
                    "venue_id": venue.id,
                    "current_pricing_point_id": venue.current_pricing_point.id,  # type: ignore [union-attr]
                    "pending_finance_event_status": models.FinanceEventStatus.PENDING.value,
                    "validated_pricing_status": models.PricingStatus.VALIDATED.value,
                },
            )

        modified_info = {"pricingPointSiret": {"old_info": old_pricing_point_siret, "new_info": None}}
        if old_reimbursement_point_siret:
            modified_info["reimbursementPointSiret"] = {"old_info": old_reimbursement_point_siret, "new_info": None}

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
