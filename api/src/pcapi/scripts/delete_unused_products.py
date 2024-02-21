import logging
import time
from typing import Generator

import requests
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.exceptions import ImageTooSmall
from pcapi.core.offers.exceptions import UnidentifiedImage
from pcapi.core.offers.models import Product
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


"""
+---------+----------------+-----------------------------------------------------------+
| count   | lastProviderId | name                                                      |
|---------+----------------+-----------------------------------------------------------|
| 118     | 1              | à supprimer ? ex OpenAgenda                               |
| 263     | 4              | Experimentation Spreadsheet (Offres)                      |
| 2167156 | 9              | TiteLive (Epagine / Place des libraires.com)              |
| 174206  | 16             | TiteLive (Epagine / Place des libraires.com) Descriptions |
| 132140  | 17             | TiteLive (Epagine / Place des libraires.com) Thumbs       |
| 569453  | 19             | Init TiteLive (Epagine / Place des libraires.com)         |
| 137867  | 20             | Init TiteLive Descriptions                                |
| 10552   | 22             | Allociné                                                  |
| 15558   | 70             | Ciné Office                                               |
| 4326    | 71             | Boost                                                     |
| 1       | 1073           | CGR                                                       |
| 1023    | 1081           | EMS                                                       |
| 929587  | 1082           | TiteLive API Epagine                                      |
| 550     | 1097           | Allocine Products                                         |
+---------+----------------+-----------------------------------------------------------+
"""

# STAGING
PROVIDER_PRODUCT_RANGE = {
    1: {"min": None, "max": None},
    4: {"min": 1, "max": 343},
    9: {"min": None, "max": None},
    16: {"min": None, "max": None},
    17: {"min": None, "max": None},
    19: {"min": None, "max": None},
    20: {"min": None, "max": None},
    22: {"min": None, "max": None},
    70: {"min": None, "max": None},
    71: {"min": None, "max": None},
    1073: {"min": None, "max": None},
    1081: {"min": None, "max": None},
    1082: {"min": None, "max": None},
    1097: {"min": None, "max": None},
}

CHUNK_SIZE = 1000


def get_products_to_delete(product_id: int, provider_id: int) -> Generator[offers_models.Product, None, None]:
    return offers_models.Product.query.filter(
        offers_models.Product.lastProviderId == provider_id,  # pylint: disable=comparison-with-callable
        offers_models.Product.id.between(product_id, product_id + CHUNK_SIZE),
    ).options(joinedload(offers_models.Product.offers))


def execute_request(provider_id: int, min_product_id: int, max_product_id: int, dry_run: bool = True) -> None:
    print(f"Starting for {provider_id = } in range ({min_product_id}, {max_product_id})")
    start_provider = time.time()
    for chunk_start_id in range(min_product_id, max_product_id, CHUNK_SIZE):
        with transaction():
            product_to_delete = get_products_to_delete(chunk_start_id, provider_id)
            products_id_to_delete = []
            not_deleted_products = []
            for product in product_to_delete:
                print(f"{product.id = }, {len(product.offers) = }")
                must_delete_product = True
                offers = product.offers

                updated_offers = []

                for offer in offers:
                    # make_transient(offer)
                    offer.productId = None
                    db.session.add(offer)
                    # If the offer doesn't have an image but the product does
                    # Transfer the product image to the offers
                    if not offer.activeMediation and product.thumbUrl:
                        image = requests.get(product.thumbUrl, timeout=5)
                        if image.ok:
                            try:
                                mediation = offers_api.create_mediation(
                                    user=None,
                                    credit=None,
                                    offer=offer,
                                    image_as_bytes=image.content,
                                    keep_ratio=True,
                                    check_image_validity=False,
                                )
                                db.session.add(mediation)
                            except (ImageTooSmall, UnidentifiedImage) as exc:
                                # If product's image is too small, we keep the product and its thumb
                                # We can't do much for now. Not deleted product ids will be displayed at the end of the script.
                                must_delete_product = False
                                print(f"Must not delete product {product.id}: {exc}")
                            else:
                                db.session.add(mediation)
                    updated_offers.append(offer)

                # db.session.add_all(updated_offers)
                for o in updated_offers:
                    print("authorId:", o.authorId)
                    print("lastProviderId:", o.lastProviderId)
                    print("venueId:", o.venueId)

                if must_delete_product:
                    products_id_to_delete.append(product.id)
                else:
                    not_deleted_products.append(product.id)

                print(
                    f"{product.id = } / {max_product_id} ({time.time() - start_provider:.2f}s) (Estimated time {(time.time() - start_provider) / ((product.id - min_product_id or 1) / (max_product_id - min_product_id)):.2f})"
                )

            if dry_run:
                db.session.rollback()
            else:
                try:
                    offers_models.Product.query.filter(offers_models.Product.id.in_(products_id_to_delete)).delete(
                        synchronize_session=False
                    )
                except Exception as e:
                    # Handle delete errors
                    print(f"Error deleting products: {e}")

    end_provider = time.time()
    print(f"Provider {provider_id} took {end_provider - start_provider:.2f}")
    print(f"Deleted products = {products_id_to_delete}")
    print(f"Not deleted products = {not_deleted_products}")


def get_max_provider_id(provider_id: int) -> int:
    return PROVIDER_PRODUCT_RANGE[provider_id]["max"] or (
        Product.query.filter(Product.lastProviderId == provider_id)  # pylint: disable=comparison-with-callable
        .with_entities(sa.func.max(Product.id))
        .scalar()
    )


def get_min_provider_id(provider_id: int) -> int:
    return PROVIDER_PRODUCT_RANGE[provider_id]["min"] or (
        Product.query.filter(Product.lastProviderId == provider_id)  # pylint: disable=comparison-with-callable
        .with_entities(sa.func.min(Product.id))
        .scalar()
    )


def delete_unused_products(provider_id: int, dry_run: bool = True) -> None:
    execute_request(provider_id, get_min_provider_id(provider_id), get_max_provider_id(provider_id), dry_run)


if __name__ == "__main__":
    import argparse

    from pcapi.flask_app import app

    parser = argparse.ArgumentParser(description="""Determine if the script should run in dry run or not""")

    parser.add_argument(
        "--no-dry-run",
        "-n",
        help="deactivate the dry run mode",
        dest="dry_run",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--provider-id",
        "-p",
        help="choose the provider you want to delete products from",
        dest="provider_id",
        type=int,
        required=True,
    )

    args = parser.parse_args()
    with app.app_context():
        delete_unused_products(args.provider_id, args.dry_run)
