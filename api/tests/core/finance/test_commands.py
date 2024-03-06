import datetime
from unittest.mock import patch

import pcapi.core.categories.subcategories_v2 as subcategories
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import db

from tests.conftest import clean_database
from tests.test_utils import run_command


class AddCustomOfferReimbursementRuleTest:
    @clean_database
    def test_basics(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id
        # fmt: off
        result = run_command(
            app,
            "add_custom_offer_reimbursement_rule",
            "--offer-id", offer.id,
            "--offer-original-amount", "24,68",
            "--offerer-id", str(offer.venue.managingOffererId),
            "--reimbursed-amount", "12.34",
            "--valid-from", "2030-01-01",
            "--valid-until", "2030-01-02",
        )

        # fmt: on
        assert "Created new rule" in result.output
        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.offer.id == offer_id
        assert rule.amount == 1234

    @clean_database
    def test_warnings(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        # fmt: off
        result = run_command(
            app,
            "add_custom_offer_reimbursement_rule",
            "--offer-id", offer.id,
            "--offer-original-amount", "0,34",  # wrong amount
            "--offerer-id", str(offer.venue.managingOffererId + 7),
            "--reimbursed-amount", "12.34",
            "--valid-from", "2030-01-01",
            "--valid-until", "2030-01-02",
        )
        # fmt: on
        assert "Command has failed" in result.output
        assert "Mismatch on offerer" in result.output
        assert "Mismatch on original amount" in result.output
        assert finance_models.CustomReimbursementRule.query.count() == 0

    @clean_database
    def test_force_with_warnings(self, app):
        stock = offers_factories.StockFactory(price=24.68)
        offer = stock.offer
        offer_id = offer.id

        # fmt: off
        result = run_command(
            app,
            "add_custom_offer_reimbursement_rule",
            "--offer-id", offer.id,
            "--offer-original-amount", "0,34",  # wrong amount
            "--offerer-id", str(offer.venue.managingOffererId + 7),
            "--reimbursed-amount", "12.34",
            "--valid-from", "2030-01-01",
            "--valid-until", "2030-01-02",
            "--force",
        )
        # fmt: on
        assert "Created new rule" in result.output
        rule = finance_models.CustomReimbursementRule.query.one()
        assert rule.offer.id == offer_id
        assert rule.amount == 1234


@override_settings(SLACK_GENERATE_INVOICES_FINISHED_CHANNEL="channel")
@override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
@clean_database
def test_generate_invoices_internal_notification(app, css_font_http_request_mock):
    venue = offerers_factories.VenueFactory()
    batch = finance_factories.CashflowBatchFactory()
    finance_factories.CashflowFactory.create_batch(
        size=3,
        batch=batch,
        reimbursementPoint=venue,
        status=finance_models.CashflowStatus.UNDER_REVIEW,
    )
    finance_factories.BankInformationFactory(venue=venue)

    with patch("pcapi.core.finance.commands.send_internal_message") as mock_send_internal_message:
        run_command(
            app,
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


@override_features(WIP_ENABLE_FINANCE_INCIDENT=True, WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
@clean_database
def test_when_there_is_a_debit_note_to_generate_on_total_incident(app, css_font_http_request_mock):
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
        app,
        "generate_invoices",
        "--batch-id",
        str(first_batch.id),
    )

    db.session.flush()

    invoices = finance_models.Invoice.query.order_by(finance_models.Invoice.date).all()
    assert len(invoices) == 1
    assert invoices[0].reference.startswith("F")
    assert invoices[0].amount == -2850
    assert invoices[0].bankAccountId == bank_account_id
    assert len(invoices[0].lines) == 1

    ## Two weeks later

    previous_incident_booking = finance_models.FinanceEvent.query.filter_by(id=previous_incident_booking_id).one()
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
        app,
        "generate_invoices",
        "--batch-id",
        str(second_batch.id),
    )

    invoices = finance_models.Invoice.query.order_by(finance_models.Invoice.date).all()
    assert len(invoices) == 2
    assert invoices[1].reference.startswith("A")
    assert invoices[1].amount == 2850
    assert invoices[1].bankAccountId == bank_account_id
    assert len(invoices[1].lines) == 1
    assert invoices[1].amount == -invoices[0].amount


@override_features(WIP_ENABLE_FINANCE_INCIDENT=True, WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=True)
@clean_database
def test_when_there_is_a_debit_note_to_generate_on_partial_incident(app, css_font_http_request_mock):
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
        app,
        "generate_invoices",
        "--batch-id",
        str(first_batch.id),
    )

    db.session.flush()

    invoices = finance_models.Invoice.query.all()
    assert len(invoices) == 1
    assert invoices[0].reference.startswith("F")
    assert invoices[0].amount == -3000
    assert invoices[0].bankAccountId == bank_account_id
    assert len(invoices[0].lines) == 1

    ## Two weeks later

    previous_incident_booking = finance_models.FinanceEvent.query.filter_by(id=previous_incident_booking_id).one()
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
        app,
        "generate_invoices",
        "--batch-id",
        str(second_batch.id),
    )

    invoices = finance_models.Invoice.query.all()
    assert len(invoices) == 2
    assert invoices[1].reference.startswith("A")
    assert invoices[1].bankAccountId == bank_account_id
    assert len(invoices[1].lines) == 1
    assert invoices[1].amount == -invoices[0].amount / 2
    assert invoices[1].amount == 1500
