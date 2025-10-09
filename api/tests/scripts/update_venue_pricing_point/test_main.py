import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.scripts.update_venue_pricing_point import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_update_venue_pricing_point_no_venue():
    venue = offerers_factories.VenueFactory.create(id=36361)
    pricing_point_venue = offerers_factories.VenueFactory.create()
    bank_account = finance_factories.BankAccountFactory.create()
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue,
        bankAccount=bank_account,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue,
        pricingPoint=pricing_point_venue,
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=pricing_point_venue,
        pricingPoint=pricing_point_venue,
    )
    main.main(not_dry=True)
    assert venue.current_bank_account is None
    assert venue.current_pricing_point == venue
