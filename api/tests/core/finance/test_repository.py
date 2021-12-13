import datetime

import pytest

from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import repository
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class GetInvoicesTest:
    def test_basics(self):
        business_unit1 = factories.BusinessUnitFactory()
        invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        business_unit2 = factories.BusinessUnitFactory()
        invoice2 = factories.InvoiceFactory(businessUnit=business_unit2)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer = venue1.managingOfferer
        _venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            businessUnit=business_unit2,
        )
        other_business_unit = factories.BusinessUnitFactory()
        _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
        _other_invoice = factories.InvoiceFactory(businessUnit=other_business_unit)

        invoices = repository.get_invoices_query(offerer.id).order_by(models.Invoice.id)
        assert list(invoices) == [invoice1, invoice2]

    def test_filter_on_date(self):
        business_unit = factories.BusinessUnitFactory()
        venue = offerers_factories.VenueFactory(businessUnit=business_unit)
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
        offerer = venue.managingOfferer

        invoices = repository.get_invoices_query(
            offerer.id,
            date_from=datetime.date(2021, 7, 1),
            date_until=datetime.date(2021, 8, 1),
        )
        assert list(invoices) == [invoice_within]

    def test_filter_on_business_unit(self):
        business_unit1 = factories.BusinessUnitFactory()
        invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        business_unit2 = factories.BusinessUnitFactory()
        _invoice2 = factories.InvoiceFactory(businessUnit=business_unit2)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer = venue1.managingOfferer

        invoices = repository.get_invoices_query(
            offerer.id,
            business_unit_id=business_unit1.id,
        )
        assert list(invoices) == [invoice1]

    def test_wrong_business_unit(self):
        # Make sure that specifying a business unit id that belongs to
        # another offerer does not return anything.
        business_unit1 = factories.BusinessUnitFactory()
        _invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer = venue1.managingOfferer

        other_business_unit = factories.BusinessUnitFactory()
        _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
        _other_invoice = factories.InvoiceFactory(businessUnit=other_business_unit)

        invoices = repository.get_invoices_query(
            offerer.id,
            business_unit_id=other_business_unit.id,
        )
        assert list(invoices) == []
