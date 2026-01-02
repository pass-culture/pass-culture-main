import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.scripts.end_vbal_vppl_venue_soft_deleted.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_end_vbal_and_vppl_on_soft_deleted_venues():
    venue_address = offerers_factories.VenueFactory(siret=None, comment="address venue")  # venue address without siret
    venue_address_id = venue_address.id
    venue_with_siret = offerers_factories.VenueFactory(managingOfferer=venue_address.managingOfferer)
    bank_account = finance_factories.BankAccountFactory()
    derecated_venue_bank_account_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_address, bankAccount=bank_account
    )
    derecated_venue_pricing_point_link = offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_address, pricingPoint=venue_with_siret
    )
    venue_bank_account_link = offerers_factories.VenueBankAccountLinkFactory(
        venue=venue_with_siret, bankAccount=bank_account
    )
    venue_pricing_point_link = offerers_factories.VenuePricingPointLinkFactory(
        venue=venue_with_siret, pricingPoint=venue_with_siret
    )

    author = users_factories.UserFactory()

    assert venue_address.current_bank_account_link == derecated_venue_bank_account_link
    assert venue_address.current_pricing_point_link == derecated_venue_pricing_point_link
    assert venue_with_siret.current_bank_account_link == venue_bank_account_link
    assert venue_with_siret.current_pricing_point_link == venue_pricing_point_link

    # regularization action:
    venue_address.isSoftDeleted = True
    db.session.flush()

    main(author=author, not_dry=True)

    soft_deleted_venue_address = (
        db.session.query(offerers_models.Venue).filter_by(id=venue_address_id).execution_options(include_deleted=True)
    ).one()

    venue_address_depecated_count = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.venueId == soft_deleted_venue_address.id,
            history_models.ActionHistory.bankAccountId == bank_account.id,
            history_models.ActionHistory.authorUser == author,
            history_models.ActionHistory.actionType == history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
        )
        .count()
    )
    assert venue_address_depecated_count == 1

    assert soft_deleted_venue_address.current_bank_account_link == None
    assert soft_deleted_venue_address.current_pricing_point_link == None
    assert derecated_venue_bank_account_link.timespan.upper is not None
    assert derecated_venue_pricing_point_link.timespan.upper is not None
    assert venue_with_siret.current_bank_account_link == venue_bank_account_link
    assert venue_with_siret.current_pricing_point_link == venue_pricing_point_link
