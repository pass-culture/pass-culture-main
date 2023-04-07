import datetime
import logging

from pcapi.core.finance import factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories


logger = logging.getLogger(__name__)


def create_industrial_offerer_with_custom_reimbursement_rule() -> None:
    logger.info("create_industrial_offerer_with_custom_reimbursement_rule")
    offerer = offerers_factories.OffererFactory(name="Structure avec un tarif dérogatoire")
    finance_factories.CustomReimbursementRuleFactory(
        offerer=offerer,
        subcategories=["FESTIVAL_LIVRE", "FESTIVAL_CINE"],
        timespan=[
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            None,
        ],
    )
    logger.info("Created offerer with custom reimbursement rule")
