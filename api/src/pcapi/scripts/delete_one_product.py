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


# STAGING
PROVIDER_IDS = [22, 70, 71, 1073, 1081]

CHUNK_SIZE = 1000


def get_products_to_delete(product_id: int, provider_id: int) -> Generator[offers_models.Product, None, None]:
    query = offers_models.Product.query.filter(
        offers_models.Product.lastProviderId == provider_id,  # pylint: disable=comparison-with-callable
        offers_models.Product.id.between(product_id, product_id + CHUNK_SIZE),
    ).options(joinedload(offers_models.Product.offers))
    for product in query:
        yield product


def execute_request(
    provider_id: int, min_provider_id: int, max_product_id_for_provider: int, dry_run: bool = True
) -> None:
    print(f"Starting for {provider_id = }")
    start_provider = time.time()
    with transaction():
        products = Product.query.filter(
            Product.id > 2793848 - 5000,
            Product.id < 2793848 + 5000,
            Product.lastProviderId == 22,
        ).all()
        product_to_delete = products
        print(f"{len(products) = }")
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
                # If the offer doesn't have an image but the product does
                # Transfer the product image to the offers
                if not offer.activeMediation and product.thumbUrl:
                    image = requests.get(product.thumbUrl, timeout=5)
                    if image.ok:
                        try:
                            mediation = offers_api.create_mediation(
                                user=None, credit=None, offer=offer, image_as_bytes=image.content, keep_ratio=True
                            )
                            db.session.add(mediation)
                        except (ImageTooSmall, UnidentifiedImage):
                            # If product's image is too small, we keep the product and its thumb
                            # We can't do much for now. Not deleted product ids will be displayed at the end of the script.
                            must_delete_product = False
                        else:
                            db.session.add(mediation)
                updated_offers.append(offer)

            db.session.add_all(updated_offers)
            for o in updated_offers:
                print("authorId:", o.authorId)
                print("lastProviderId:", o.lastProviderId)
                print("venueId:", o.venueId)

            if must_delete_product:
                products_id_to_delete.append(product.id)
            else:
                not_deleted_products.append(product.id)

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
    return (
        Product.query.filter(Product.lastProviderId == provider_id)  # pylint: disable=comparison-with-callable
        .with_entities(sa.func.max(Product.id))
        .scalar()
    )


def get_min_provider_id(provider_id: int) -> int:
    return (
        Product.query.filter(Product.lastProviderId == provider_id)  # pylint: disable=comparison-with-callable
        .with_entities(sa.func.min(Product.id))
        .scalar()
    )


def delete_unused_products(dry_run: bool = True) -> None:
    execute_request(22, 0, 0, dry_run)
