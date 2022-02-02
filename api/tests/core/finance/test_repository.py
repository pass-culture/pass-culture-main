import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import repository
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models.bank_information import BankInformationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class GetBusinessUnitsTest:
    def test_basics(self):
        admin = users_factories.AdminFactory()
        venue = offerers_factories.VenueFactory()
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        other_venue = offerers_factories.VenueFactory()
        business_unit2 = other_venue.businessUnit

        business_units = repository.get_business_units_query(admin)
        business_units = list(business_units.order_by(models.BusinessUnit.id))
        assert business_units == [business_unit1, business_unit2]

    def test_pro(self):
        venue = offerers_factories.VenueFactory()
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        pro = users_factories.ProFactory(offerers=[venue.managingOfferer])
        _other_venue_with_business_unit = offerers_factories.VenueFactory()
        business_units = list(repository.get_business_units_query(pro))
        assert business_units == [business_unit1]

    def test_admin_and_filter_on_offerer_id(self):
        admin = users_factories.AdminFactory()
        venue1 = offerers_factories.VenueFactory()
        business_unit1 = venue1.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer_id = venue1.managingOffererId
        _other_venue_with_business_unit = offerers_factories.VenueFactory()

        business_units = repository.get_business_units_query(admin, offerer_id=offerer_id)
        business_units = list(business_units.order_by(models.BusinessUnit.id))
        assert business_units == [business_unit1]

    def test_pro_and_filter_on_offerer_id(self):
        venue = offerers_factories.VenueFactory()
        offerer_id = venue.managingOffererId
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        other_venue = offerers_factories.VenueFactory()
        pro = users_factories.ProFactory(offerers=[venue.managingOfferer, other_venue.managingOfferer])

        business_units = list(repository.get_business_units_query(pro, offerer_id=offerer_id))
        assert business_units == [business_unit1]

    def test_check_offerer_id_and_pro_user(self):
        # Make sure that a pro user cannot specify an offerer id for
        # which they don't have access.
        venue = offerers_factories.VenueFactory()
        offerer_id = venue.managingOffererId
        pro = users_factories.ProFactory(offerers=[])

        business_units = list(repository.get_business_units_query(pro, offerer_id=offerer_id))
        assert business_units == []

    def test_return_accepted_bank_information_only(self):
        admin = users_factories.AdminFactory()
        venue = offerers_factories.VenueFactory()
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        _other_venue = offerers_factories.VenueFactory(
            businessUnit__bankAccount__status=BankInformationStatus.REJECTED,
        )

        business_units = repository.get_business_units_query(admin)
        business_units = list(business_units.order_by(models.BusinessUnit.id))
        assert business_units == [business_unit1]


class GetInvoicesQueryTest:
    def test_basics(self):
        business_unit1 = factories.BusinessUnitFactory()
        invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        business_unit2 = factories.BusinessUnitFactory()
        invoice2 = factories.InvoiceFactory(businessUnit=business_unit2)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer = venue1.managingOfferer
        pro = users_factories.ProFactory(offerers=[offerer])
        _venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            businessUnit=business_unit2,
        )
        other_business_unit = factories.BusinessUnitFactory()
        _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
        _other_invoice = factories.InvoiceFactory(businessUnit=other_business_unit)

        invoices = repository.get_invoices_query(pro).order_by(models.Invoice.id)
        assert list(invoices) == [invoice1, invoice2]

    def test_filter_on_date(self):
        business_unit = factories.BusinessUnitFactory()
        venue = offerers_factories.VenueFactory(businessUnit=business_unit)
        pro = users_factories.ProFactory(offerers=[venue.managingOfferer])
        _invoice_before = factories.InvoiceFactory(
            businessUnit=business_unit,
            date=datetime.date(2021, 6, 15),
        )
        invoice_within = factories.InvoiceFactory(
            businessUnit=business_unit,
            date=datetime.date(2021, 7, 1),
        )
        _invoice_after = factories.InvoiceFactory(
            businessUnit=business_unit,
            date=datetime.date(2021, 8, 1),
        )

        invoices = repository.get_invoices_query(
            pro,
            date_from=datetime.date(2021, 7, 1),
            date_until=datetime.date(2021, 8, 1),
        )
        assert list(invoices) == [invoice_within]

    def test_filter_on_business_unit(self):
        business_unit1 = factories.BusinessUnitFactory()
        invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        pro1 = users_factories.ProFactory(offerers=[venue1.managingOfferer])
        business_unit2 = factories.BusinessUnitFactory()
        _invoice2 = factories.InvoiceFactory(businessUnit=business_unit2)

        invoices = repository.get_invoices_query(
            pro1,
            business_unit_id=business_unit1.id,
        )
        assert list(invoices) == [invoice1]

    def test_wrong_business_unit(self):
        # Make sure that specifying a business unit id that belongs to
        # another offerer does not return anything.
        business_unit1 = factories.BusinessUnitFactory()
        _invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        pro1 = users_factories.ProFactory(offerers=[venue1.managingOfferer])

        other_business_unit = factories.BusinessUnitFactory()
        _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
        _other_invoice = factories.InvoiceFactory(businessUnit=other_business_unit)

        invoices = repository.get_invoices_query(
            pro1,
            business_unit_id=other_business_unit.id,
        )
        assert list(invoices) == []

    def test_admin_filter_on_business_unit(self):
        invoice1 = factories.InvoiceFactory()
        _venue1 = offerers_factories.VenueFactory(businessUnit=invoice1.businessUnit)
        invoice2 = factories.InvoiceFactory()
        _venue2 = offerers_factories.VenueFactory(businessUnit=invoice2.businessUnit)
        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(
            admin,
            business_unit_id=invoice1.businessUnitId,
        )
        assert list(invoices) == [invoice1]

    def test_admin_without_filter(self):
        invoice = factories.InvoiceFactory()
        _venue = offerers_factories.VenueFactory(businessUnit=invoice.businessUnit)
        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(admin)
        assert list(invoices) == []


def test_has_reimbursement():
    booking = bookings_factories.UsedIndividualBookingFactory()
    assert not repository.has_reimbursement(booking)

    pricing = factories.PricingFactory(booking=booking, status=models.PricingStatus.VALIDATED)
    assert not repository.has_reimbursement(booking)

    pricing.status = models.PricingStatus.PROCESSED
    db.session.add(pricing)
    db.session.commit()
    assert repository.has_reimbursement(booking)


class HasActiveOrFutureCustomRemibursementRuleTest:
    def test_active_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now - datetime.timedelta(days=1), now + datetime.timedelta(days=1))
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert repository.has_active_or_future_custom_reimbursement_rule(offer)

    def test_future_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now + datetime.timedelta(days=1), None)
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert repository.has_active_or_future_custom_reimbursement_rule(offer)

    def test_past_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now - datetime.timedelta(days=2), now - datetime.timedelta(days=1))
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert not repository.has_active_or_future_custom_reimbursement_rule(offer)
