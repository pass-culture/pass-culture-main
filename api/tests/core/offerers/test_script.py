import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.scripts.add_pricing_point_and_bank_account_to_regulated_venues import main as scripts


pytestmark = pytest.mark.usefixtures("db_session")


class AddPricingPointTest:
    def test_add_pricing_point_links_to_siret_venue(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900001")
        pricing_point_link = offerers_factories.VenuePricingPointLinkFactory(
            venue=venue_with_siret, pricingPoint=venue_with_siret
        )
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_with_siret)

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )
        mocked_csv = scripts.mock_csv([venue_to_link])
        scripts._add_pricing_point(mocked_csv, not_dry=True)
        VenuePricingPointLink = offerers_factories.VenuePricingPointLinkFactory._meta.model
        new_link = db.session.query(VenuePricingPointLink).filter_by(venueId=venue_to_link.id).one()

        assert new_link.pricingPointId == pricing_point_link.pricingPointId
        assert new_link.venueId == venue_to_link.id

    def test_should_not_add_pricing_point_if_offerer_has_no_siret(self):
        venue_without_siret = offerers_factories.VenueFactory(siret=None, comment="Missing SIRET")
        offerers_factories.VenuePricingPointLinkFactory(venue=venue_without_siret, pricingPoint=venue_without_siret)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_without_siret)

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_without_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_pricing_point(mocked_csv, not_dry=True)

        VenuePricingPointLink = offerers_factories.VenuePricingPointLinkFactory._meta.model
        new_link = db.session.query(VenuePricingPointLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link == None

    def test_should_not_add_pricing_point_if_offerer_has_multiple_siret_venues(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        offerers_factories.VenueFactory(managingOfferer=venue_with_siret.managingOfferer, siret="12345678900020")
        offerers_factories.VenuePricingPointLinkFactory(venue=venue_with_siret, pricingPoint=venue_with_siret)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_with_siret)
        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )
        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_pricing_point(mocked_csv, not_dry=True)

        VenuePricingPointLink = offerers_factories.VenuePricingPointLinkFactory._meta.model
        new_link = db.session.query(VenuePricingPointLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link is None


class AddBankAccountTest:
    def test_add_bank_account_links_to_siret_venue(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        bank_account = finance_factories.BankAccountFactory(offerer=venue_with_siret.managingOfferer)

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_bank_account(mocked_csv, not_dry=True)

        VenueBankAccountLink = offerers_factories.VenueBankAccountLinkFactory._meta.model

        new_link = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link.bankAccountId == bank_account.id
        assert new_link.venueId == venue_to_link.id

    def test_add_bank_account_even_if_no_siret(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        venue_without_siret = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Has a bank account but no siret"
        )
        bank_account = finance_factories.BankAccountFactory(offerer=venue_without_siret.managingOfferer)

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_bank_account(mocked_csv, not_dry=True)

        VenueBankAccountLink = offerers_factories.VenueBankAccountLinkFactory._meta.model

        new_link = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link.bankAccountId == bank_account.id
        assert new_link.venueId == venue_to_link.id

    def test_should_not_add_bank_account_if_offerer_has_more_than_one(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        finance_factories.BankAccountFactory(offerer=venue_with_siret.managingOfferer)
        finance_factories.BankAccountFactory(offerer=venue_with_siret.managingOfferer)

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_bank_account(mocked_csv, not_dry=True)

        VenueBankAccountLink = offerers_factories.VenueBankAccountLinkFactory._meta.model

        new_link = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link is None

    def test_should_not_add_bank_account_if_inactive(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        finance_factories.BankAccountFactory(offerer=venue_with_siret.managingOfferer, isActive=False)

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_bank_account(mocked_csv, not_dry=True)

        VenueBankAccountLink = offerers_factories.VenueBankAccountLinkFactory._meta.model

        new_link = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link is None

    def test_should_not_add_bank_account_if_not_accepted(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        finance_factories.BankAccountFactory(
            offerer=venue_with_siret.managingOfferer, status=BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS
        )

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_bank_account(mocked_csv, not_dry=True)

        VenueBankAccountLink = offerers_factories.VenueBankAccountLinkFactory._meta.model

        new_link = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link is None

    def test_should_add_bank_account_if_only_one_valid(self):
        venue_with_siret = offerers_factories.VenueFactory(siret="12345678900010")
        valid_bank_account = finance_factories.BankAccountFactory(offerer=venue_with_siret.managingOfferer)
        finance_factories.BankAccountFactory(offerer=venue_with_siret.managingOfferer, isActive=False)
        finance_factories.BankAccountFactory(
            offerer=venue_with_siret.managingOfferer,
            status=BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS,
        )

        venue_to_link = offerers_factories.VenueFactory(
            managingOfferer=venue_with_siret.managingOfferer, siret=None, comment="Venue address that has no siret"
        )

        mocked_csv = scripts.mock_csv([venue_to_link])

        scripts._add_bank_account(mocked_csv, not_dry=True)

        VenueBankAccountLink = offerers_factories.VenueBankAccountLinkFactory._meta.model

        new_link = db.session.query(VenueBankAccountLink).filter_by(venueId=venue_to_link.id).one_or_none()
        assert new_link.bankAccountId == valid_bank_account.id
        assert new_link.venueId == venue_to_link.id
