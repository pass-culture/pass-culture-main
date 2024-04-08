import logging
import time
from typing import Generator

from sqlalchemy.orm import joinedload

from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

CHUNK_SIZE = 500


def products_to_delete(min_id: int) -> Generator[offers_models.Product, None, None]:
    return (
        offers_models.Product.query.filter(
            offers_models.Product.lastProviderId.is_(None),
            offers_models.Product.idAtProviders.is_(None),
            offers_models.Product.id > min_id,
        )
        .options(joinedload(offers_models.Product.offers))
        .limit(CHUNK_SIZE)
        .all()
    )


def delete_unused_products(min_id: int) -> None:
    current_batch_idx = 0
    print(f"Starting from {min_id}")
    start_time = time.time()
    while products := products_to_delete(min_id):
        current_batch_idx += 1
        print(f"Starting - batch {current_batch_idx}")

        with transaction():
            products_id_to_delete = []
            for product in products:
                offers = product.offers

                for offer in offers:
                    offer.productId = None

                db.session.add_all(offers)
                products_id_to_delete.append(product.id)

            offers_models.Product.query.filter(offers_models.Product.id.in_(products_id_to_delete)).delete(
                synchronize_session=False
            )

        batch_time = time.time() - start_time
        print(f"Ending - batch {current_batch_idx} - {batch_time:.2f} s")
        start_time = time.time()


if __name__ == "__main__":
    import argparse

    from pcapi.flask_app import app

    parser = argparse.ArgumentParser(description="""Delete products with null idAtProviders""")

    parser.add_argument("--min-id", type=int, default=0, help="minimum product id")

    args = parser.parse_args()
    with app.app_context():
        delete_unused_products(args.min_id)
