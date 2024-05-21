from contextlib import suppress

import sqlalchemy as sa

import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.categories.subcategories_v2 import Subcategory
from pcapi.core.offers.models import Product
from pcapi.models import db
from pcapi.scripts.integration.eans_data import EANS
from pcapi.scripts.integration.eans_data import EAN_CAT


def get_known_eans() -> set[str]:
    query = Product.query.filter(Product.extraData != None).options(sa.orm.load_only(Product.extraData))
    eans = set()

    for product in query.yield_per(2_000):
        with suppress(TypeError, KeyError):
            eans.add(product.extraData["ean"])

    return eans


def get_subcategory_from_ean_type(ean_type: EAN_CAT) -> Subcategory:
    return {
        EAN_CAT.CDS: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD,
        EAN_CAT.VINYLES: subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE,
        EAN_CAT.EBOOKS: subcategories.LIVRE_NUMERIQUE,
        EAN_CAT.UNELIGIBLE_BOOKS: subcategories.LIVRE_PAPIER,
        EAN_CAT.ELIGIBLE_BOOKS: subcategories.LIVRE_PAPIER,
    }[ean_type]


def fill_missing_eans() -> None:
    known_eans = get_known_eans()

    for idx, (ean_type, eans) in enumerate(EANS.items()):
        missing_eans = eans - known_eans
        subcategory = get_subcategory_from_ean_type(ean_type)

        for ean in missing_eans:
            db.session.add(
                Product(name=f"{subcategory.pro_label} #{idx}", subcategoryId=subcategory.id, extraData={"ean": ean})
            )

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            print(f"Could not commit for {ean_type}")
            raise
