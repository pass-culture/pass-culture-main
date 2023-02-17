from decimal import Decimal

import pcapi.core.history.models as history_models
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


class CheckError(Exception):
    pass


def get_yearly_revenue(venue_id: int) -> Decimal:
    # Calculate yearly revenue of target venue
    query = """
      select sum(booking.amount * booking.quantity) as "chiffre d'affaires"
      from booking
      where
        "venueId" = :venue_id
        and "dateUsed" is not null
        -- On ajoute 1 heure pour la conversion UTC -> CET afin de récupérer
        -- le chiffre d'affaires de l'année en cours.
        and DATE_PART('year', "dateUsed" + interval '1 hour') = date_part('year', now() + interval '1 hour');
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
        if revenue and revenue > 10_000:
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
