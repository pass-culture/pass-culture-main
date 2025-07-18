import csv
import datetime
from io import StringIO

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.bookings import models as bookings_models
from pcapi.core.educational import models as educational_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.routes.serialization.reimbursement_csv_serialize import ReimbursementDetails
from pcapi.utils.date import utc_datetime_to_department_timezone


@pytest.mark.usefixtures("db_session")
def test_without_reimbursement_period(client):
    user_offerer = offerers_factories.UserOffererFactory()
    pro = user_offerer.user

    offerer_id = user_offerer.offerer.id
    client = client.with_session_auth(pro.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # check user_offerer exists
    num_queries += 1  # rollback
    with testing.assert_num_queries(num_queries):
        response = client.get(f"/reimbursements/csv?offererId={offerer_id}")
        assert response.status_code == 400

    assert response.json["reimbursementPeriodBeginningDate"] == [
        "Vous devez renseigner une date au format ISO (ex. 2021-12-24)"
    ]
    assert response.json["reimbursementPeriodEndingDate"] == [
        "Vous devez renseigner une date au format ISO (ex. 2021-12-24)"
    ]


@pytest.mark.usefixtures("db_session")
def test_without_offerer_id(client):
    user_offerer = offerers_factories.UserOffererFactory()
    pro = user_offerer.user

    client = client.with_session_auth(pro.email)
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # rollback
    with testing.assert_num_queries(num_queries):
        response = client.get(
            "/reimbursements/csv?reimbursementPeriodBeginningDate=2021-01-01&reimbursementPeriodEndingDate=2021-01-15"
        )
        assert response.status_code == 400

    assert response.json["offererId"] == ["Ce champ est obligatoire"]


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "cutoff,fortnight",
    [(datetime.date(year=2023, month=1, day=16), "1ère"), (datetime.date(year=2023, month=1, day=1), "2nde")],
)
def test_with_venue_filter_with_pricings(client, cutoff, fortnight):
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
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

    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)

    for bank_account, venue in zip((bank_account_1, bank_account_2), (venue1, venue2)):
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account, date=cutoff)
        cashflow = finance_factories.CashflowFactory(
            batch=batch, creationDate=cutoff, bankAccount=bank_account, invoices=[invoice]
        )
        finance_factories.PricingFactory(  # the offer is created in  PricingFactory->booking( UsedBookingFactory)->stock(StockFactory)->offer(OfferFactory)
            booking__stock__offer__venue=venue, status=finance_models.PricingStatus.INVOICED, cashflows=[cashflow]
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account_1.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.get_csv_headers()
    rows = list(reader)
    assert len(rows) == 1
    row = rows[0]

    invoice = (
        db.session.query(finance_models.Invoice).filter(finance_models.Invoice.bankAccountId == bank_account_1.id).one()
    )
    batch = db.session.query(finance_models.CashflowBatch).one()
    offer = db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == venue1.id).one()
    booking = db.session.query(bookings_models.Booking).filter(bookings_models.Booking.venueId == venue1.id).one()
    pricing = db.session.query(finance_models.Pricing).filter(finance_models.Pricing.bookingId == booking.id).one()

    assert f"{fortnight} quinzaine" in row["Réservations concernées par le remboursement"]
    assert row["Date du justificatif"] == invoice.date.strftime("%Y-%m-%d")
    assert row["N° du justificatif"] == invoice.reference
    assert row["N° de virement"] == batch.label
    assert row["Intitulé du compte bancaire"] == bank_account_1.label
    assert row["SIRET de la structure"] == venue1.siret
    assert row["IBAN"] == bank_account_1.iban
    assert row["Raison sociale de la structure"] == venue1.name
    assert row["Adresse de l'offre"] == venue1.offererAddress.address.fullAddress
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


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "cutoff,fortnight",
    [(datetime.date(year=2023, month=1, day=16), "1ère"), (datetime.date(year=2023, month=1, day=1), "2nde")],
)
def test_with_reimbursement_period_filter_with_pricings_using_oa(client, cutoff, fortnight):
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # Within the reimbursement period filter
    invoice_1 = finance_factories.InvoiceFactory(bankAccount=bank_account, date=cutoff)
    cashflow_1 = finance_factories.CashflowFactory(
        batch=batch, creationDate=cutoff, bankAccount=bank_account, invoices=[invoice_1]
    )
    finance_factories.PricingFactory(
        booking__stock__offer__venue=venue,
        booking__dateUsed=datetime.date.today() - datetime.timedelta(days=1),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_1],
    )
    finance_factories.PricingFactory(
        booking__stock__offer__venue=venue,
        booking__dateUsed=datetime.date.today() - datetime.timedelta(days=1),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_1],
    )

    # Outside the reimbursement period filter
    invoice_2 = finance_factories.InvoiceFactory(
        bankAccount=bank_account, date=datetime.date.today() - datetime.timedelta(days=5)
    )
    cashflow_2 = finance_factories.CashflowFactory(
        batch=batch,
        creationDate=datetime.date.today() - datetime.timedelta(days=5),
        bankAccount=bank_account,
        invoices=[invoice_2],
    )
    finance_factories.PricingFactory(
        booking__stock__offer__venue=venue,
        booking__dateUsed=datetime.date.today() - datetime.timedelta(days=4),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_2],
    )
    finance_factories.PricingFactory(
        booking__stock__offer__venue=venue,
        booking__dateUsed=datetime.date.today() - datetime.timedelta(days=4),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_2],
    )

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames[:6] == ReimbursementDetails.CSV_HEADER[:6]
    assert reader.fieldnames[6:10] == [
        "SIRET de la structure",
        "Raison sociale de la structure",
        "Nom de l'offre",
        "Adresse de l'offre",
    ]
    assert reader.fieldnames[10:] == ReimbursementDetails.CSV_HEADER[10:]
    rows = list(reader)
    assert len(rows) == 2

    bookings = (
        db.session.query(bookings_models.Booking)
        .filter(bookings_models.Booking.venueId == venue.id)
        .order_by(bookings_models.Booking.dateUsed.desc(), bookings_models.Booking.id.desc())
        .all()
    )

    for row, booking in zip(rows, bookings):
        pricing = db.session.query(finance_models.Pricing).filter(finance_models.Pricing.bookingId == booking.id).one()
        cashflow = pricing.cashflows[0]
        invoice = cashflow.invoices[0]
        offer = booking.stock.offer
        batch = db.session.query(finance_models.CashflowBatch).one()

        assert f"{fortnight} quinzaine" in row["Réservations concernées par le remboursement"]
        assert row["Date du justificatif"] == invoice.date.strftime("%Y-%m-%d")
        assert row["N° du justificatif"] == invoice.reference
        assert row["N° de virement"] == batch.label
        assert row["Intitulé du compte bancaire"] == bank_account.label
        assert row["IBAN"] == bank_account.iban
        assert row["Raison sociale de la structure"] == venue.name
        assert row["Adresse de l'offre"] == venue.offererAddress.address.fullAddress
        assert row["SIRET de la structure"] == venue.siret
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


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "cutoff,fortnight",
    [(datetime.date(year=2023, month=1, day=16), "1ère"), (datetime.date(year=2023, month=1, day=1), "2nde")],
)
def test_with_bank_account_filter_with_pricings_collective_use_case(client, cutoff, fortnight):
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
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

    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)

    for bank_account, venue in zip((bank_account_1, bank_account_2), (venue1, venue2)):
        invoice = finance_factories.InvoiceFactory(bankAccount=bank_account, date=cutoff)
        cashflow = finance_factories.CashflowFactory(
            batch=batch, creationDate=cutoff, bankAccount=bank_account, invoices=[invoice]
        )
        finance_factories.CollectivePricingFactory(
            collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account_1.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.get_csv_headers()
    rows = list(reader)
    assert len(rows) == 1
    row = rows[0]

    invoice = (
        db.session.query(finance_models.Invoice).filter(finance_models.Invoice.bankAccountId == bank_account_1.id).one()
    )
    batch = db.session.query(finance_models.CashflowBatch).one()
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.venueId == venue1.id)
        .one()
    )
    collective_booking = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(educational_models.CollectiveBooking.venueId == venue1.id)
        .one()
    )
    pricing = (
        db.session.query(finance_models.Pricing)
        .filter(finance_models.Pricing.collectiveBookingId == collective_booking.id)
        .one()
    )
    redactor = collective_booking.educationalRedactor
    institution = collective_booking.educationalInstitution

    assert f"{fortnight} quinzaine" in row["Réservations concernées par le remboursement"]
    assert row["Date du justificatif"] == invoice.date.strftime("%Y-%m-%d")
    assert row["N° du justificatif"] == invoice.reference
    assert row["N° de virement"] == batch.label
    assert row["Intitulé du compte bancaire"] == bank_account_1.label
    assert row["SIRET de la structure"] == venue1.siret
    assert row["IBAN"] == bank_account_1.iban
    assert row["Raison sociale de la structure"] == venue1.name
    assert row["Adresse de l'offre"] == venue1.offererAddress.address.fullAddress
    assert row["Nom de l'offre"] == collective_offer.name
    assert row["N° de réservation (offre collective)"] == str(collective_booking.id)
    assert row["Nom (offre collective)"] == redactor.lastName
    assert row["Prénom (offre collective)"] == redactor.firstName
    assert row["Nom de l'établissement (offre collective)"] == institution.name
    assert row["Date de l'évènement (offre collective)"] == utc_datetime_to_department_timezone(
        collective_booking.collectiveStock.startDatetime, venue1.offererAddress.address.departmentCode
    ).strftime("%d/%m/%Y %H:%M")
    assert row["Contremarque"] == ""
    assert row["Date de validation de la réservation"] == collective_booking.dateUsed.strftime("%Y-%m-%d %H:%M:%S")
    assert row["Intitulé du tarif"] == ""
    assert row["Montant de la réservation"] == str(collective_booking.collectiveStock.price).replace(".", ",")
    assert row["Barème"].replace("\xa0", " ") == "100 %"
    assert row["Montant remboursé"] == "{:.2f}".format(-pricing.amount / 100).replace(".", ",")


@pytest.mark.usefixtures("db_session")
def test_no_irrelevant_data_collective_offers_use_case(client):
    # setup relevant date for filter
    cutoff = datetime.date(year=2023, month=1, day=1)
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = datetime.date(year=2023, month=1, day=16).isoformat()
    # create offerer with 3 venues
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    venue2 = offerers_factories.VenueFactory(
        managingOfferer=offerer, pricing_point="self", offererAddress__address__street="4 place du Selkirk Rex"
    )
    offerers_factories.VenueFactory(
        managingOfferer=offerer, pricing_point="self", offererAddress__address__street="4 avenue du bebe chat"
    )
    # create a bank account, link it to the first 2 venues and prepare invoice
    bank_account_1 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )

    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)

    invoice = finance_factories.InvoiceFactory(bankAccount=bank_account_1, date=cutoff)
    cashflow = finance_factories.CashflowFactory(
        batch=batch, creationDate=cutoff, bankAccount=bank_account_1, invoices=[invoice]
    )
    # create one used booking for venue1 and one booking to be reimbursed later for venue2
    finance_factories.CollectivePricingFactory(
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue1,
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow],
    )
    finance_factories.CollectivePricingFactory(
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue2,
        status=finance_models.PricingStatus.VALIDATED,
        cashflows=[cashflow],
    )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account_1.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.get_csv_headers()
    rows = list(reader)
    # We test that only the reimbursment for venue 1 is displayed and that it has the right address
    assert len(rows) == 1
    assert rows[0]["Adresse de l'offre"] == venue1.offererAddress.address.fullAddress


@pytest.mark.usefixtures("db_session")
def test_no_irrelevant_data_individual_offers_use_case(client):
    # setup relevant date for filter
    cutoff = datetime.date(year=2023, month=1, day=1)
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = datetime.date(year=2023, month=1, day=16).isoformat()
    # create offerer with 3 venues
    offerer = offerers_factories.OffererFactory()
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    venue2 = offerers_factories.VenueFactory(
        managingOfferer=offerer, pricing_point="self", offererAddress__address__street="4 place du Selkirk Rex"
    )
    offerers_factories.VenueFactory(
        managingOfferer=offerer, pricing_point="self", offererAddress__address__street="4 avenue du bebe chat"
    )
    # create a bank account, link it to the first 2 venues and prepare invoice
    bank_account_1 = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue1, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue2, bankAccount=bank_account_1, timespan=(datetime.datetime.utcnow(),)
    )

    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)

    invoice = finance_factories.InvoiceFactory(bankAccount=bank_account_1, date=cutoff)
    cashflow = finance_factories.CashflowFactory(
        batch=batch, creationDate=cutoff, bankAccount=bank_account_1, invoices=[invoice]
    )
    # create one used booking for venue1 and one booking to be reimbursed later for venue2
    finance_factories.PricingFactory(
        booking__stock__offer__venue=venue1,
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow],
    )
    finance_factories.PricingFactory(
        booking__stock__offer__venue=venue2,
        status=finance_models.PricingStatus.VALIDATED,
        cashflows=[cashflow],
    )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account_1.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.get_csv_headers()
    rows = list(reader)
    # We test that only the reimbursment for venue 1 is displayed and that it has the right address
    assert len(rows) == 1
    assert rows[0]["Adresse de l'offre"] == venue1.offererAddress.address.fullAddress


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "cutoff,fortnight",
    [(datetime.date(year=2023, month=1, day=16), "1ère"), (datetime.date(year=2023, month=1, day=1), "2nde")],
)
def test_with_reimbursement_period_filter_with_pricings_collective_use_case(client, cutoff, fortnight):
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    # Within the reimbursement period filter
    invoice_1 = finance_factories.InvoiceFactory(bankAccount=bank_account, date=cutoff)
    cashflow_1 = finance_factories.CashflowFactory(
        batch=batch, creationDate=cutoff, bankAccount=bank_account, invoices=[invoice_1]
    )
    finance_factories.CollectivePricingFactory(
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__dateUsed=datetime.date.today() - datetime.timedelta(days=1),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_1],
    )
    finance_factories.CollectivePricingFactory(
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__dateUsed=datetime.date.today() - datetime.timedelta(days=1),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_1],
    )

    # Outside the reimbursement period filter
    invoice_2 = finance_factories.InvoiceFactory(
        bankAccount=bank_account, date=datetime.date.today() - datetime.timedelta(days=5)
    )
    cashflow_2 = finance_factories.CashflowFactory(
        batch=batch,
        creationDate=datetime.date.today() - datetime.timedelta(days=5),
        bankAccount=bank_account,
        invoices=[invoice_2],
    )
    finance_factories.CollectivePricingFactory(
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__dateUsed=datetime.date.today() - datetime.timedelta(days=4),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_2],
    )
    finance_factories.CollectivePricingFactory(
        collectiveBooking__collectiveStock__collectiveOffer__venue=venue,
        collectiveBooking__dateUsed=datetime.date.today() - datetime.timedelta(days=4),
        status=finance_models.PricingStatus.INVOICED,
        cashflows=[cashflow_2],
    )

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    # Then
    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == ReimbursementDetails.get_csv_headers()
    rows = list(reader)
    assert len(rows) == 2

    collective_bookings = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(educational_models.CollectiveBooking.venueId == venue.id)
        .order_by(educational_models.CollectiveBooking.dateUsed.desc(), educational_models.CollectiveBooking.id.desc())
        .all()
    )

    for row, collective_booking in zip(rows, collective_bookings):
        pricing = (
            db.session.query(finance_models.Pricing)
            .filter(finance_models.Pricing.collectiveBookingId == collective_booking.id)
            .one()
        )
        cashflow = pricing.cashflows[0]
        invoice = cashflow.invoices[0]
        collective_offer = collective_booking.collectiveStock.collectiveOffer
        redactor = collective_booking.educationalRedactor
        institution = collective_booking.educationalInstitution
        batch = db.session.query(finance_models.CashflowBatch).one()

        assert f"{fortnight} quinzaine" in row["Réservations concernées par le remboursement"]
        assert row["Date du justificatif"] == invoice.date.strftime("%Y-%m-%d")
        assert row["N° du justificatif"] == invoice.reference
        assert row["N° de virement"] == batch.label
        assert row["Intitulé du compte bancaire"] == bank_account.label
        assert row["SIRET de la structure"] == venue.siret
        assert row["IBAN"] == bank_account.iban
        assert row["Raison sociale de la structure"] == venue.name
        assert row["Adresse de l'offre"] == venue.offererAddress.address.fullAddress
        assert row["Nom de l'offre"] == collective_offer.name
        assert row["N° de réservation (offre collective)"] == str(collective_booking.id)
        assert row["Nom (offre collective)"] == redactor.lastName
        assert row["Prénom (offre collective)"] == redactor.firstName
        assert row["Nom de l'établissement (offre collective)"] == institution.name
        assert row["Date de l'évènement (offre collective)"] == utc_datetime_to_department_timezone(
            collective_booking.collectiveStock.startDatetime, venue.offererAddress.address.departmentCode
        ).strftime("%d/%m/%Y %H:%M")
        assert row["Contremarque"] == ""
        assert row["Date de validation de la réservation"] == collective_booking.dateUsed.strftime("%Y-%m-%d %H:%M:%S")
        assert row["Intitulé du tarif"] == ""
        assert row["Montant de la réservation"] == str(collective_booking.collectiveStock.price).replace(".", ",")
        assert row["Barème"].replace("\xa0", " ") == "100 %"
        assert row["Montant remboursé"] == "{:.2f}".format(-pricing.amount / 100).replace(".", ",")


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "offer_has_oa, len_offerer_addresses, expected_address",
    [
        (True, 2, "1 rue de la paix 75002 Paris"),
        (False, 1, "1 boulevard Poissonnière 75002 Paris"),
        (True, 2, "1 rue de la paix 75002 Paris"),
    ],
)
def test_with_offer_address_and_venue_address(client, offer_has_oa, len_offerer_addresses, expected_address):
    """This case consider venue with oa and offer with oa"""

    cutoff = datetime.date(year=2023, month=1, day=1)
    beginning_date_iso_format = (cutoff - datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = (cutoff + datetime.timedelta(days=2)).isoformat()
    ending_date_iso_format = datetime.date(year=2023, month=1, day=16).isoformat()
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        pricing_point="self",
        offererAddress__address__street="1 boulevard Poissonnière",
        offererAddress__address__postalCode="75002",
        offererAddress__address__city="Paris",
    )
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow(),)
    )
    batch = finance_factories.CashflowBatchFactory(cutoff=cutoff)

    invoice = finance_factories.InvoiceFactory(bankAccount=bank_account, date=cutoff)
    cashflow = finance_factories.CashflowFactory(
        batch=batch, creationDate=cutoff, bankAccount=bank_account, invoices=[invoice]
    )
    if offer_has_oa:
        oa = offerers_factories.OffererAddressFactory(
            address__street="1 rue de la paix",
            address__postalCode="75002",
            address__city="Paris",
        )
        finance_factories.PricingFactory(  # the offer is created in  PricingFactory->booking( UsedBookingFactory)->stock(StockFactory)->offer(OfferFactory)
            booking__stock__offer__venue=venue,
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
            booking__stock__offer__offererAddress=oa,
        )
    else:
        finance_factories.PricingFactory(  # the offer is created in  PricingFactory->booking( UsedBookingFactory)->stock(StockFactory)->offer(OfferFactory)
            booking__stock__offer__venue=venue,
            status=finance_models.PricingStatus.INVOICED,
            cashflows=[cashflow],
            booking__stock__offer__offererAddress=None,
        )
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

    client = client.with_session_auth(pro.email)
    bank_account_id = bank_account.id  # avoid extra SQL query below
    queries = testing.AUTHENTICATION_QUERIES
    queries += 1  # check user has access to offerer
    queries += 1  # select booking and related items
    queries += 1  # select educational redactor
    with testing.assert_num_queries(queries):
        response = client.get(
            f"/reimbursements/csv?reimbursementPeriodBeginningDate={beginning_date_iso_format}&reimbursementPeriodEndingDate={ending_date_iso_format}&bankAccountId={bank_account_id}&offererId={offerer.id}"
        )
        assert response.status_code == 200

    offers = db.session.query(offers_models.Offer).all()
    addresses = db.session.query(offerers_models.OffererAddress).all()
    bookings = db.session.query(bookings_models.Booking).all()

    assert response.headers["Content-type"] == "text/csv; charset=utf-8;"
    assert response.headers["Content-Disposition"] == "attachment; filename=remboursements_pass_culture.csv"
    reader = csv.DictReader(StringIO(response.data.decode("utf-8-sig")), delimiter=";")
    assert reader.fieldnames == [
        "Réservations concernées par le remboursement",
        "Date du justificatif",
        "N° du justificatif",
        "N° de virement",
        "Intitulé du compte bancaire",
        "IBAN",
        "SIRET de la structure",
        "Raison sociale de la structure",
        "Nom de l'offre",
        "Adresse de l'offre",
        "N° de réservation (offre collective)",
        "Nom (offre collective)",
        "Prénom (offre collective)",
        "Nom de l'établissement (offre collective)",
        "Date de l'évènement (offre collective)",
        "Contremarque",
        "Date de validation de la réservation",
        "Intitulé du tarif",
        "Montant de la réservation",
        "Barème",
        "Montant remboursé",
        "Type d'offre",
    ]
    rows = list(reader)
    assert len(rows) == 1
    assert len(bookings) == 1
    assert len(offers) == 1
    assert len(addresses) == len_offerer_addresses
    assert rows[0]["Adresse de l'offre"].strip() == expected_address
