"""
FIXME: move this to a proper Flask command.

Usage:

    $ python /tmp/move-siret.py 1234 9876 12345678901234 'lieu public, le SIRET est porté par le "Lieu administratif"' --apply-changes
"""

from pcapi.flask_app import app


app.app_context().push()

import argparse

import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


class CheckError(Exception):
    pass


def check(source_id: int, target_id: int, siret: str, override_revenue_check: bool):
    source = offerers_models.Venue.query.get(source_id)
    target = offerers_models.Venue.query.get(target_id)
    if source.managingOffererId != target.managingOffererId:
        raise CheckError(f"Source {source_id} and target {target_id} do not have the same offerer")
    offerer = target.managingOfferer
    if offerer.siren != siret[:9]:
        raise CheckError(f"SIRET {siret} does not match offerer SIREN {offerer.siren}")
    if source.siret != siret:
        raise CheckError(f"Source venue {source.id} has SIRET {source.siret}, not requested SIRET {siret}")
    if target.siret is not None:
        raise CheckError(f"Target venue {target.id} already has a siret: {target.siret}")

    if not override_revenue_check:
        # Calculate yearly revenue of target venue
        query = """
          select sum(booking.amount * booking.quantity) as "chiffre d'affaires"
          from booking
          where
            "venueId" = :target_id
            and "dateUsed" is not null
            -- On ajoute 1 heure pour la conversion UTC -> CET afin de récupérer
            -- le chiffre d'affaires de l'année en cours.
            and DATE_PART('year', "dateUsed" + interval '1 hour') = date_part('year', now() + interval '1 hour');
        """
        rows = db.session.execute(query, {"target_id": target_id}).fetchone()
        revenue = rows[0]
        if revenue and revenue > 10_000:
            raise CheckError("Target venue has an unexpectedly high yearly revenue.")


def move(source_id: int, target_id: int, siret: str, comment: str, apply_changes: bool):
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
        -- If the pricing of the target venue was the source venue before our changes,
        -- the update above will have changed the existing row. Thus the source venue
        -- now points to itself, which means that we don't need to execute this insert
        -- (and it would raise an integrity error). Hence the "do nothing" below.
        on conflict do nothing
        """,
    ]
    db.session.begin()
    for query in queries:
        db.session.execute(
            query,
            {
                "source_id": source_id,
                "target_id": target_id,
                "siret": siret,
                "comment": comment,
            },
        )
    if apply_changes:
        db.session.commit()
        print("Siret has been moved.")
    else:
        db.session.rollback()
        print("DRY RUN: NO CHANGES HAVE BEEN MADE")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_id", type=int)
    parser.add_argument("target_id", type=int)
    parser.add_argument("siret")
    parser.add_argument("comment")
    parser.add_argument("--apply-changes", default=False, action="store_true")
    parser.add_argument("--override-revenue-check", default=False, type=bool)
    args = parser.parse_args()

    try:
        check(
            source_id=args.source_id,
            target_id=args.target_id,
            siret=args.siret,
            override_revenue_check=args.override_revenue_check,
        )
    except CheckError as exc:
        print(str(exc))
        return

    move(
        source_id=args.source_id,
        target_id=args.target_id,
        siret=args.siret,
        comment=args.comment,
        apply_changes=args.apply_changes,
    )


if __name__ == "__main__":
    main()
