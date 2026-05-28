"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=stg \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-41603-rattrapage-artistes-encore \
  -f NAMESPACE=clean_artist_again \
  -f SCRIPT_ARGUMENTS="";

Rebuilds ArtistOfferLink rows for every offer created before CUTOFF_DATE:

  1. Deletes all ArtistOfferLink rows for those offers (including offers linked to a product).
  2. Re-creates one ArtistOfferLink per relevant artist_type present in the offer's extraData, with `(artist_id=None, custom_name=<exact extraData value>)`.
     The raw extraData value is copied into custom_name. Offers linked to a product are NOT re-created.
"""

import argparse
import logging
import typing

import sqlalchemy as sa

from pcapi.models import db


logger = logging.getLogger(__name__)

BATCH_SIZE = 50_000
DEFAULT_MIN_ID = 0
DEFAULT_MAX_ID = 50000


_DELETE_SQL = sa.text(
    """
    DELETE FROM artist_offer_link
    WHERE offer_id BETWEEN :low AND :high
    """
)

_INSERT_SQL = sa.text(
    """
    INSERT INTO artist_offer_link (offer_id, artist_type, custom_name)
    SELECT DISTINCT sub.offer_id,
        CASE kv.key WHEN 'stageDirector' THEN 'stage_director' ELSE kv.key END,
        kv.value
    FROM (
        SELECT
            o.id AS offer_id,
            o."jsonData" AS extra_data
        FROM offer o
        WHERE o.id BETWEEN :low AND :high
          AND o."productId" IS NULL
    ) sub
    CROSS JOIN LATERAL jsonb_each_text(
        CASE WHEN jsonb_typeof(sub.extra_data) = 'object' THEN sub.extra_data ELSE '{}'::jsonb END
    ) AS kv
    WHERE kv.key IN ('author', 'performer', 'stageDirector')
      AND kv.value IS NOT NULL
      AND btrim(kv.value) <> ''
    ON CONFLICT DO NOTHING
    """
)

_INSERT_SQL_WITH_RETURN = sa.text(_INSERT_SQL.text + " RETURNING offer_id, artist_type, custom_name")


def _process_range(low: int, high: int, verbose: bool) -> int:
    params = {"low": low, "high": high}
    db.session.execute(_DELETE_SQL, params)
    if verbose:
        rows = db.session.execute(_INSERT_SQL_WITH_RETURN, params).all()
        for offer_id, artist_type, custom_name in rows:
            logger.info("  offre %s : %s = %r", offer_id, artist_type, custom_name)
        return len(rows)
    else:
        result = typing.cast(sa.CursorResult, db.session.execute(_INSERT_SQL, params))
        return result.rowcount or 0


def main(
    commit: bool,
    min_offer_id: int = DEFAULT_MIN_ID,
    max_offer_id: int = DEFAULT_MAX_ID,
    batch_size: int = BATCH_SIZE,
    verbose: bool = False,
) -> None:
    logger.info("Traitement des offres %s..%s (commit=%s)", min_offer_id, max_offer_id, commit)
    low = min_offer_id

    total_created = 0
    while low <= max_offer_id:
        high = min(low + batch_size - 1, max_offer_id)
        created = _process_range(low, high, verbose)
        total_created += created
        logger.info("Batch %s..%s : %s liens créés", low, high, created)

        if commit:
            db.session.commit()
        else:
            db.session.flush()
        low = high + 1

    if commit:
        logger.info("Script terminé avec succès — %s liens créés au total", total_created)
    else:
        db.session.rollback()
        logger.info("Dry run terminé (%s liens auraient été créés), rollback des données", total_created)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument(
        "--min-offer-id",
        type=int,
        default=DEFAULT_MIN_ID,
        help="Resume from this offer id (inclusive).",
    )
    parser.add_argument(
        "--max-offer-id",
        type=int,
        default=DEFAULT_MAX_ID,
        help="Stop at this offer id (inclusive).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help="Offer id range processed per batch.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log every created artist_offer_link (offer id, artist type, custom name).",
    )
    args = parser.parse_args()

    db.session.execute(sa.text("SET SESSION statement_timeout = '1200s'"))  # 20 minutes

    main(
        commit=args.commit,
        min_offer_id=args.min_offer_id,
        max_offer_id=args.max_offer_id,
        batch_size=args.batch_size,
        verbose=args.verbose,
    )
