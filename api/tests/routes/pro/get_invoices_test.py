import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories


class GetInvoicesTest:
    def test_get_invoices(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        pro_reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        finance_factories.BankInformationFactory(venue=pro_reimbursement_point1)
        dt1 = datetime.datetime(2021, 1, 1)
        invoice1 = finance_factories.InvoiceFactory(reimbursementPoint=pro_reimbursement_point1, date=dt1, amount=-1000)
        dt2 = dt1 + datetime.timedelta(days=15)
        invoice2 = finance_factories.InvoiceFactory(reimbursementPoint=pro_reimbursement_point1, date=dt2, amount=-1500)
        finance_factories.CashflowFactory(
            invoices=[invoice1, invoice2],
            reimbursementPoint=pro_reimbursement_point1,
            bankAccount=pro_reimbursement_point1.bankInformation,
            amount=-2500,
            batch=finance_factories.CashflowBatchFactory(label="VIR1"),
        )
        _other_reimbursement_point = offerers_factories.VenueFactory(reimbursement_point="self")
        _other_invoice = finance_factories.InvoiceFactory(reimbursementPoint=_other_reimbursement_point)

        client = client.with_session_auth(pro.email)
        response = client.get("/finance/invoices")

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 2
        assert invoices[0] == {
            "reference": invoice2.reference,
            "date": invoice2.date.date().isoformat(),
            "cashflowLabels": ["VIR1"],
            "amount": 15.00,
            "url": invoice2.url,
            "reimbursementPointName": pro_reimbursement_point1.name,
        }
        assert invoices[1]["reference"] == invoice1.reference

    def test_get_invoices_only_return_visible_invoices(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        pro_reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        finance_factories.BankInformationFactory(venue=pro_reimbursement_point1)
        dt1 = datetime.datetime(2021, 1, 1)
        invoice1 = finance_factories.InvoiceFactory(reimbursementPoint=pro_reimbursement_point1, date=dt1, amount=-1000)
        dt2 = dt1 + datetime.timedelta(days=15)
        invoice2 = finance_factories.InvoiceFactory(reimbursementPoint=pro_reimbursement_point1, date=dt2, amount=-1500)
        finance_factories.CashflowFactory(
            invoices=[invoice1, invoice2],
            reimbursementPoint=pro_reimbursement_point1,
            bankAccount=pro_reimbursement_point1.bankInformation,
            amount=-2500,
            batch=finance_factories.CashflowBatchFactory(label="VIR1"),
        )
        offerer2 = offerers_factories.OffererFactory()
        reimbursement_point3 = offerers_factories.VenueFactory(reimbursement_point="self")
        _other_invoice = finance_factories.InvoiceFactory(reimbursementPoint=reimbursement_point3, amount=-15000000)
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerers_factories.NotValidatedUserOffererFactory(user=pro, offerer=offerer2)

        client = client.with_session_auth(pro.email)
        response = client.get("/finance/invoices")

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 2
        assert invoices[0] == {
            "reference": invoice2.reference,
            "date": invoice2.date.date().isoformat(),
            "amount": 15.0,
            "cashflowLabels": ["VIR1"],
            "url": invoice2.url,
            "reimbursementPointName": pro_reimbursement_point1.name,
        }
        assert invoices[1] == {
            "reference": invoice1.reference,
            "date": invoice1.date.date().isoformat(),
            "amount": 10.0,
            "cashflowLabels": ["VIR1"],
            "url": invoice1.url,
            "reimbursementPointName": pro_reimbursement_point1.name,
        }

    def test_get_invoices_specify_reimbursement_point(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        pro_reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        invoice1 = finance_factories.InvoiceFactory(reimbursementPoint=pro_reimbursement_point1, amount=-1000)
        pro_reimbursement_point2 = offerers_factories.VenueFactory(reimbursement_point="self")
        _invoice2 = finance_factories.InvoiceFactory(reimbursementPoint=pro_reimbursement_point2, amount=-1500)

        client = client.with_session_auth(pro.email)
        params = {"reimbursementPointId": pro_reimbursement_point1.id}
        response = client.get("/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice1.reference

    def test_get_invoices_specify_dates(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        pro_reimbursement_point = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        _invoice_before = finance_factories.InvoiceFactory(
            reimbursementPoint=pro_reimbursement_point,
            date=datetime.datetime(2021, 6, 1),
        )
        invoice_within = finance_factories.InvoiceFactory(
            reimbursementPoint=pro_reimbursement_point,
            date=datetime.datetime(2021, 7, 1),
        )
        _invoice_after = finance_factories.InvoiceFactory(
            reimbursementPoint=pro_reimbursement_point,
            date=datetime.datetime(2021, 8, 1),
        )

        client = client.with_session_auth(pro.email)
        params = {"periodBeginningDate": "2021-07-01", "periodEndingDate": "2021-07-31"}
        response = client.get("/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert len(invoices) == 1
        assert invoices[0]["reference"] == invoice_within.reference

    def test_get_invoices_unauthorized_reimbursement_point(self, client):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        other_reimbursement_point = offerers_factories.VenueFactory(reimbursement_point="self")
        _other_reimbursement_point_invoice = finance_factories.InvoiceFactory(
            reimbursementPoint=other_reimbursement_point, amount=-1000
        )

        client = client.with_session_auth(pro.email)
        params = {"reimbursementPointId": other_reimbursement_point.id}
        response = client.get("/finance/invoices", params=params)

        assert response.status_code == 200
        invoices = response.json
        assert invoices == []
