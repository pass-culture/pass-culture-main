from contextlib import contextmanager
import time

from pcapi.app import app
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.search import IndexationReason
from pcapi.core.search import async_index_offer_ids
from pcapi.repository import db


@contextmanager
def transaction(dry_run: bool):
    try:
        yield
        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@contextmanager
def timed():
    start = time.time()
    yield
    end = time.time()
    print(f"Executed in {end - start:.2f}s")


@timed()
def get_allocine_products() -> list[Product]:
    products = Product.query.filter(
        Product.extraData["visa"].is_not(None),
        Product.extraData["allocineId"].is_not(None),
    ).all()
    print("get_allocine_products", end=" ")
    return products


@timed()
def get_attachable_offers(visas: list[str]) -> list[Offer]:
    offers = Offer.query.filter(Offer.extraData["visa"].astext.in_(visas)).all()
    print("get_attachable_offers", end=" ")
    return offers


@timed()
def catch_up_orphan_cine_offers(dry_run: bool) -> list[Offer]:
    products = get_allocine_products()
    known_visas = {product.extraData["visa"]: product for product in products if product.extraData.get("visa")}
    print(f"{len(known_visas)} known visa")
    offers = get_attachable_offers(known_visas)
    print(f"{len(offers)} attachable offers")

    with transaction(dry_run):
        for offer in offers:
            product = known_visas[offer.extraData["visa"]]
            offer.durationMinutes = product.durationMinutes
            offer.description = product.description
            offer.extraData.update(product.extraData)
            offer.name = product.name
            offer.product = product

        db.session.add_all(offers)

    async_index_offer_ids([offer.id for offer in offers], IndexationReason.OFFER_REINDEXATION)

    print("catch_up_orphan_cine_offers", end=" ")


def main(*args) -> None:
    dry_run = len(args) == 2 and args[1] == "--no-dry-run"
    if dry_run:
        print("This is a dry run")
    else:
        print("WARNING: This is not a dry run")

    with app.app_context():
        catch_up_orphan_cine_offers(dry_run)


if __name__ == "__main__":
    import sys

    main(*sys.argv)
