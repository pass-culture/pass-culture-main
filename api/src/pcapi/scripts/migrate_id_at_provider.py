from pcapi.core.offers.models import Offer
from pcapi.flask_app import logger
from pcapi.models import db


def migrate_id_at_provider() -> None:
    OFFER_BY_PAGE = 1000

    pagination = (
        Offer.query.filter(Offer.idAtProvider.isnot(None))
        .with_entities(Offer.id, Offer.idAtProviders, Offer.idAtProvider)
        .paginate(per_page=OFFER_BY_PAGE)
    )

    has_items_to_process = True

    while has_items_to_process:
        offers = pagination.items

        offer_count = len(offers)
        logger.info("Start migration of idAtProvider to idAtProviders", extra={"offer_count": offer_count})

        mapping = []

        for offer in offers:
            mapping.append(
                {
                    "id": offer[0],
                    "idAtProviders": offer.idAtProvider,
                }
            )

        logger.info(
            "Saving %s offers",
            offer_count,
            extra={
                "page": pagination.page,
                "total_page": pagination.pages,
            },
        )
        db.session.bulk_update_mappings(Offer, mapping)

        if pagination.has_next:
            pagination = pagination.next()
        else:
            break

    db.session.commit()
