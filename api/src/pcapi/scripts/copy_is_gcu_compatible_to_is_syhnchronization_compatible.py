import logging

from sqlalchemy import and_

from pcapi.models import Product
from pcapi.models import db


logger = logging.getLogger(__name__)


def copy_is_gcu_compatible_to_is_synchronization_compatible(batch_size: int = 1000) -> None:
    logger.info("Copy isGcuCompatible to isSynchronizationCompatible")
    max_product_id = Product.query.order_by(Product.id.desc()).first().id

    for current_start_index in range(0, max_product_id, batch_size):
        query_to_update = Product.query.filter(
            and_(Product.id > current_start_index, Product.id <= (current_start_index + batch_size))
        )
        query_to_update.update({"isSynchronizationCompatible": Product.isGcuCompatible}, synchronize_session=False)

        db.session.commit()

    query_to_update_new_added_products = Product.query.filter(Product.id >= max_product_id)
    query_to_update_new_added_products.update(
        {"isSynchronizationCompatible": Product.isGcuCompatible}, synchronize_session=False
    )
    db.session.commit()

    inconsistent_products_count = Product.query.filter(
        Product.isGcuCompatible != Product.isSynchronizationCompatible
    ).count()
    if inconsistent_products_count != 0:
        logger.info(
            "Inconsistent data in product table, isGcuCompatible and isSynchronizationCompatible should be equal for each row",
            extra={"inconsistent_products_count": inconsistent_products_count},
        )

    logger.info("Finished copy isGcuCompatible to isSynchronizationCompatible")
