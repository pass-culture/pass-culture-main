import csv
import datetime
from io import StringIO

import pytest

from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.utils.date import utc_datetime_to_department_timezone


pytestmark = pytest.mark.usefixtures("db_session")


def test_without_invoices_references(client):
    user_offerer = offerers_factories.UserOffererFactory()
    pro = user_offerer.user

    # When
    response = client.with_session_auth(pro.email).get("/v2/reimbursements/csv")

    # Then
    assert response.status_code == 400
    assert response.json["invoicesReferences"] == ["Ce champ est obligatoire"]


def test_with_pricings(client):
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    bank_account_1 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )

    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point=venue1)
    bank_account_2 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_2, timespan=(datetime.datetime.utcnow(),)
    )

    batch = finance_factories.CashflowBatchFactory()

    invoices_references_str = ""

    for bank_account, venue in zip((bank_account_1, bank_account_2), (venue1, venue2)):
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account)
        if invoices_references_str:
            invoices_references_str += "&"
        invoices_references_str += f"invoicesReferences={invoice.reference}"
        cashflow = finance_factories.CashflowFactory(batch=batch, bankAccount=bank_account, invoices=[invoice])
        finance_factories.PricingFactory(
            booking__stock__offer__venue=venue, status=finance_models.PricingStatus.INVOICED, cashflows=[cashflow]
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # When
    client = client.with_session_auth(pro.email)
    queries = AUTHENTICATION_QUERIES
    queries += 1  # get offerers from invoices references
    queries += 1  # check user has acces to offerers
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    queries += 1  # feature flag
    with assert_num_queries(queries):
        response = client.get(f"/v2/reimbursements/csv?{invoices_references_str}")
        assert response.status_code == 200

    # Then
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.CSV_HEADER
    rows = list(reader)
    assert len(rows) == 2
    row = rows[1]

    invoice = finance_models.Invoice.query.filter(finance_models.Invoice.bankAccountId == bank_account_1.id).one()
    batch = finance_models.CashflowBatch.query.one()
    offer = offers_models.Offer.query.filter(offers_models.Offer.venueId == venue1.id).one()
    booking = bookings_models.Booking.query.filter(bookings_models.Booking.venueId == venue1.id).one()
    pricing = finance_models.Pricing.query.filter(finance_models.Pricing.bookingId == booking.id).one()

    assert row["Date du justificatif"] == invoice.date.strftime("%Y-%m-%d")
    assert row["N° du justificatif"] == invoice.reference
    assert row["N° de virement"] == batch.label
    assert row["Intitulé du compte bancaire"] == bank_account_1.label
    assert row["SIRET du lieu"] == venue1.siret
    assert row["IBAN"] == bank_account_1.iban
    assert row["Raison sociale du lieu"] == venue1.name
    assert row["Adresse du lieu"] == f"{venue1.street} {venue1.postalCode} {venue1.city}"
    assert row["SIRET du lieu"] == venue1.siret
    assert row["Nom de l'offre"] == offer.name
    assert row["N° de réservation (offre collective)"] == ""
    assert row["Nom (offre collective)"] == ""
    assert row["Prénom (offre collective)"] == ""
    assert row["Nom de l'établissement (offre collective)"] == ""
    assert row["Date de l'évènement (offre collective)"] == ""
    assert row["Contremarque"] == booking.token
    assert row["Date de validation de la réservation"] == booking.dateUsed.strftime("%Y-%m-%d %H:%M:%S")
    assert row["Intitulé du tarif"] == ""
    assert row["Montant de la réservation"] == str(booking.amount).replace(".", ",")
    assert row["Barème"].replace("\xa0", " ") == "100 %"
    assert row["Montant remboursé"] == "{:.2f}".format(-pricing.amount / 100).replace(".", ",")


def test_with_pricings_collective_use_case(client):
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    bank_account_1 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )

    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point=venue1)
    bank_account_2 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_2, timespan=(datetime.datetime.utcnow(),)
    )

    batch = finance_factories.CashflowBatchFactory()

    invoices_references_str = ""

    for bank_account, venue in zip((bank_account_1, bank_account_2), (venue1, venue2)):
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account)
        if invoices_references_str:
            invoices_references_str += "&"
        invoices_references_str += f"invoicesReferences={invoice.reference}"
        cashflow = finance_factories.CashflowFactory(batch=batch, bankAccount=bank_account, invoices=[invoice])
        finance_factories.CollectivePricingFactory(
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # When
    client = client.with_session_auth(pro.email)
    queries = AUTHENTICATION_QUERIES
    queries += 1  # get offerers from invoices references
    queries += 1  # check user has access to offerers
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    queries += 1  # feature flag
    with assert_num_queries(queries):
        response = client.get(f"/v2/reimbursements/csv?{invoices_references_str}")
        assert response.status_code == 200

    # Then
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.CSV_HEADER
    rows = list(reader)
    assert len(rows) == 2
    row = rows[1]

    invoice = finance_models.Invoice.query.filter(finance_models.Invoice.bankAccountId == bank_account_1.id).one()
    batch = finance_models.CashflowBatch.query.one()
    collective_offer = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.venueId == venue1.id
    ).one()
    collective_booking = educational_models.CollectiveBooking.query.filter(
        educational_models.CollectiveBooking.venueId == venue1.id
    ).one()
    pricing = finance_models.Pricing.query.filter(
        finance_models.Pricing.collectiveBookingId == collective_booking.id
    ).one()
    redactor = collective_booking.educationalRedactor
    institution = collective_booking.educationalInstitution

    assert row["Date du justificatif"] == invoice.date.strftime("%Y-%m-%d")
    assert row["N° du justificatif"] == invoice.reference
    assert row["N° de virement"] == batch.label
    assert row["Intitulé du compte bancaire"] == bank_account_1.label
    assert row["SIRET du lieu"] == venue1.siret
    assert row["IBAN"] == bank_account_1.iban
    assert row["Raison sociale du lieu"] == venue1.name
    assert row["Adresse du lieu"] == f"{venue1.street} {venue1.postalCode} {venue1.city}"
    assert row["SIRET du lieu"] == venue1.siret
    assert row["Nom de l'offre"] == collective_offer.name
    assert row["N° de réservation (offre collective)"] == str(collective_booking.id)
    assert row["Nom (offre collective)"] == redactor.lastName
    assert row["Prénom (offre collective)"] == redactor.firstName
    assert row["Nom de l'établissement (offre collective)"] == institution.name
    assert row["Date de l'évènement (offre collective)"] == utc_datetime_to_department_timezone(
        collective_booking.collectiveStock.beginningDatetime, venue1.departementCode
    ).strftime("%d/%m/%Y %H:%M")
    assert row["Contremarque"] == ""
    assert row["Date de validation de la réservation"] == collective_booking.dateUsed.strftime("%Y-%m-%d %H:%M:%S")
    assert row["Intitulé du tarif"] == ""
    assert row["Montant de la réservation"] == str(collective_booking.collectiveStock.price).replace(".", ",")
    assert row["Barème"].replace("\xa0", " ") == "100 %"
    assert row["Montant remboursé"] == "{:.2f}".format(-pricing.amount / 100).replace(".", ",")


def test_return_only_searched_invoice(client):
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    bank_account_1 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )

    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point=venue1)
    bank_account_2 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_2, timespan=(datetime.datetime.utcnow(),)
    )

    batch = finance_factories.CashflowBatchFactory()

    for bank_account, venue in zip((bank_account_1, bank_account_2), (venue1, venue2)):
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account)
        finance_factories.InvoiceFactory(bankAccount=bank_account)
        invoice_reference = invoice.reference
        cashflow = finance_factories.CashflowFactory(batch=batch, bankAccount=bank_account, invoices=[invoice])
        finance_factories.CollectivePricingFactory(
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # When
    client = client.with_session_auth(pro.email)
    queries = AUTHENTICATION_QUERIES
    queries += 1  # get offerers from invoices references
    queries += 1  # check user has access to offerers
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    queries += 1  # feature flag
    with assert_num_queries(queries):
        response = client.get(f"/v2/reimbursements/csv?invoicesReferences={invoice_reference}")
        assert response.status_code == 200

    # Then
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.CSV_HEADER
    rows = list(reader)
    assert len(rows) == 1
