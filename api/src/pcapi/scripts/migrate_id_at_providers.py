import sqlalchemy as sa

from pcapi.core.offers.models import Offer
from pcapi.flask_app import logger
from pcapi.models import db


class OfferScript(Offer):
    __tablename__ = "offer"

    __table_args__ = {"extend_existing": True}

    idAtProvidersToMigrate = sa.Column("idAtProviders", sa.Text, nullable=True)


def _get_isbn_from_idAtProviders(idAtProvider: str) -> str:
    return idAtProvider.split("@")[0]


def migrate_id_at_providers() -> None:
    OFFER_BY_PAGE = 1000

    pagination = (
        OfferScript.query.filter(OfferScript.idAtProvidersToMigrate.isnot(None))
        .filter(OfferScript.idAtProvider.is_(None))
        .with_entities(OfferScript.id, OfferScript.idAtProvidersToMigrate, OfferScript.idAtProvider)
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
        db.session.bulk_update_mappings(OfferScript, mapping)

        if pagination.has_next:
            pagination = pagination.next()
        else:
            break

    db.session.commit()
