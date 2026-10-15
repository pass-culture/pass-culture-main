import datetime
import logging

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.finance import factories as finance_factories
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def create_industrial_offerer_with_custom_reimbursement_rule() -> None:
    logger.info("create_industrial_offerer_with_custom_reimbursement_rule")
    _create_offerer_with_custom_reimbursement_rules()
    _create_venues_with_custom_reimbursement_rules()
    logger.info("Created offerer with custom reimbursement rule")


def _create_offerer_with_custom_reimbursement_rules() -> None:
    offerer = offerers_factories.OffererFactory.create(name="Entité juridique avec des tarifs dérogatoires")
    offerers_factories.VenueFactory.create(
        name="Entité juridique avec des tarifs dérogatoires", managingOfferer=offerer, pricing_point="self"
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        offerer=offerer,
        subcategories=["FESTIVAL_LIVRE", "FESTIVAL_CINE"],
        timespan=[  # start date in the past => not editable
            date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
            None,
        ],
        rate=0.9375,
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        offerer=offerer,
        subcategories=["FESTIVAL_MUSIQUE"],
        timespan=[  # start date in the future, end date not defined => editable
            date_utils.get_naive_utc_now() + datetime.timedelta(days=100),
            None,
        ],
        rate=0.925,
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        offerer=offerer,
        subcategories=["FESTIVAL_SPECTACLE"],
        timespan=[  # start date in the future, end date not defined => editable
            date_utils.get_naive_utc_now() + datetime.timedelta(days=150),
            None,
        ],
        rate=0.9125,
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        offerer=offerer,
        subcategories=["FESTIVAL_ART_VISUEL"],
        timespan=[  # start date in the future but end date defined => not editable
            date_utils.get_naive_utc_now() + datetime.timedelta(days=200),
            date_utils.get_naive_utc_now() + datetime.timedelta(days=250),
        ],
        rate=0.9,
    )


def _create_venues_with_custom_reimbursement_rules() -> None:
    offerer = offerers_factories.OffererFactory(name="Partenaires avec tarifs dérogatoires")

    venue_1 = offerers_factories.VenueFactory.create(
        managingOfferer=offerer,
        name="Partenaire avec un tarif dérogatoire",
        pricing_point="self",
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        venue=venue_1,
        timespan=[date_utils.get_naive_utc_now() - datetime.timedelta(days=10), None],
        rate=0.97,
    )

    venue_2 = offerers_factories.VenueFactory.create(
        managingOfferer=offerer,
        name="Partenaire avec un tarif dérogatoire ciblé",
        pricing_point="self",
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        venue=venue_2,
        subcategories=["CARTE_CINE_MULTISEANCES"],
        timespan=[datetime.datetime(2026, 1, 1), None],
        rate=0.85,
    )

    venue_3 = offerers_factories.VenueFactory.create(
        managingOfferer=offerer,
        name="Partenaire avec plusieurs tarifs dérogatoires actifs",
        pricing_point="self",
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        venue=venue_3,
        subcategories=["CARTE_CINE_ILLIMITE"],
        timespan=[datetime.datetime(2026, 1, 1), None],
        rate=0.8,
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        venue=venue_3,
        subcategories=["CARTE_CINE_MULTISEANCES"],
        timespan=[datetime.datetime(2026, 1, 1), None],
        rate=0.9,
    )
    finance_factories.CustomReimbursementRuleFactory.create(
        venue=venue_3,
        subcategories=["SEANCE_CINE"],
        timespan=[datetime.datetime(2026, 1, 1), None],
        rate=0.95,
    )
