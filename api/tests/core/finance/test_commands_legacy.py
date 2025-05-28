import csv
import datetime
import io
import zipfile
from decimal import Decimal
from unittest.mock import patch

import pytest

from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.utils import human_ids


pytestmark = [
    pytest.mark.features(WIP_ENABLE_NEW_FINANCE_WORKFLOW=False),
]


@pytest.mark.settings(SLACK_GENERATE_INVOICES_FINISHED_CHANNEL="channel")
def test_generate_invoices_internal_notification(run_command, css_font_http_request_mock):
    offerer = offerers_factories.OffererFactory()
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    offerers_factories.VenueFactory(bank_account=bank_account)
    batch = finance_factories.CashflowBatchFactory()
    finance_factories.CashflowFactory.create_batch(
        size=3,
        batch=batch,
        bankAccount=bank_account,
        status=finance_models.CashflowStatus.UNDER_REVIEW,
    )

    with patch("pcapi.core.finance.commands.send_internal_message") as mock_send_internal_message:
        run_command(
            "generate_invoices",
            "--batch-id",
            str(batch.id),
        )

    assert mock_send_internal_message.call_count == 1
    call_kwargs = mock_send_internal_message.call_args.kwargs
    assert len(call_kwargs["blocks"]) == 1
    call_block = call_kwargs["blocks"][0]
    assert call_block["text"]["text"] == f"La Génération de factures ({batch.label}) est terminée avec succès"
    assert call_block["text"]["type"] == "mrkdwn"
    assert call_block["type"] == "section"

    assert call_kwargs["channel"] == "channel"
    assert call_kwargs["icon_emoji"] == ":large_green_circle:"


def test_when_there_is_a_debit_note_to_generate_on_total_incident(run_command, css_font_http_request_mock):
    sixteen_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=16)
    fifteen_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=15)
    fourteen_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=14)

    user = users_factories.RichBeneficiaryFactory()
    venue_kwargs = {
        "pricing_point": "self",
    }
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, **venue_kwargs)
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    bank_account_id = bank_account.id
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account, timespan=[sixteen_days_ago, None]
    )

    # Invoice Part
    book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    finance_factories.CustomReimbursementRuleFactory(amount=2850, offer=book_offer)

    incident_booking1_event = finance_factories.UsedBookingFinanceEventFactory(
        booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
        booking__user=user,
        booking__amount=30,
        booking__quantity=1,
        booking__dateCreated=sixteen_days_ago,
    )

    finance_api.price_event(incident_booking1_event)
    incident_booking1_event.booking.pricings[0].creationDate = fifteen_days_ago
    incident_booking1_event.booking.pricings[0].valueDate = fifteen_days_ago

    incident_booking1_event.booking.dateUsed = fifteen_days_ago
    first_batch = finance_api.generate_cashflows_and_payment_files(fourteen_days_ago)
    previous_incident_booking_id = incident_booking1_event.id

    run_command(
        "generate_invoices",
        "--batch-id",
        str(first_batch.id),
    )

    db.session.flush()

    invoices = db.session.query(finance_models.Invoice).order_by(finance_models.Invoice.date).all()
    assert len(invoices) == 1
    assert invoices[0].reference.startswith("F")
    assert invoices[0].amount == -2850
    assert invoices[0].bankAccountId == bank_account_id
    assert len(invoices[0].lines) == 1

    ## Two weeks later

    previous_incident_booking = (
        db.session.query(finance_models.FinanceEvent).filter_by(id=previous_incident_booking_id).one()
    )
    # Debit Note part
    booking_total_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        incident__status=finance_models.IncidentStatus.VALIDATED,
        incident__forceDebitNote=True,
        incident__venue=venue,
        booking=previous_incident_booking.booking,
        newTotalAmount=-previous_incident_booking.booking.total_amount * 100,
    )
    incident_event = finance_api._create_finance_events_from_incident(
        booking_total_incident, datetime.datetime.utcnow()
    )

    finance_api.price_event(incident_event[0])

    second_batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())

    run_command(
        "generate_invoices",
        "--batch-id",
        str(second_batch.id),
    )

    invoices = db.session.query(finance_models.Invoice).order_by(finance_models.Invoice.date).all()
    assert len(invoices) == 2
    assert invoices[1].reference.startswith("A")
    assert invoices[1].amount == 2850
    assert invoices[1].bankAccountId == bank_account_id
    assert len(invoices[1].lines) == 1
    assert invoices[1].amount == -invoices[0].amount


def test_when_there_is_a_debit_note_to_generate_on_partial_incident(run_command, css_font_http_request_mock):
    sixteen_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=16)
    fifteen_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=15)
    fourteen_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=14)

    user = users_factories.RichBeneficiaryFactory()
    venue_kwargs = {
        "pricing_point": "self",
    }
    offerer = offerers_factories.OffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=offerer, **venue_kwargs)
    bank_account = finance_factories.BankAccountFactory(offerer=offerer)
    bank_account_id = bank_account.id

    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account, timespan=[sixteen_days_ago, None]
    )

    # Invoice Part
    book_offer = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)

    incident_booking1_event = finance_factories.UsedBookingFinanceEventFactory(
        booking__stock=offers_factories.StockFactory(offer=book_offer, price=30, quantity=1),
        booking__user=user,
        booking__amount=30,
        booking__quantity=1,
        booking__dateCreated=sixteen_days_ago,
    )

    finance_api.price_event(incident_booking1_event)
    incident_booking1_event.booking.pricings[0].creationDate = fifteen_days_ago
    incident_booking1_event.booking.pricings[0].valueDate = fifteen_days_ago

    incident_booking1_event.booking.dateUsed = fifteen_days_ago
    first_batch = finance_api.generate_cashflows_and_payment_files(fourteen_days_ago)
    previous_incident_booking_id = incident_booking1_event.id

    run_command(
        "generate_invoices",
        "--batch-id",
        str(first_batch.id),
    )

    db.session.flush()

    invoices = db.session.query(finance_models.Invoice).all()
    assert len(invoices) == 1
    assert invoices[0].reference.startswith("F")
    assert invoices[0].amount == -3000
    assert invoices[0].bankAccountId == bank_account_id
    assert len(invoices[0].lines) == 1

    ## Two weeks later

    previous_incident_booking = (
        db.session.query(finance_models.FinanceEvent).filter_by(id=previous_incident_booking_id).one()
    )
    # Debit Note part
    booking_partial_incident = finance_factories.IndividualBookingFinanceIncidentFactory(
        incident__status=finance_models.IncidentStatus.VALIDATED,
        incident__forceDebitNote=True,
        incident__venue=venue,
        booking=previous_incident_booking.booking,
        newTotalAmount=((previous_incident_booking.booking.total_amount * 100) / 2),
    )
    incident_events = finance_api._create_finance_events_from_incident(
        booking_partial_incident, datetime.datetime.utcnow()
    )

    for incident_event in incident_events:
        finance_api.price_event(incident_event)

    second_batch = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    run_command(
        "generate_invoices",
        "--batch-id",
        str(second_batch.id),
    )

    invoices = db.session.query(finance_models.Invoice).order_by(finance_models.Invoice.id).all()
    assert len(invoices) == 2
    assert invoices[1].reference.startswith("A")
    assert invoices[1].bankAccountId == bank_account_id
    assert len(invoices[1].lines) == 1
    assert invoices[1].amount == -invoices[0].amount / 2
    assert invoices[1].amount == 1500


def test_generate_invoice_file_with_debit_note(run_command, tmp_path, monkeypatch, css_font_http_request_mock):
    _paths = []

    def _upload_files_to_google_drive(folder_name, paths) -> None:
        nonlocal _paths
        _paths = paths

    monkeypatch.setattr(finance_api, "_upload_files_to_google_drive", _upload_files_to_google_drive)
    monkeypatch.setattr(finance_api.tempfile, "mkdtemp", lambda: tmp_path)

    offerer1 = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
    bank_account1 = finance_factories.BankAccountFactory(offerer=offerer1)
    venue1 = offerers_factories.VenueFactory(pricing_point="self", managingOfferer=offerer1, bank_account=bank_account1)
    author_user = users_factories.UserFactory()

    user1 = users_factories.BeneficiaryGrant18Factory()
    ############################################################################
    # Create an offer, book it, invoice it and reimburse it for bank_account 1 #
    ############################################################################
    booking1 = bookings_factories.BookingFactory(
        user=user1,
        quantity=13,
        stock__price=Decimal("5.0"),
        stock__offer__venue=venue1,
    )  # 65€
    bookings_api.mark_as_used(
        booking=booking1,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    finance_events = db.session.query(finance_models.FinanceEvent).all()
    assert len(finance_events) == 1

    initial_finance_event = finance_events[0]
    finance_api.price_event(initial_finance_event)

    cashflow_batch1 = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    run_command(
        "generate_invoices",
        "--batch-id",
        str(cashflow_batch1.id),
    )
    db.session.add_all([cashflow_batch1, booking1, bank_account1, author_user, initial_finance_event])
    assert len(cashflow_batch1.cashflows) == 1
    cashflow1 = cashflow_batch1.cashflows[0]
    assert len(cashflow1.invoices) == 1
    invoice1 = cashflow1.invoices[0]
    assert booking1.status == bookings_models.BookingStatus.REIMBURSED

    assert len(_paths) == 1
    path = _paths[0]
    with zipfile.ZipFile(path) as zfile:
        invoices_files = [
            file_name for file_name in zfile.namelist() if file_name.startswith(f"invoices_{cashflow_batch1.label}")
        ]
        assert len(invoices_files) == 1
        with zfile.open(invoices_files[0]) as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 2
    assert {"offerer contribution", "offerer revenue"} == {row["Type de ticket de facturation"] for row in rows}
    row_revenue1 = next(row for row in rows if row["Type de ticket de facturation"] == "offerer revenue")
    assert row_revenue1["Identifiant des coordonnées bancaires"] == str(bank_account1.id)
    assert row_revenue1["Identifiant humanisé des coordonnées bancaires"] == human_ids.humanize(bank_account1.id)
    assert row_revenue1["Référence du justificatif"] == invoice1.reference
    assert row_revenue1["Somme des tickets de facturation"] == Decimal("-6500.0")

    row_contribution1 = next(row for row in rows if row["Type de ticket de facturation"] == "offerer contribution")
    assert row_contribution1["Identifiant des coordonnées bancaires"] == str(bank_account1.id)
    assert row_contribution1["Identifiant humanisé des coordonnées bancaires"] == human_ids.humanize(bank_account1.id)
    assert row_contribution1["Référence du justificatif"] == invoice1.reference
    assert row_contribution1["Somme des tickets de facturation"] == Decimal("0")

    #################################################
    # Create an overpayment incident for debit note #
    #################################################
    incident = finance_api.create_overpayment_finance_incident(
        bookings=[booking1],
        author=author_user,
        origin=finance_models.FinanceIncidentRequestOrigin.SUPPORT_PRO,
        comment="BO",
        amount=Decimal("30"),
    )

    finance_api.validate_finance_overpayment_incident(
        finance_incident=incident,
        force_debit_note=True,
        author=author_user,
    )

    finance_events = (
        db.session.query(finance_models.FinanceEvent)
        .filter(finance_models.FinanceEvent.id != initial_finance_event.id)
        .all()
    )
    assert len(finance_events) == 2
    assert {finance_event.motive for finance_event in finance_events} == {
        finance_models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT,
        finance_models.FinanceEventMotive.INCIDENT_NEW_PRICE,
    }
    for finance_event in finance_events:
        finance_api.price_event(finance_event)

    ###########################################################################
    # Create a second booking to reimburse and include it in the invoices csv #
    ###########################################################################

    offerer2 = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318460")
    bank_account2 = finance_factories.BankAccountFactory(offerer=offerer2)
    venue2 = offerers_factories.VenueFactory(pricing_point="self", managingOfferer=offerer2, bank_account=bank_account2)

    user2 = users_factories.BeneficiaryGrant18Factory()
    booking2 = bookings_factories.BookingFactory(
        user=user2,
        quantity=4,
        stock__price=Decimal("5.0"),
        stock__offer__venue=venue2,
    )  # 20€
    bookings_api.mark_as_used(
        booking=booking2,
        validation_author_type=bookings_models.BookingValidationAuthorType.OFFERER,
    )
    finance_events = booking2.finance_events
    assert len(finance_events) == 1

    finance_event = finance_events[0]
    finance_api.price_event(finance_event)

    ####################################################################################################
    # Generate the cashflows and the invoice csv that should include both lines for income and outcome #
    ####################################################################################################
    cashflow_batch2 = finance_api.generate_cashflows_and_payment_files(cutoff=datetime.datetime.utcnow())
    run_command(
        "generate_invoices",
        "--batch-id",
        str(cashflow_batch2.id),
    )
    db.session.add_all([cashflow_batch2, booking2, bank_account1, bank_account2])
    assert len(cashflow_batch2.cashflows) == 2
    assert {cashflow.bankAccountId for cashflow in cashflow_batch2.cashflows} == {bank_account1.id, bank_account2.id}
    cashflow2 = next(c for c in cashflow_batch2.cashflows if c.bankAccountId == bank_account1.id)
    assert len(cashflow2.invoices) == 1
    invoice2 = cashflow2.invoices[0]
    cashflow3 = next(c for c in cashflow_batch2.cashflows if c.bankAccountId == bank_account2.id)
    assert len(cashflow3.invoices) == 1
    invoice3 = cashflow3.invoices[0]
    assert booking2.status == bookings_models.BookingStatus.REIMBURSED

    assert len(_paths) == 1
    path = _paths[0]
    with zipfile.ZipFile(path) as zfile:
        invoices_files = [
            file_name for file_name in zfile.namelist() if file_name.startswith(f"invoices_{cashflow_batch2.label}")
        ]
        assert len(invoices_files) == 1
        with zfile.open(invoices_files[0]) as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 4
    assert {r["Référence du justificatif"] for r in rows} == {invoice2.reference, invoice3.reference}
    assert invoice2.reference.startswith("A")  # →  debit note
    invoice2_rows = [row for row in rows if row["Référence du justificatif"] == invoice2.reference]
    assert len(invoice2_rows) == 2

    assert {"offerer contribution", "offerer revenue"} == {
        row["Type de ticket de facturation"] for row in invoice2_rows
    }
    row_revenue2 = next(row for row in invoice2_rows if row["Type de ticket de facturation"] == "offerer revenue")
    assert row_revenue2["Identifiant des coordonnées bancaires"] == str(bank_account1.id)
    assert row_revenue2["Identifiant humanisé des coordonnées bancaires"] == human_ids.humanize(bank_account1.id)
    assert row_revenue2["Somme des tickets de facturation"] == Decimal("3000.0")
    assert row_revenue2["Type de réservation"] == "PR18+"

    row_contribution2 = next(
        row for row in invoice2_rows if row["Type de ticket de facturation"] == "offerer contribution"
    )
    assert row_contribution2["Identifiant des coordonnées bancaires"] == str(bank_account1.id)
    assert row_contribution2["Identifiant humanisé des coordonnées bancaires"] == human_ids.humanize(bank_account1.id)
    assert row_contribution2["Somme des tickets de facturation"] == Decimal("0")
    assert row_contribution2["Type de réservation"] == "PR18+"

    invoice3_rows = [row for row in rows if row["Référence du justificatif"] == invoice3.reference]
    assert len(invoice3_rows) == 2

    assert {"offerer contribution", "offerer revenue"} == {
        row["Type de ticket de facturation"] for row in invoice3_rows
    }
    row_revenue3 = next(row for row in invoice3_rows if row["Type de ticket de facturation"] == "offerer revenue")
    assert row_revenue3["Identifiant des coordonnées bancaires"] == str(bank_account2.id)
    assert row_revenue3["Identifiant humanisé des coordonnées bancaires"] == human_ids.humanize(bank_account2.id)
    assert row_revenue3["Somme des tickets de facturation"] == Decimal("-2000.0")

    row_contribution3 = next(
        row for row in invoice3_rows if row["Type de ticket de facturation"] == "offerer contribution"
    )
    assert row_contribution3["Identifiant des coordonnées bancaires"] == str(bank_account2.id)
    assert row_contribution3["Identifiant humanisé des coordonnées bancaires"] == human_ids.humanize(bank_account2.id)
    assert row_contribution3["Somme des tickets de facturation"] == Decimal("0")
