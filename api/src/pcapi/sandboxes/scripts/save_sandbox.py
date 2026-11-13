import logging
import time
import typing

import sqlalchemy as sa

from pcapi import settings
from pcapi.core import search
from pcapi.core.artist import models as artists_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.db_utils import clean_all_database
from pcapi.models import db
from pcapi.models.feature import install_feature_flags
from pcapi.sandboxes import dump
from pcapi.sandboxes import scripts
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_mediations import clean_industrial_mediations_bucket
from pcapi.sandboxes.scripts.utils import helpers


logger = logging.getLogger(__name__)

SAVE_SANDBOX_BY_NAME: typing.Final[dict[str, typing.Callable[[], None]]] = {
    "accessibility_offers": scripts.sandbox_accessibility_offers.save_sandbox,
    "allocine": scripts.sandbox_allocine.save_sandbox,
    "beneficiaries": scripts.sandbox_beneficiaries.save_sandbox,
    "big": scripts.sandbox_big.save_sandbox,
    "industrial": scripts.sandbox_industrial.save_sandbox,
    "tiny": scripts.sandbox_tiny.save_sandbox,
}


def save_sandbox(
    name: tuple[str],
    with_clean: bool = True,
    with_clean_bucket: bool = False,
    with_indexing: bool = True,
    steps_to_skip: typing.Iterable[str] | None = None,
) -> None:
    if any(n for n in name if n not in SAVE_SANDBOX_BY_NAME):
        raise ValueError("Invalid name provided")

    if with_clean:
        logger.info("Cleaning database")
        clean_all_database(reset_ids=True)
        logger.info("All databases cleaned")
    if with_clean_bucket:
        clean_industrial_mediations_bucket()

    logger.info("Starting sandbox %s", name)
    for sandbox_name in name:
        save_sandbox_func = SAVE_SANDBOX_BY_NAME[sandbox_name]

        with helpers.skip_steps(steps=steps_to_skip):
            save_sandbox_func()

    logger.info("Sandbox %s saved", name)
    if with_indexing:
        index_sandbox()
    else:
        logger.info("Indexing finished (skipped)")


def restore_industrial_sandbox(with_clean_bucket: bool, with_indexing: bool) -> None:
    """Restore the industrial sandbox from its tracked dump."""
    started_at = time.monotonic()
    try:
        dump.check_restorable(settings.SANDBOX_POSTGRES_CONTAINER)
        # Empty the tables whose data is dumped: all the tables of the `public` schema except `dump.EXCLUDED_TABLES`
        db.session.execute(
            sa.text("""
                DO $$
                BEGIN
                    EXECUTE (
                        SELECT 'TRUNCATE TABLE ' || string_agg(format('%I.%I', schemaname, tablename), ', ')
                        FROM pg_tables
                        WHERE schemaname = 'public' AND tablename NOT IN ('alembic_version', 'spatial_ref_sys')
                    );
                END
                $$
            """)
        )
        db.session.commit()
        dump.restore_dump(settings.SANDBOX_POSTGRES_CONTAINER, db.engine.url.render_as_string())
    except Exception:
        db.session.rollback()
        raise
    logger.info("Sandbox dump restored in %.1fs", time.monotonic() - started_at)

    install_feature_flags()
    perm_models.sync_db_permissions(db.session)
    perm_models.sync_db_roles(db.session)
    if with_clean_bucket:
        clean_industrial_mediations_bucket()
    if with_indexing:
        index_sandbox()
    logger.info(f"Sandbox industrial restored from its dump in {time.monotonic() - started_at:.1f}s")


def index_sandbox() -> None:
    _index_all_offers()
    _index_all_collective_offer_templates()
    _index_all_venues()
    _index_all_artists()
    logger.info("Indexing finished")


# The following functions are rather naive
# The reason it is acceptable is that we only use this on the sandbox, which contains a small amount of data
def _index_all_offers() -> None:
    logger.info("Reindexing offers")

    search.unindex_all_offers()
    query = (
        db.session.query(offers_models.Offer)
        .outerjoin(offers_models.Stock)
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .filter(offers_models.Offer.is_eligible_for_search)
        .with_entities(offers_models.Offer.id)
    )
    search.reindex_offer_ids([offer_id for (offer_id,) in query])

    logger.info("Reindexing offers done")


def _index_all_collective_offer_templates() -> None:
    logger.info("Reindexing collective offer templates")

    search.unindex_all_collective_offer_templates()
    search.index_all_collective_offers_and_templates()

    logger.info("Reindexing collective offer templates done")


def _index_all_artists() -> None:
    logger.info("Reindexing artists")

    search.unindex_all_artists()
    query = db.session.query(artists_models.Artist).with_entities(artists_models.Artist.id)
    search.reindex_artist_ids([artist_id for (artist_id,) in query])

    logger.info("Reindexing artists done")


def _index_all_venues() -> None:
    logger.info("Reindexing venues")

    search.unindex_all_venues()
    query = (
        db.session.query(offerers_models.Venue)
        .with_entities(offerers_models.Venue.id)
        .order_by(offerers_models.Venue.id)
    )
    search.reindex_venue_ids([venue_id for (venue_id,) in query])

    logger.info("Reindexing venues done")
