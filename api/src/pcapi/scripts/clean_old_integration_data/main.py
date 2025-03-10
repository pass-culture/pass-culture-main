import argparse
import logging

import psycopg2
import sqlalchemy as sa

from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


_REPORT_EVERY = 10_000
_BATCH_SIZE = 500
_MIN_ID = 1
_MAX_ID = 266_349_987
_LEGACY_API_PROVIDERS_IDS = [
    15,  # TiteLive Stocks (Epagine / Place des libraires.com)
    59,  # Praxiel/Inférence
    58,  # FNAC
    23,  # www.leslibraires.fr
    66,  # Decitre
    63,  # Librisoft
    68,  # TMIC-Ellipses
    65,  # Mollat
    67,  # CDI-Bookshop
]


def _get_next_offers_ids(last_id: int) -> list[int]:
    nb_retry = 3

    while True:
        try:
            return [
                offer_id
                for offer_id, in Offer.query.filter(
                    Offer.id > last_id,
                    Offer.id <= _MAX_ID,
                    Offer.lastProviderId.in_(_LEGACY_API_PROVIDERS_IDS),
                )
                .with_entities(Offer.id)
                .order_by(Offer.id)
                .limit(_BATCH_SIZE)
            ]
        except psycopg2.errors.OperationalError:
            db.session.rollback()
            nb_retry -= 1
            if nb_retry == 0:
                raise


def _set_of_idAtProvider_to_none(offers_ids: list[int]) -> None:
    nb_retry = 3
    while True:
        try:
            db.session.execute(
                sa.text(
                    """
                UPDATE offer
                SET "idAtProvider" = NULL
                WHERE id = ANY (:id_list)
                    """
                ),
                params={"id_list": offers_ids},
            )
        except psycopg2.errors.OperationalError:
            db.session.rollback()
            nb_retry -= 1
            if nb_retry == 0:
                raise


def clean_id_at_provider(start_id: int | None = None) -> None:
    last_id = start_id or (_MIN_ID - 1)
    update_count = 0

    while True:
        with transaction():
            db.session.execute(sa.text("SET SESSION statement_timeout = '300s'"))
            offers_ids = _get_next_offers_ids(last_id)

            if not offers_ids:
                break

            last_id = offers_ids[-1]
            _set_of_idAtProvider_to_none(offers_ids)

            update_count += _BATCH_SIZE
            if update_count % _REPORT_EVERY == 0:
                logger.info(
                    "[Clean idAtProvider job] Status : %s offers updated (now at id %s)",
                    str(update_count),
                    str(last_id),
                )

    logger.info("[Clean idAtProvider job] DONE !")


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(
        description="Remove `idAtProvider` in offers coming from old provider integrations"
    )
    parser.add_argument("--starting-id", type=int, default=1, help="starting offer id")
    args = parser.parse_args()

    clean_id_at_provider(args.starting_id)
