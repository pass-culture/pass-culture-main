import logging
import typing

from pcapi.core import search
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offers import models as offers_models
from pcapi.db_utils import clean_all_database
from pcapi.models import db
from pcapi.sandboxes import scripts
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_mediations import clean_industrial_mediations_bucket
from pcapi.sandboxes.scripts.utils import helpers


logger = logging.getLogger(__name__)


def save_sandbox(
    name: str,
    with_clean: bool = True,
    with_clean_bucket: bool = False,
    steps_to_skip: typing.Iterable[str] | None = None,
) -> None:
    if with_clean:
        logger.info("Cleaning database")
        clean_all_database(reset_ids=True)
        logger.info("All databases cleaned")
    if with_clean_bucket:
        clean_industrial_mediations_bucket()

    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)

    with helpers.skip_steps(steps=steps_to_skip):
        sandbox_module.save_sandbox()

    logger.info("Sandbox %s saved", name)
    _index_all_offers()
    _index_all_venues()


# The following functions are rather naive
# The reason it is acceptable is that we only use this on the sandbox, which contains a small amount of data
def _index_all_offers() -> None:
    logger.info("Reindexing offers")

    query = (
        db.session.query(offers_models.Offer)
        .outerjoin(offers_models.Stock)
        .join(offerer_models.Venue)
        .join(offerer_models.Offerer)
        .filter(offers_models.Offer.is_eligible_for_search)
        .with_entities(offers_models.Offer.id)
    )
    search.reindex_offer_ids([offer_id for (offer_id,) in query])

    logger.info("Reindexing done")


def _index_all_venues() -> None:
    logger.info("Reindexing venues")
    query = (
        db.session.query(offerer_models.Venue)
        .with_entities(offerer_models.Venue.id)
        .filter(offerer_models.Venue.isPermanent.is_(True))
        .order_by(offerer_models.Venue.id)
    )
    search.reindex_venue_ids([venue_id for (venue_id,) in query])
    logger.info("Reindexing done")
