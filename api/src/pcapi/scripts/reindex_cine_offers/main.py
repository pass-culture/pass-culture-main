from contextlib import contextmanager
import time
import typing

from pcapi.app import app
from pcapi.core import search
from pcapi.core.categories import subcategories_v2
from pcapi.core.offers.models import Offer

BATCH_SIZE = 1000


@contextmanager
def timed():
    start = time.time()
    yield
    end = time.time()
    print(f"Executed in {end - start:.2f}s")


@timed()
def get_cine_offer_ids() -> typing.Generator[int, None, None]:
    query = Offer.query.filter(
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
    ).with_entities(Offer.id)
    yield from query.yield_per(BATCH_SIZE)


@timed()
def reindex_cine_offers() -> None:
    batch = []
    for offer_id_row in get_cine_offer_ids():
        batch.append(offer_id_row[0])
        if len(batch) >= BATCH_SIZE:
            search.reindex_offer_ids(batch)
            batch = []

    search.reindex_offer_ids(batch)

    print("reindex_offers", end=" ")


with app.app_context():
    reindex_cine_offers()
