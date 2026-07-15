"""
Script to nullify Venue.collectivePhone values that contain only a whitelisted country code.

Examples of corrected values: +33, 0033, +590, 590.
"""

import argparse
import logging
import re

from pydantic import BaseModel

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.phone_number import WHITELISTED_COUNTRY_PHONE_CODES
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


class CorrectionCounters(BaseModel):
    scanned: int = 0
    corrected: int = 0


def _normalize_phone(raw_phone: str) -> str:
    # Keep only digits and a possible leading + for robust matching across formatting variants.
    compact_phone = re.sub(r"[\s().-]", "", raw_phone.strip())
    if compact_phone.startswith("+"):
        return f"+{re.sub(r'\D', '', compact_phone[1:])}"
    return re.sub(r"\D", "", compact_phone)


def _is_country_code_only(raw_phone: str) -> bool:
    normalized_phone = _normalize_phone(raw_phone)

    for country_code in WHITELISTED_COUNTRY_PHONE_CODES:
        as_text = str(country_code)
        if normalized_phone in (as_text, f"+{as_text}", f"00{as_text}"):
            return True

    return False


@atomic()
def main(apply: bool) -> None:
    counters = CorrectionCounters()

    venues = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.collectivePhone.isnot(None)).all()
    counters.scanned = len(venues)

    for venue in venues:
        collective_phone = venue.collectivePhone
        if collective_phone is None:
            continue

        if not _is_country_code_only(collective_phone):
            continue

        logger.info(
            "Nullifying collectivePhone for venue_id=%s (old_value=%s)",
            venue.id,
            collective_phone,
        )
        venue.collectivePhone = None
        counters.corrected += 1
        db.session.flush()
    logger.info("Processed %s venues", counters.scanned)
    logger.info("Found %s invalid collectivePhone values", counters.corrected)

    if not apply:
        logger.info("Dry-run mode: transaction will be rolled back. Use --apply to persist changes.")
        mark_transaction_as_invalid()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Persist changes in database")
    args = parser.parse_args()

    logger.info("Starting correction for Venue.collectivePhone with args %s", args)
    main(apply=args.apply)
    logger.info("Finished")
