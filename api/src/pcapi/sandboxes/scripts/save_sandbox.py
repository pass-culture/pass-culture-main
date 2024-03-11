import logging

from pcapi.core import search
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offers import models as offer_models
from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes import scripts


logger = logging.getLogger(__name__)


def save_sandbox(name: str, with_clean: bool = True) -> None:
    if with_clean:
        logger.info("Cleaning database")
        clean_all_database(reset_ids=True)
        logger.info("All databases cleaned")

    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)
    sandbox_module.save_sandbox()
    logger.info("Sandbox %s saved", name)
    _index_all_offers()
    _index_all_venues()


# The following functions are rather naive
# The reason it is acceptable is that we only use this on the sandbox, which contains a small amount of data
def _index_all_offers() -> None:
    logger.info("Reindexing offers")
    query = (
        offer_models.Offer.query.with_entities(offer_models.Offer.id)
        .filter(offer_models.Offer.isActive.is_(True))
        .order_by(offer_models.Offer.id)
    )
    search.reindex_offer_ids([offer_id for offer_id, in query])
    logger.info("Reindexing done")


def _index_all_venues() -> None:
    logger.info("Reindexing venues")
    query = (
        offerer_models.Venue.query.with_entities(offerer_models.Venue.id)
        .filter(offerer_models.Venue.isPermanent.is_(True))
        .order_by(offerer_models.Venue.id)
    )
    search.reindex_venue_ids([venue_id for venue_id, in query])
    logger.info("Reindexing done")


def save_sandbox_ci() -> None:
    clean_all_database()
    script_name = "sandbox_industrial"
    sandbox_module = getattr(scripts, script_name)
    sandbox_module.save_ci_sandbox()
    logger.info("Sandbox ci saved")
