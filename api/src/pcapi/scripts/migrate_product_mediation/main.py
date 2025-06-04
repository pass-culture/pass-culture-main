"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/jmontagnat/PC-36410-migrate-products-images/api/src/pcapi/scripts/migrate_product_mediation/main.py
"""

import argparse
import logging
import uuid

from pcapi import settings
from pcapi.app import app
from pcapi.connectors import thumb_storage
from pcapi.core import object_storage
from pcapi.core.offers.models import ImageType
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import ProductMediation
from pcapi.models import db


logger = logging.getLogger(__name__)


def migrate_product_images_to_product_mediations() -> None:
    products_with_thumbs = db.session.query(Product).filter(Product.thumbCount > 0).order_by(Product.id).yield_per(1000)

    migrated_count = 0
    skipped_existing_mediation = 0
    skipped_fetch_error = 0
    skipped_store_error = 0

    for product in products_with_thumbs:
        logger.info(
            "Processing Product ID: %s (thumbCount: %s, subcategoryId: %s)",
            product.id,
            product.thumbCount,
            product.subcategoryId,
        )
        target_image_type = ImageType.POSTER if product.subcategoryId == "SEANCE_CINE" else ImageType.RECTO
        logger.info("Target imageType for Product ID %s is %s", product.id, target_image_type.value)

        if db.session.query(ProductMediation).filter_by(productId=product.id, imageType=target_image_type).first():
            logger.info(
                "Product ID %s already has a %s ProductMediation. Skipping.", product.id, target_image_type.value
            )
            skipped_existing_mediation += 1
            continue

        image_bytes = None
        try:
            old_thumb_object_id = product.get_thumb_storage_id()
            logger.info(
                "Fetching old image for Product ID %s from: folder='%s', object_id='%s'",
                product.id,
                settings.THUMBS_FOLDER_NAME,
                old_thumb_object_id,
            )
            image_bytes_list = object_storage.get_public_object(
                folder=settings.THUMBS_FOLDER_NAME, object_id=old_thumb_object_id
            )
            if not image_bytes_list:
                logger.warning("No image data found for Product ID %s. Skipping.", product.id)
                skipped_fetch_error += 1
                continue
            image_bytes = image_bytes_list[0]
        except Exception as err:
            logger.error("Error fetching old image for Product ID %s: %s. Skipping.", product.id, err, exc_info=True)
            skipped_fetch_error += 1
            continue

        new_mediation_internal_uuid = str(uuid.uuid4())
        try:
            logger.info(
                "Storing new image for Product ID %s using create_thumb with new UUID: %s",
                product.id,
                new_mediation_internal_uuid,
            )
            thumb_storage.create_thumb(
                model_with_thumb=product,
                image_as_bytes=image_bytes,
                object_id=new_mediation_internal_uuid,
                keep_ratio=True,
            )
        except Exception as err:
            logger.error(
                "Unexpected error using create_thumb for Product ID %s: %s. Skipping.", product.id, err, exc_info=True
            )
            skipped_store_error += 1
            continue

        new_mediation = ProductMediation(
            productId=product.id,
            imageType=target_image_type,
            uuid=new_mediation_internal_uuid,
            lastProviderId=product.lastProviderId,
        )
        db.session.add(new_mediation)
        migrated_count += 1
        logger.info(
            "ProductMediation (%s) created for Product ID %s with new UUID: %s",
            target_image_type.value,
            product.id,
            new_mediation_internal_uuid,
        )

    if migrated_count > 0:
        logger.info("Migration finished. %d ProductMediations created and stored.", migrated_count)
    else:
        logger.info("Migration finished. No new ProductMediations were created.")

    if skipped_existing_mediation > 0:
        logger.info("%d products skipped (mediation already existed).", skipped_existing_mediation)
    if skipped_fetch_error > 0:
        logger.info("%d products skipped (error fetching old image).", skipped_fetch_error)
    if skipped_store_error > 0:
        logger.info("%d products skipped (error storing new image via create_thumb).", skipped_store_error)


if __name__ == "__main__":
    app.app_context().push()
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    migrate_product_images_to_product_mediations()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
