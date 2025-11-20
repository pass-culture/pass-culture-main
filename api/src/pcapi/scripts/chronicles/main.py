from typing import Any

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.chronicles.models import Chronicle
from pcapi.core.chronicles.models import ProductChronicle
from pcapi.core.offers.models import Product
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


def main() -> None:
    groups = (
        db.session.query(
            Chronicle.productIdentifierType,
            Chronicle.productIdentifier,
        )
        .distinct()
        .all()
    )

    for identifier_type, identifier in groups:
        attach_products(identifier_type, identifier)


@atomic()
def attach_products(identifier_type: Any, identifier: str) -> None:
    products = get_products(
        product_identifier_type=identifier_type,
        product_identifier=identifier,
    )
    if not products:
        return

    chronicles = (
        db.session.query(Chronicle)
        .filter(
            Chronicle.productIdentifierType == identifier_type,
            Chronicle.productIdentifier == identifier,
        )
        .options(sa_orm.joinedload(Chronicle.products))
    )

    updated_product = 0
    for chronicle in chronicles:
        for product in products:
            if product not in chronicle.products:
                updated_product += 1
                chronicle.products.append(product)
        db.session.flush()

    if updated_product:
        print(updated_product, " updated products")


def get_products(product_identifier_type: Any, product_identifier: str) -> list[Product]:
    oldest_existing_chronicle_id = (
        db.session.query(Chronicle.id)
        .filter(
            Chronicle.productIdentifierType == product_identifier_type,
            Chronicle.productIdentifier == product_identifier,
        )
        .order_by(Chronicle.id)
        .limit(1)
        .scalar()
    )

    # if it is not the first product on this products identifier, ignore the product identifier and
    # use the same products as the other chronicles
    if oldest_existing_chronicle_id:
        return (
            db.session.query(Product)
            .join(ProductChronicle, Product.id == ProductChronicle.productId)
            .filter(ProductChronicle.chronicleId == oldest_existing_chronicle_id)
            .options(sa_orm.load_only(Product.id))
            .all()
        )

    # should never happen
    raise ValueError("no chronicle found")


if __name__ == "__main__":
    app.app_context().push()
    main()
