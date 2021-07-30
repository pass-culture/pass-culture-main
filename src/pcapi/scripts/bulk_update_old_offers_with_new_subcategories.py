from sqlalchemy.orm import Query
from pcapi.core.categories.conf import get_subcategory_from_type
from pcapi.models import Offer
from pcapi.models import db


def bulk_update_old_offers_with_new_subcategories(batch_size: int = 10000) -> None:
    empty_subcategory_count = find_empty_subcategory_offers().count()

    updated_total = 0
    empty_subcategory_offers_ids = find_empty_subcategory_offers_ids().limit(batch_size).all()
    max_id = empty_subcategory_offers_ids[-1][0]

    db.session.commit()

    while empty_subcategory_offers_ids:
        updated = (
            Offer.query.filter(Offer.id <= max_id)
            .filter(Offer.id.in_(empty_subcategory_offers_ids))
            .update(
                {"subcategoryId": get_subcategory_from_type(Offer.offer_type, Offer.venue.is_virtual)},
                synchronize_session=False,
            )
        )

        updated_total += updated
        empty_subcategory_offers_ids = find_empty_subcategory_offers_ids().limit(batch_size).all()
        if empty_subcategory_offers_ids:
            max_id = empty_subcategory_offers_ids[-1][0]


def find_empty_subcategory_offers() -> Query:
    return Offer.query.filter(Offer.subcategoryId.is_(None)).all()


def find_empty_subcategory_offers_ids() -> Query:
    return find_empty_subcategory_offers().order_by(Offer.id).with_entities(Offer.id)
