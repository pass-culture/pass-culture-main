import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.scripts.update_offerer_venues_pp_and_ba import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_update_offer_venues_pp_and_ba():
    offerer = offerers_factories.OffererFactory.create(id=7790)
    venue_with_pp_without_ba = offerers_factories.VenueFactory.create(
        managingOfferer=offerer, siret=None, comment="comment"
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_with_pp_without_ba,
        pricingPoint=venue_with_pp_without_ba,
    )

    venue_with_ba = offerers_factories.VenueFactory.create(managingOfferer=offerer, siret=None, comment="comment")
    ba = finance_factories.BankAccountFactory.create()
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=venue_with_ba,
        bankAccount=ba,
    )

    pricing_point_venue = offerers_factories.VenueFactory.create(id=18698, managingOfferer=offerer)
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=pricing_point_venue,
        pricingPoint=pricing_point_venue,
    )

    pp_ba = finance_factories.BankAccountFactory.create()
    offerers_factories.VenueBankAccountLinkFactory.create(
        venue=pricing_point_venue,
        bankAccount=pp_ba,
    )

    main.main(not_dry=True)
    assert venue_with_pp_without_ba.current_bank_account == pp_ba
    assert venue_with_pp_without_ba.current_pricing_point == pricing_point_venue
    assert venue_with_ba.current_bank_account == ba
    assert venue_with_ba.current_pricing_point == pricing_point_venue
