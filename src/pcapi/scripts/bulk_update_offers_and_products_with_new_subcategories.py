from datetime import datetime

from pcapi.core.categories.conf import get_subcategory_from_type
from pcapi.models import EventType
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import ThingType
from pcapi.models.db import db


def bulk_update_old_offers_with_new_subcategories(batch_size: int = 10_000) -> None:
    all_types = [str(t) for t in list(ThingType) + list(EventType) if str(t) != "ThingType.LIVRE_EDITION"]
    all_types.append("ThingType.LIVRE_EDITION")
    for offer_type in all_types:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] >>> Now updating Offers of type={offer_type} <<<\n")
        count = 0
        query = Offer.query.filter(Offer.subcategoryId.is_(None)).filter(Offer.type == offer_type).limit(batch_size)
        empty_subcategory_offers = query.all()
        while empty_subcategory_offers:
            mappings = []
            print(f"[{datetime.now().strftime('%H:%M:%S')}]Updating batch #{count}")
            for offer in empty_subcategory_offers:
                mappings.append(
                    {"id": offer.id, "subcategoryId": get_subcategory_from_type(offer.type, offer.isDigital)}
                )
            db.session.bulk_update_mappings(Offer, mappings)
            db.session.commit()
            empty_subcategory_offers = query.all()
            count += 1


def bulk_update_products_with_subcategories(batch_size: int = 10_000) -> None:
    count = 0
    query = Product.query.filter(Product.subcategoryId.is_(None)).limit(batch_size)
    empty_subcategory_products = query.all()
    while empty_subcategory_products:
        mappings = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}]Updating batch #{count}")
        for product in empty_subcategory_products:
            mappings.append(
                {"id": product.id, "subcategoryId": get_subcategory_from_type(product.type, product.isDigital)}
            )
        db.session.bulk_update_mappings(Product, mappings)
        db.session.commit()
        empty_subcategory_products = query.all()
        count += 1
