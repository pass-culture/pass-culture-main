from contextlib import contextmanager
import time
from pcapi.core import search
from pcapi.core.categories import subcategories_v2
from pcapi.core.offers.models import Offer


@contextmanager
def timed():
    start = time.time()
    yield
    end = time.time()
    print(f"Executed in {end - start:.2f}s")


@timed()
def get_cine_offer_ids() -> list[Offer]:
    offer_ids = [
        offer[0]
        for offer in Offer.query.filter(
            Offer.subcategoryId.in_(
                (
                    subcategories_v2.SUPPORT_PHYSIQUE_FILM.id,
                    subcategories_v2.VOD.id,
                    subcategories_v2.ABO_PLATEFORME_VIDEO.id,
                    subcategories_v2.AUTRE_SUPPORT_NUMERIQUE.id,
                    subcategories_v2.CARTE_CINE_MULTISEANCES.id,
                    subcategories_v2.CARTE_CINE_ILLIMITE.id,
                    subcategories_v2.SEANCE_CINE.id,
                    subcategories_v2.EVENEMENT_CINE.id,
                    subcategories_v2.FESTIVAL_CINE.id,
                    subcategories_v2.CINE_VENTE_DISTANCE.id,
                    subcategories_v2.CINE_PLEIN_AIR.id,
                )
            ),
            Offer.isActive.is_(True),
        )
        .with_entities(Offer.id)
        .limit(1)
    ]
    print(f"get_cine_offer_ids", end=" ")
    return offer_ids


@timed()
def reindex_offers(offer_ids: list[int]) -> None:
    batch_size = 1000
    start = 0
    while start < len(offer_ids):
        batch = offer_ids[start : start + batch_size]
        search.reindex_offer_ids(batch)
        start += batch_size

    print(f"reindex_offers", end=" ")


def main() -> None:
    offer_ids = get_cine_offer_ids()
    reindex_offers(offer_ids)


if __name__ == "__main__":
    main()
