import math

from pcapi.core.offers.models import Offer
from pcapi.flask_app import logger
from pcapi.models import db


def _get_isbn_from_idAtProviders(idAtProvider: str) -> str:
    return idAtProvider.split("@")[0]


def migrate_id_at_providers() -> None:
    OFFER_BY_PAGE = 1000
    page = 0

    offers = (
        Offer.query.filter(Offer.idAtProviders.isnot(None))
        .with_entities(Offer.id, Offer.idAtProviders, Offer.idAtProvider)
        .all()
    )

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

        if len(mapping) > OFFER_BY_PAGE:
            page += 1
            logger.info(
                "Saving 1000 offers",
                extra={
                    "page": page,
                    "total_page": math.ceil(offer_count / OFFER_BY_PAGE),
                },
            )
            db.session.bulk_update_mappings(Offer, mapping)
            mapping[:] = []

    logger.info(
        "Saving the remaining offers",
        extra={
            "page": page,
            "total_page": math.ceil(offer_count / OFFER_BY_PAGE),
        },
    )
    db.session.bulk_update_mappings(Offer, mapping)
    db.session.commit()
