import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_invoices(client):
    business_unit1 = finance_factories.BusinessUnitFactory()
    dt1 = datetime.datetime(2021, 1, 1)
    invoice1 = finance_factories.InvoiceFactory(businessUnit=business_unit1, date=dt1)
    business_unit2 = finance_factories.BusinessUnitFactory()
    dt2 = dt1 + datetime.timedelta(days=15)
    invoice2 = finance_factories.InvoiceFactory(businessUnit=business_unit2, date=dt2, amount=-1234)
    finance_factories.CashflowFactory(
        invoices=[invoice1, invoice2],
        businessUnit=business_unit1,
        amount=-1234,
        batch=finance_factories.CashflowBatchFactory(label="VIR1"),
    )
    venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
    offerer = venue1.managingOfferer
    _venue2 = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        businessUnit=business_unit2,
    )
    other_business_unit = finance_factories.BusinessUnitFactory()
    _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
    _other_invoice = finance_factories.InvoiceFactory(businessUnit=other_business_unit)
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    response = client.get("/finance/invoices")

    assert response.status_code == 200
    invoices = response.json
    assert len(invoices) == 2
    assert invoices[0] == {
        "reference": invoice2.reference,
        "date": invoice2.date.date().isoformat(),
        "cashflowLabels": ["VIR1"],
        "amount": 12.34,
        "url": invoice2.url,
        "businessUnitName": business_unit2.name,
    }
    assert invoices[1]["reference"] == invoice1.reference


def test_get_invoices_only_return_visible_invoices(client):
    batch1 = finance_factories.CashflowBatchFactory(label="firstBatch")
    batch2 = finance_factories.CashflowBatchFactory(label="secondBatch")
    business_unit1 = finance_factories.BusinessUnitFactory()
    dt1 = datetime.datetime(2021, 1, 1)
    invoice1 = finance_factories.InvoiceFactory(businessUnit=business_unit1, amount=-4321, date=dt1)
    business_unit2 = finance_factories.BusinessUnitFactory()
    dt2 = dt1 + datetime.timedelta(days=15)
    invoice2 = finance_factories.InvoiceFactory(businessUnit=business_unit2, amount=-1234, date=dt2)
    finance_factories.CashflowFactory(invoices=[invoice1], businessUnit=business_unit1, amount=-1234, batch=batch1)
    finance_factories.CashflowFactory(invoices=[invoice1], businessUnit=business_unit1, amount=-4321, batch=batch2)
    finance_factories.CashflowFactory(invoices=[invoice2], businessUnit=business_unit1, amount=-4321, batch=batch2)
    venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
    offerer = venue1.managingOfferer
    _venue2 = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        businessUnit=business_unit2,
    )

    # The user_offerer link is not validated, he should not be able to see their invoices.
    business_unit3 = finance_factories.BusinessUnitFactory()
    finance_factories.InvoiceFactory(businessUnit=business_unit3, amount=-15000000)
    venue3 = offerers_factories.VenueFactory(businessUnit=business_unit3)
    offerer2 = venue3.managingOfferer

    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer2, validationToken="token")

    client = client.with_session_auth(pro.email)
    response = client.get("/finance/invoices")

    assert response.status_code == 200
    invoices = response.json
    assert len(invoices) == 2
    assert invoices[0] == {
        "reference": invoice2.reference,
        "date": invoice2.date.date().isoformat(),
        "cashflowLabels": ["secondBatch"],
        "amount": 12.34,
        "url": invoice2.url,
        "businessUnitName": business_unit2.name,
    }
    assert invoices[1] == {
        "reference": invoice1.reference,
        "date": invoice1.date.date().isoformat(),
        "amount": 43.21,
        "cashflowLabels": ["firstBatch", "secondBatch"],
        "url": invoice1.url,
        "businessUnitName": business_unit1.name,
    }


def test_get_invoices_specify_business_unit(client):
    business_unit1 = finance_factories.BusinessUnitFactory()
    invoice1 = finance_factories.InvoiceFactory(businessUnit=business_unit1)
    business_unit2 = finance_factories.BusinessUnitFactory()
    _invoice2 = finance_factories.InvoiceFactory(businessUnit=business_unit2)
    venue = offerers_factories.VenueFactory(businessUnit=business_unit1)
    offerer = venue.managingOfferer
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    params = {"businessUnitId": business_unit1.id}
    response = client.get("/finance/invoices", params=params)

    assert response.status_code == 200
    invoices = response.json
    assert len(invoices) == 1
    assert invoices[0]["reference"] == invoice1.reference


def test_get_invoices_specify_dates(client):
    business_unit = finance_factories.BusinessUnitFactory()
    _invoice_before = finance_factories.InvoiceFactory(
        businessUnit=business_unit,
        date=datetime.datetime(2021, 6, 1),
    )
    invoice_within = finance_factories.InvoiceFactory(
        businessUnit=business_unit,
        date=datetime.datetime(2021, 7, 1),
    )
    _invoice_after = finance_factories.InvoiceFactory(
        businessUnit=business_unit,
        date=datetime.datetime(2021, 8, 1),
    )
    venue = offerers_factories.VenueFactory(businessUnit=business_unit)
    offerer = venue.managingOfferer
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    params = {"periodBeginningDate": "2021-07-01", "periodEndingDate": "2021-07-31"}
    response = client.get("/finance/invoices", params=params)

    assert response.status_code == 200
    invoices = response.json
    assert len(invoices) == 1
    assert invoices[0]["reference"] == invoice_within.reference


def test_get_invoices_unauthorized_business_unit(client):
    offerer = offerers_factories.OffererFactory()
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
    other_invoice = finance_factories.InvoiceFactory()
    other_business_unit = other_invoice.businessUnit

    client = client.with_session_auth(pro.email)
    params = {"businessUnitId": other_business_unit.id}
    response = client.get("/finance/invoices", params=params)

    assert response.status_code == 200
    invoices = response.json
    assert invoices == []
