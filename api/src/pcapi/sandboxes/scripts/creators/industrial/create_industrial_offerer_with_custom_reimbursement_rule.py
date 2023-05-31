import datetime
import logging

from pcapi.core.finance import factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories


logger = logging.getLogger(__name__)


def create_industrial_offerer_with_custom_reimbursement_rule() -> None:
    logger.info("create_industrial_offerer_with_custom_reimbursement_rule")
    offerer = offerers_factories.OffererFactory(name="Structure avec des tarifs dérogatoires")
    finance_factories.CustomReimbursementRuleFactory(
        offerer=offerer,
        subcategories=["FESTIVAL_LIVRE", "FESTIVAL_CINE"],
        timespan=[  # start date in the past => not editable
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            None,
        ],
    )
    finance_factories.CustomReimbursementRuleFactory(
        offerer=offerer,
        subcategories=["FESTIVAL_MUSIQUE"],
        timespan=[  # start date in the future, end date not defined => editable
            datetime.datetime.utcnow() + datetime.timedelta(days=100),
            None,
        ],
        amount=None,
        rate=0.925,
    )
    finance_factories.CustomReimbursementRuleFactory(
        offerer=offerer,
        subcategories=["FESTIVAL_SPECTACLE"],
        timespan=[  # start date in the future, end date not defined => editable
            datetime.datetime.utcnow() + datetime.timedelta(days=150),
            None,
        ],
        amount=None,
        rate=0.9125,
    )
    finance_factories.CustomReimbursementRuleFactory(
        offerer=offerer,
        subcategories=["FESTIVAL_ART_VISUEL"],
        timespan=[  # start date in the future but end date defined => not editable
            datetime.datetime.utcnow() + datetime.timedelta(days=200),
            datetime.datetime.utcnow() + datetime.timedelta(days=250),
        ],
        amount=None,
        rate=0.9,
    )
    logger.info("Created offerer with custom reimbursement rule")
