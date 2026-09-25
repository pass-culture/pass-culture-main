"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-42661-api-offres-synchronisees-avec-tite-live-stocks-epagine-place-des-libraires-com-encore-publiees \
  -f NAMESPACE=update_offers_from_deactivated_sync \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import typing
from functools import partial

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm

import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offers.models as offers_models
from pcapi import settings
from pcapi.core import search
from pcapi.core.search.models import IndexationReason
from pcapi.models import db
from pcapi.utils import transaction_manager
from pcapi.utils.chunks import get_chunks
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


type OfferIds = set[int]
type VenueIds = set[int]


def batch_activate_offers(
    query: sa_orm.Query[offers_models.Offer],
    activate: bool,
    apply: bool = True,
) -> set[int]:
    query = query.filter(offers_models.Offer.validation == offers_models.OfferValidationStatus.APPROVED)

    update_fields = {"publicationDatetime": get_naive_utc_now() if activate else None}

    def log_processed_chunk(offer_ids: OfferIds, venue_ids: VenueIds) -> None:
        if activate is not None:
            logger.info(
                "Offers have been activated" if activate else "Offers have been deactivated",
                technical_message_id="offers.activated" if activate else "offers.deactivated",
                extra={"offer_ids": offer_ids, "venue_ids": venue_ids},
            )

    return batch_update_offers(
        query=query,
        update_fields=update_fields,
        chunk_processed_callback=log_processed_chunk,
        apply=apply,
    )


def batch_update_offers(
    query: sa_orm.Query[offers_models.Offer],
    update_fields: dict,
    send_email_notification: bool = False,
    chunk_processed_callback: typing.Callable[[OfferIds, VenueIds], None] | None = None,
    chunk_size: int = settings.BATCH_UPDATE_OFFERS_CHUNK_SIZE,
    apply: bool = True,
) -> set[int]:
    results = query.with_entities(offers_models.Offer.id, offers_models.Offer.venueId).yield_per(2_500).tuples()

    updated_offer_ids = set()
    found_venue_ids = set()

    logger.info("Batch update of offers: start", extra={"updated_fields": update_fields})

    for chunk in get_chunks(results, chunk_size=chunk_size):
        with atomic():
            if not apply:
                transaction_manager.mark_transaction_as_invalid()

            raw_offer_ids, raw_venue_ids = zip(*chunk)
            query_to_update = db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_(raw_offer_ids))
            try:
                with atomic():
                    query_to_update.update(update_fields, synchronize_session=False)
                    offer_ids = set(raw_offer_ids)
                    venue_ids = set(raw_venue_ids)
            except sa_exc.OperationalError as exc:
                # Batch failed, likely timeout. Let's fallback on a one by one basis.
                logging.info("Batch failed, falling back on a per offer processing.", extra={"exception": str(exc)})
                offer_ids = set()
                venue_ids = set()
                for offer_id, venue_id in zip(raw_offer_ids, raw_venue_ids):
                    for i in range(5):
                        try:
                            with atomic():
                                db.session.query(offers_models.Offer).filter(offers_models.Offer.id == offer_id).update(
                                    update_fields, synchronize_session=False
                                )
                                offer_ids.add(offer_id)
                                venue_ids.add(venue_id)
                                # offer updated, break the retry loop
                                break
                        except Exception as exc:
                            logging.info("Single UPDATE offer %s failed with reason: %s (try #%s)", offer_id, exc, i)

            updated_offer_ids |= offer_ids
            found_venue_ids |= venue_ids

            if chunk_processed_callback:
                chunk_processed_callback(offer_ids, venue_ids)

            on_commit(
                partial(
                    search.async_index_offer_ids,
                    offer_ids,
                    reason=IndexationReason.OFFER_BATCH_UPDATE,
                    log_extra={"changes": set(update_fields.keys())},
                ),
            )

            withdrawal_updated = {"withdrawalDetails", "withdrawalType", "withdrawalDelay"}.intersection(
                update_fields.keys()
            )
            if send_email_notification and withdrawal_updated:
                for offer in query_to_update.all():
                    transactional_mails.send_email_for_each_ongoing_booking(offer)

    log_extra = {
        "updated_fields": update_fields,
        "nb_offers": len(updated_offer_ids),
        "nb_venues": len(found_venue_ids),
    }
    logger.info("Batch update of offers: end", extra=log_extra)

    return updated_offer_ids


def main(provider_id: int, venue_ids: list[int] | None, apply: bool = False) -> None:
    query = db.session.query(offers_models.Offer).filter(
        offers_models.Offer.lastProviderId == provider_id,
        offers_models.Offer.publicationDatetime != None,
    )
    if venue_ids:
        query = query.filter(
            offers_models.Offer.venueId.in_(venue_ids),
        )
    logger.info("Deactivating offers for provider %s and venues %s", provider_id, venue_ids)
    batch_activate_offers(query, activate=False, apply=apply)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--venue-id",
        type=int,
        required=False,
        nargs="*",
    )
    parser.add_argument("--provider-id", type=int, required=True)
    args = parser.parse_args()

    with atomic():
        db.session.execute(sa.text("SET SESSION lock_timeout = :lock_timeout").bindparams(lock_timeout="5s"))
        db.session.execute(
            sa.text("SET SESSION statement_timeout = :statement_timeout").bindparams(statement_timeout="120s")
        )
        main(provider_id=args.provider_id, venue_ids=args.venue_id, apply=args.apply)
        db.session.execute(
            sa.text("SET SESSION lock_timeout = ':lock_timeout'").bindparams(
                lock_timeout=settings.DATABASE_LOCK_TIMEOUT
            )
        )
        db.session.execute(
            sa.text("SET SESSION statement_timeout = ':statement_timeout'").bindparams(
                statement_timeout=settings.DATABASE_STATEMENT_TIMEOUT
            )
        )

        if not args.apply:
            logger.info("Finished dry run")
        else:
            logger.info("Finished")
