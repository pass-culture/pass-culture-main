import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_industrial_non_payment_notices() -> None:
    logger.info("create_industrial_non_payment_notices")
    offerer = offerers_factories.OffererFactory(name="Entité avec avis d'impayé")
    offerers_factories.NonPaymentNoticeFactory()
    offerers_factories.NonPaymentNoticeFactory(offerer=offerer, venue=None)
    offerers_factories.NonPaymentNoticeFactory(
        offerer=offerer, venue=offerers_factories.VenueFactory(managingOfferer=offerer)
    )
    offerers_factories.NonPaymentNoticeFactory(
        offerer=offerer, venue=offerers_factories.VenueFactory(managingOfferer=offerer)
    )
