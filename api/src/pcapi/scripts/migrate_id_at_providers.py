import sqlalchemy as sa

from pcapi.core.offers.models import Offer
from pcapi.flask_app import logger
from pcapi.models import db


class OfferScript(Offer):
    __tablename__ = "offer"

    __table_args__ = {"extend_existing": True}

    idAtProvidersToMigrate = sa.Column("idAtProviders", sa.Text, nullable=True)


def _get_isbn_from_id_at_providers(idAtProvider: str) -> str:
    return idAtProvider.split("@")[0]


def migrate_id_at_providers(offer_per_page: int = 1000) -> int:
    has_items_to_process = True
    total_count_to_update = (
        OfferScript.query.filter(
            sa.not_(sa.or_(OfferScript.lastProviderId.is_(None), OfferScript.idAtProvider.isnot(None)))
        )
        .with_entities(OfferScript.id, OfferScript.idAtProvidersToMigrate, OfferScript.idAtProvider)
        .count()
    )

    local_total_count = total_count_to_update

    while has_items_to_process:

        offers = (
            OfferScript.query.filter(
                sa.not_(sa.or_(OfferScript.lastProviderId.is_(None), OfferScript.idAtProvider.isnot(None)))
            )
            .with_entities(OfferScript.id, OfferScript.idAtProvidersToMigrate, OfferScript.idAtProvider)
            .limit(offer_per_page)
        )

        current_offers_count = offers.count()
        if current_offers_count == 0:
            logger.info(
                "End of migration of idAtProviders to idAtProvider", extra={"offer_count": current_offers_count}
            )
            break

        logger.info("Start migration of idAtProviders to idAtProvider", extra={"offer_count": current_offers_count})

        mapping = []

        for offer in offers:
            isbn = _get_isbn_from_id_at_providers(offer[1])

            mapping.append(
                {
                    "id": offer[0],
                    "idAtProvider": isbn,
                }
            )

        local_total_count = local_total_count - current_offers_count

        logger.info(
            "Saving %s offers",
            current_offers_count,
            extra={"nb_left_to_update": local_total_count},
        )
        db.session.bulk_update_mappings(OfferScript, mapping)
        db.session.commit()

    return total_count_to_update
