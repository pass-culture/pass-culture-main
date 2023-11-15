# Ce script est à usage unique.
# Il permet de mettre à jour les offres de vinyles non synchronisées pour les ajouter dans la caégorie "Vinyles".
# A supprimer après utilisation.

import argparse
import random

from sqlalchemy.orm import Query

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.search import async_index_offer_ids
from pcapi.models import db


def get_non_synchronized_vinyl_query(slug: str = "vinyl") -> Query:
    query = Offer.query.filter(
        Offer.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, Offer.name.ilike(f"%{slug}%")
    )
    return query


def update_non_synchronized_vinyl_subcategory(batch_size: int = 1000, dry_run: bool = True) -> list[int]:
    query = get_non_synchronized_vinyl_query()
    count = query.count()
    udpated_offer_ids = []

    for offer in query.yield_per(batch_size):
        offer.subcategoryId = subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        if offer.product:
            offer.product.subcategoryId = subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id
        udpated_offer_ids.append(offer.id)

    if not dry_run:
        db.session.commit()
        print("Commit successful")
    else:
        print(f"Dry run. Would have updated {count} offers.")
        db.session.rollback()

    return udpated_offer_ids


def main(dry_run: bool = True) -> None:
    offer_ids = update_non_synchronized_vinyl_subcategory(dry_run=dry_run)
    print(f"Updated {len(offer_ids)} offers")
    print("Reindexing offers")
    if not dry_run:
        async_index_offer_ids(offer_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-dry-run", action="store_true", help="Execute the script for real")

    args = parser.parse_args()

    dry_run_value = not args.no_dry_run
    main(dry_run=dry_run_value)


#### --- Testing only --- ####


def create_data(size: int = 100, name_prefix: str = "vinyl") -> None:
    from pcapi.core.offers.factories import OfferFactory

    for i in range(size):
        OfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            name=name_prefix + str(i),
            # Yeah yeah this is ugly AF, but now is not the time to fix our Offerer factory
            venue__managingOfferer__siren=random.randint(100000000, 999999999),
        )


def delete_data(name_prefix: str = "vinyl") -> None:
    Offer.query.filter(Offer.name.ilike(name_prefix + "%")).delete(synchronize_session=False)
    db.session.commit()


def test_data() -> None:
    from pcapi import settings

    if settings.ENV not in ["testing", "development"]:
        raise Exception(  # pylint: disable=broad-exception-raised
            "This script is only meant to be run in testing environment"
        )
    name_prefix = "vinyl tests "

    create_data(name_prefix=name_prefix)
    offers_to_update_query = Offer.query.filter(Offer.name.ilike(name_prefix + "%"))

    update_non_synchronized_vinyl_subcategory(batch_size=2, dry_run=False)
    assert get_non_synchronized_vinyl_query().count() == 0

    for offer in offers_to_update_query:
        assert offer.subcategoryId == subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id

    print("Test successful, deleting test data")
    delete_data(name_prefix=name_prefix)
    print("Test data deleted")
