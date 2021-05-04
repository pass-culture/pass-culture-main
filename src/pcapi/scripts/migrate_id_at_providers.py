from pcapi.core.offers.models import Offer
from pcapi.flask_app import logger
from pcapi.models import db


def _get_isbn_from_idAtProviders(idAtProvider: str) -> str:
    return idAtProvider.split("@")[0]


def migrate_id_at_providers() -> None:
    OFFER_BY_PAGE = 1000

    pagination = (
        Offer.query.filter(Offer.idAtProviders.isnot(None))
        .with_entities(Offer.id, Offer.idAtProviders, Offer.idAtProvider)
        .paginate(per_page=OFFER_BY_PAGE)
    )

    has_items_to_process = True

    while has_items_to_process:
        offers = pagination.items

        offer_count = len(offers)
        logger.info("Start migration of idAtProviders to idAtProvider", extra={"offer_count": offer_count})

        mapping = []

        for offer in offers:
            isbn = _get_isbn_from_idAtProviders(offer[1])

            mapping.append(
                {
                    "id": offer[0],
                    "idAtProviders": offer[1],
                    "idAtProvider": isbn,
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
