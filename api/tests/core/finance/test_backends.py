import datetime
from typing import NamedTuple

import pytest
import time_machine

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingRecreditType
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.dummy import bank_accounts as dummy_bank_accounts
from pcapi.core.finance.backend.dummy import invoices as dummy_invoices
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.utils import db as db_utils


pytestmark = [
    pytest.mark.usefixtures("db_session"),
]


@pytest.fixture(name="cegid_auth_token")
def cegid_auth_token_fixture(faker):
    return {
        "access_token": faker.pystr(min_chars=43, max_chars=43),
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "api",
    }


@pytest.fixture(name="cegid_config")
def cegid_config_fixture(faker, settings):
    client_id = faker.uuid4().upper()

    class Config(NamedTuple):
        CEGID_URL: str = faker.uri()
        CEGID_USERNAME: str = faker.user_name()
        CEGID_PASSWORD: str = faker.password()
        CEGID_CLIENT_ID: str = f"{client_id}@PASS_CULTURE_TEST"
        CEGID_CLIENT_SECRET: str = faker.pystr(min_chars=22, max_chars=22)

    config = Config()
    settings.CEGID_URL = config.CEGID_URL
    settings.CEGID_USERNAME = config.CEGID_USERNAME
    settings.CEGID_PASSWORD = config.CEGID_PASSWORD
    settings.CEGID_CLIENT_ID = config.CEGID_CLIENT_ID
    settings.CEGID_CLIENT_SECRET = config.CEGID_CLIENT_SECRET
    yield config


@pytest.fixture(name="mock_cegid_auth")
def mock_cegid_auth_fixture(cegid_config, requests_mock, cegid_auth_token):
    yield requests_mock.register_uri(
        "POST",
        f"{cegid_config.CEGID_URL}/identity/connect/token",
        json=cegid_auth_token,
        status_code=200,
    )


@pytest.mark.usefixtures("clean_dummy_backend_data")
class DummyFinanceBackendTest:
    def test_get_backend(self):
        current_backend = finance_backend._get_backend()
        assert isinstance(current_backend, finance_backend.DummyFinanceBackend)

    def test_push_invoice(self):
        invoice = finance_factories.InvoiceFactory()
        finance_backend.push_invoice(invoice.id)
        assert invoice in dummy_invoices

    def test_push_bank_account(self):
        bank_account = finance_factories.BankAccountFactory()
        finance_backend.push_bank_account(bank_account.id)
        assert bank_account in dummy_bank_accounts

    def test_get_invoice(self):
        invoice = finance_factories.InvoiceFactory()
        invoice_dict = finance_backend.get_invoice(invoice.reference)
        assert invoice_dict == invoice.__dict__

    def test_get_bank_account(self):
        bank_account = finance_factories.BankAccountFactory()
        bank_account_dict = finance_backend.get_bank_account(bank_account.id)
        assert bank_account_dict == bank_account.__dict__


class BaseBackendTest:
    @pytest.mark.parametrize(
        "used_recredit_type,deposit_type,pricing_line_category,product_id,title",
        [
            (
                None,
                finance_models.DepositType.GRANT_18,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORINDGRANT_18",
                "Réservations",
            ),
            (
                None,
                finance_models.DepositType.GRANT_18,
                finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
                "OCINDGRANT_18",
                "Réservations",
            ),
            (
                None,
                finance_models.DepositType.GRANT_18,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGINDGRANT_18",
                "Gestes commerciaux",
            ),
            (
                None,
                finance_models.DepositType.GRANT_15_17,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORINDGRANT_15_17",
                "Réservations",
            ),
            (
                None,
                finance_models.DepositType.GRANT_15_17,
                finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
                "OCINDGRANT_15_17",
                "Réservations",
            ),
            (
                None,
                finance_models.DepositType.GRANT_15_17,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGINDGRANT_15_17",
                "Gestes commerciaux",
            ),
            (
                BookingRecreditType.RECREDIT_18,
                finance_models.DepositType.GRANT_17_18,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORINDGRANT_18_V3",
                "Réservations",
            ),
            (
                BookingRecreditType.RECREDIT_18,
                finance_models.DepositType.GRANT_17_18,
                finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
                "OCINDGRANT_18_V3",
                "Réservations",
            ),
            (
                BookingRecreditType.RECREDIT_18,
                finance_models.DepositType.GRANT_17_18,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGINDGRANT_18_V3",
                "Gestes commerciaux",
            ),
            (
                BookingRecreditType.RECREDIT_17,
                finance_models.DepositType.GRANT_17_18,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORINDGRANT_17_V3",
                "Réservations",
            ),
            (
                BookingRecreditType.RECREDIT_17,
                finance_models.DepositType.GRANT_17_18,
                finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
                "OCINDGRANT_17_V3",
                "Réservations",
            ),
            (
                BookingRecreditType.RECREDIT_17,
                finance_models.DepositType.GRANT_17_18,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGINDGRANT_17_V3",
                "Gestes commerciaux",
            ),
            (
                None,
                finance_models.DepositType.GRANT_FREE,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORINDGRANT_FREE",
                "Réservations",
            ),
            (
                None,
                finance_models.DepositType.GRANT_FREE,
                finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
                "OCINDGRANT_FREE",
                "Réservations",
            ),
        ],
    )
    def test_get_invoice_line_indiv(self, used_recredit_type, deposit_type, pricing_line_category, product_id, title):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        booking = bookings_factories.UsedBookingFactory(
            user__deposit__type=deposit_type, stock__offer__venue=venue, usedRecreditType=used_recredit_type
        )
        pricing = finance_factories.PricingFactory(
            booking=booking, pricingPoint=venue, status=finance_models.PricingStatus.PROCESSED, amount=-42_66
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=pricing_line_category,
            amount=-42_66,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 1
        invoice_line = invoice_lines[0]
        assert len(invoice_line) == 3
        assert invoice_line["amount"] == -42_66
        assert invoice_line["product_id"] == product_id
        assert invoice_line["title"] == title

    def test_get_invoice_line_identical_pricing_lines(self):
        offerer = offerers_factories.OffererFactory(name="Association de chanteurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        booking1, booking2 = bookings_factories.UsedBookingFactory.create_batch(
            size=2,
            user__deposit__type=finance_models.DepositType.GRANT_18,
            stock__offer__venue=venue,
        )
        pricing1 = finance_factories.PricingFactory(
            booking=booking1,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
            amount=-2_00,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing1,
            category=finance_models.PricingLineCategory.OFFERER_REVENUE,
            amount=-1_00,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing1,
            category=finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
            amount=-1_00,
        )
        pricing2 = finance_factories.PricingFactory(
            booking=booking2,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
            amount=-2_00,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing2,
            category=finance_models.PricingLineCategory.OFFERER_REVENUE,
            amount=-1_00,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing2,
            category=finance_models.PricingLineCategory.OFFERER_CONTRIBUTION,
            amount=-1_00,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing1, pricing2])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 2
        assert {"OCINDGRANT_18", "ORINDGRANT_18"} == {e["product_id"] for e in invoice_lines}
        offerer_revenue_line = [e for e in invoice_lines if e["product_id"] == "ORINDGRANT_18"][0]
        assert offerer_revenue_line["amount"] == -200
        assert offerer_revenue_line["title"] == "Réservations"

        offerer_contribution_line = [e for e in invoice_lines if e["product_id"] == "OCINDGRANT_18"][0]
        assert offerer_contribution_line["amount"] == -200
        assert offerer_contribution_line["title"] == "Réservations"

    @pytest.mark.parametrize(
        "ministry,pricing_line_category,product_id,title",
        [
            (
                educational_models.Ministry.EDUCATION_NATIONALE.name,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORCOLEDUC_NAT",
                "Réservations",
            ),
            (
                educational_models.Ministry.EDUCATION_NATIONALE.name,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGCOLEDUC_NAT",
                "Gestes commerciaux",
            ),
            (
                educational_models.Ministry.AGRICULTURE.name,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORCOLAGRI",
                "Réservations",
            ),
            (
                educational_models.Ministry.AGRICULTURE.name,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGCOLAGRI",
                "Gestes commerciaux",
            ),
            (
                educational_models.Ministry.ARMEES.name,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORCOLARMEES",
                "Réservations",
            ),
            (
                educational_models.Ministry.ARMEES.name,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGCOLARMEES",
                "Gestes commerciaux",
            ),
            (
                educational_models.Ministry.MER.name,
                finance_models.PricingLineCategory.OFFERER_REVENUE,
                "ORCOLMER",
                "Réservations",
            ),
            (
                educational_models.Ministry.MER.name,
                finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
                "CGCOLMER",
                "Gestes commerciaux",
            ),
        ],
    )
    def test_get_invoice_line_collective_ministry(self, ministry, pricing_line_category, product_id, title):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        year = educational_factories.EducationalYearFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=year,
            ministry=ministry,
        )
        booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            educationalInstitution=educational_institution,
            educationalYear=year,
        )
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking=booking,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
            amount=-39_66,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=pricing_line_category,
            amount=-39_66,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 1
        invoice_line = invoice_lines[0]
        assert len(invoice_line) == 3
        assert invoice_line["amount"] == -39_66
        assert invoice_line["product_id"] == product_id
        assert invoice_line["title"] == title

    @pytest.mark.parametrize(
        "pricing_line_category,product_id,title",
        [
            (finance_models.PricingLineCategory.OFFERER_REVENUE, "ORCOLMEG", "Réservations"),
            (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, "CGCOLMEG", "Gestes commerciaux"),
        ],
    )
    def test_get_invoice_line_collective_meg(self, pricing_line_category, product_id, title):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        year = educational_factories.EducationalYearFactory()
        meg_program = educational_factories.EducationalInstitutionProgramFactory(name="marseille_en_grand")
        educational_institution = educational_factories.EducationalInstitutionFactory(
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(program=meg_program)
            ]
        )
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE.name,
        )
        booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            educationalInstitution=educational_institution,
            educationalYear=year,
        )
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking=booking,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
            amount=-538_55,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=pricing_line_category,
            amount=-538_55,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 1
        invoice_line = invoice_lines[0]
        assert len(invoice_line) == 3
        assert invoice_line["amount"] == -538_55
        assert invoice_line["product_id"] == product_id
        assert invoice_line["title"] == title

    @pytest.mark.parametrize(
        "pricing_line_category,product_id,title",
        [
            (finance_models.PricingLineCategory.OFFERER_REVENUE, "ORCOLEDUC_NAT", "Réservations"),
            (finance_models.PricingLineCategory.COMMERCIAL_GESTURE, "CGCOLEDUC_NAT", "Gestes commerciaux"),
        ],
    )
    def test_get_invoice_line_collective_when_leaving_meg(self, pricing_line_category, product_id, title):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        year = educational_factories.EducationalYearFactory()
        meg_program = educational_factories.EducationalInstitutionProgramFactory(name="marseille_en_grand")
        educational_institution = educational_factories.EducationalInstitutionFactory(
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(
                    program=meg_program,
                    timespan=db_utils.make_timerange(
                        start=datetime.datetime(2023, 9, 1), end=datetime.datetime(2024, 8, 31)
                    ),
                )
            ]
        )
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE.name,
        )
        booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            educationalInstitution=educational_institution,
            educationalYear=year,
        )
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking=booking,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
            amount=-538_55,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=pricing_line_category,
            amount=-538_55,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 1
        invoice_line = invoice_lines[0]
        assert len(invoice_line) == 3
        assert invoice_line["amount"] == -538_55
        assert invoice_line["product_id"] == product_id  # is not MEG (Marseille en grand)
        assert invoice_line["title"] == title

    def test_get_debit_note_line_collective(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        year = educational_factories.EducationalYearFactory()
        meg_program = educational_factories.EducationalInstitutionProgramFactory(name="marseille_en_grand")
        educational_institution = educational_factories.EducationalInstitutionFactory(
            programAssociations=[
                educational_factories.EducationalInstitutionProgramAssociationFactory(program=meg_program)
            ]
        )
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=year,
            ministry=educational_models.Ministry.EDUCATION_NATIONALE.name,
        )
        booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            educationalInstitution=educational_institution,
            educationalYear=year,
        )
        pricing = finance_factories.CollectivePricingFactory(
            collectiveBooking=booking,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
            amount=666_55,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=finance_models.PricingLineCategory.OFFERER_REVENUE,
            amount=666_55,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 1
        invoice_line = invoice_lines[0]
        assert len(invoice_line) == 3
        assert invoice_line["amount"] == 666_55
        assert invoice_line["product_id"] == "ORCOLMEG"
        assert invoice_line["title"] == "Réservations"

    def test_get_debit_note_line_indiv(self):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        booking = bookings_factories.UsedBookingFactory(
            user__deposit__type=finance_models.DepositType.GRANT_18, stock__offer__venue=venue
        )
        pricing = finance_factories.PricingFactory(
            booking=booking, pricingPoint=venue, status=finance_models.PricingStatus.PROCESSED, amount=55_66
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=finance_models.PricingLineCategory.OFFERER_REVENUE,
            amount=55_66,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account)

        backend = finance_backend.BaseFinanceBackend()
        invoice_lines = backend.get_invoice_lines(invoice)
        assert len(invoice_lines) == 1
        invoice_line = invoice_lines[0]
        assert len(invoice_line) == 3
        assert invoice_line["amount"] == 55_66
        assert invoice_line["product_id"] == "ORINDGRANT_18"
        assert invoice_line["title"] == "Réservations"


@pytest.mark.settings(
    CEGID_URL="",
    CEGID_USERNAME="",
    CEGID_PASSWORD="",
    CEGID_CLIENT_ID="",
    CEGID_CLIENT_SECRET="",
    FINANCE_BACKEND="pcapi.core.finance.backend.cegid.CegidFinanceBackend",
)
class CegidFinanceBackendTest:
    def test_get_backend(self, cegid_config):
        current_backend = finance_backend._get_backend()
        assert isinstance(current_backend, finance_backend.CegidFinanceBackend)

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_push_invoice(self, cegid_config, requests_mock):
        with time_machine.travel("2025-01-25", tick=False):
            now = datetime.datetime.utcnow()
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        booking1 = bookings_factories.UsedBookingFactory(
            user__deposit__type=finance_models.DepositType.GRANT_18,
            stock__offer__venue=venue,
        )
        pricing1 = finance_factories.PricingFactory(
            booking=booking1,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing1,
            category=finance_models.PricingLineCategory.OFFERER_REVENUE,
            amount=-1199_60,
        )
        booking_finance_incident = finance_factories.IndividualBookingFinanceCommercialGestureFactory(
            newTotalAmount=-23_20,
            booking__user=BeneficiaryFactory(deposit__type=finance_models.DepositType.GRANT_18),
            booking__stock__offer__venue=venue,
        )
        finance_event = finance_factories.FinanceEventFactory(
            bookingFinanceIncident=booking_finance_incident,
            booking=None,
            valueDate=datetime.datetime.utcnow(),
            pricingPoint=venue,
            venue=venue,
        )
        pricing2 = finance_factories.PricingFactory(
            booking=None,
            event=finance_event,
            pricingPoint=venue,
            venue=venue,
            valueDate=now,
            amount=-23_20,
            revenue=0,
            status=finance_models.PricingStatus.PROCESSED,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing2,
            category=finance_models.PricingLineCategory.COMMERCIAL_GESTURE,
            amount=-23_20,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing1, pricing2])
        invoice = finance_factories.InvoiceFactory(cashflows=[cashflow], bankAccount=bank_account, date=now)

        #########################################
        # Mock the response from Cegid XRP Flex #
        #########################################
        response_data = {
            "Amount": {"value": 1222.8},
            "ApprovedForPayment": {"value": False},
            "Balance": {"value": 1222.8},
            "BranchID": {"value": "PASSCULT"},
            "CashAccount": {},
            "CurrencyID": {"value": "EUR"},
            "Date": {"value": "2024-12-18T00:00:00+00:00"},
            "Description": {"value": f"{invoice.reference} - 15/01-31/01"},
            "Details": [
                {
                    "Account": {"value": "604000"},
                    "Amount": {"value": 1199.6},
                    "Branch": {"value": "PASSCULT"},
                    "CalculateDiscountsOnImport": {},
                    "Description": {"value": "Charges Pass Culture jeunes"},
                    "ExtendedCost": {"value": 1199.6},
                    "InventoryID": {"value": "ORIND18P000"},
                    "POLine": {},
                    "POOrderNbr": {},
                    "POOrderType": {},
                    "POReceiptLine": {},
                    "POReceiptNbr": {},
                    "POReceiptType": {},
                    "Qty": {"value": 1.0},
                    "ReferenceNbr": {"value": "000014"},
                    "Subaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
                    "TaxCategory": {"value": "SERV TN"},
                    "TransactionDescription": {"value": "Réservations"},
                    "UOM": {"value": "UNITE"},
                    "UnitCost": {"value": 1199.6},
                    "_links": {
                        "files:put": "/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.APInvoiceEntry/Transactions/8189c293-62bd-ef11-a82c-000d3ae74153/{filename}"
                    },
                    "custom": {},
                    "id": "8189c293-62bd-ef11-a82c-000d3ae74153",
                    "note": {"value": ""},
                    "rowNumber": 1,
                },
                {
                    "Account": {"value": "604300"},
                    "Amount": {"value": 23.2},
                    "Branch": {"value": "PASSCULT"},
                    "CalculateDiscountsOnImport": {},
                    "Description": {"value": "Geste commercial"},
                    "ExtendedCost": {"value": 23.2},
                    "InventoryID": {"value": "CGIND18P000"},
                    "POLine": {},
                    "POOrderNbr": {},
                    "POOrderType": {},
                    "POReceiptLine": {},
                    "POReceiptNbr": {},
                    "POReceiptType": {},
                    "Qty": {"value": 1.0},
                    "ReferenceNbr": {"value": "000014"},
                    "Subaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
                    "TaxCategory": {"value": "SERV TN"},
                    "TransactionDescription": {"value": "Gestes commerciaux"},
                    "UOM": {"value": "UNITE"},
                    "UnitCost": {"value": 23.2},
                    "_links": {
                        "files:put": "/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.APInvoiceEntry/Transactions/8689c293-62bd-ef11-a82c-000d3ae74153/{filename}"
                    },
                    "custom": {},
                    "id": "8689c293-62bd-ef11-a82c-000d3ae74153",
                    "note": {"value": ""},
                    "rowNumber": 2,
                },
            ],
            "DueDate": {"value": "2025-01-17T00:00:00+00:00"},
            "Hold": {"value": False},
            "IsTaxValid": {},
            "LastModifiedDateTime": {"value": "2024-12-18T17:07:45.433+00:00"},
            "LocationID": {"value": "PRINCIPAL"},
            "PostPeriod": {"value": f"{invoice.date:%m%Y}"},
            "ReferenceNbr": {"value": "000014"},
            "Status": {"value": "Balanced"},
            "TaxTotal": {"value": 0.0},
            "Terms": {"value": "30J"},
            "Type": {"value": "Bill"},
            "Vendor": {"value": "200178"},
            "VendorRef": {"value": "F240000095"},
            "_links": {
                "files:put": "/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.APInvoiceEntry/Document/7b89c293-62bd-ef11-a82c-000d3ae74153/{filename}",
                "self": "/passculture/entity/eCommerce/23.200.001/Bill/7b89c293-62bd-ef11-a82c-000d3ae74153",
            },
            "custom": {},
            "id": "7b89c293-62bd-ef11-a82c-000d3ae74153",
            "note": {"value": ""},
            "rowNumber": 1,
        }
        request_matcher = requests_mock.register_uri(
            "PUT",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Bill",
            json=response_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )
        with time_machine.travel("2025-01-25", tick=False):
            invoice_data = finance_backend.push_invoice(invoice.id)

        assert request_matcher.call_count == 1
        assert invoice_data == response_data
        request_json = request_matcher.request_history[0].json()
        assert request_json["Amount"] == {"value": "1222.80"}
        assert request_json["ApprovedForPayment"] == {"value": False}
        assert request_json["Balance"] == {"value": "1222.80"}
        assert request_json["BranchID"] == {"value": "PASSCULT"}
        assert request_json["CurrencyID"] == {"value": "EUR"}
        assert request_json["Date"] == {"value": now.strftime("%Y-%m-%dT%H:%M:%S+00:00")}
        assert request_json["Description"] == {"value": f"{invoice.reference} - 16/01-31/01"}
        assert "Details" in request_json
        details = request_json["Details"]
        assert len(details) == 2
        assert {v["Description"]["value"] for v in details} == {"Réservations", "Gestes commerciaux"}

        details1 = [e for e in details if e["Description"]["value"] == "Réservations"][0]
        assert details1["Amount"] == {"value": "1199.60"}
        assert details1["Branch"] == {"value": "PASSCULT"}
        assert details1["InventoryID"] == {"value": "ORIND18P0000"}
        assert details1["TransactionDescription"] == {"value": "Réservations"}
        assert details1["Description"] == {"value": "Réservations"}
        assert details1["Qty"] == {"value": 1}
        assert details1["UnitCost"] == {"value": "1199.60"}
        assert details1["UOM"] == {"value": "UNITE"}

        details2 = [e for e in details if e["Description"]["value"] == "Gestes commerciaux"][0]
        assert details2["Amount"] == {"value": "23.20"}
        assert details2["Branch"] == {"value": "PASSCULT"}
        assert details2["InventoryID"] == {"value": "CGIND18P0000"}
        assert details2["TransactionDescription"] == {"value": "Gestes commerciaux"}
        assert details2["Description"] == {"value": "Gestes commerciaux"}
        assert details2["Qty"] == {"value": 1}
        assert details2["UnitCost"] == {"value": "23.20"}
        assert details2["UOM"] == {"value": "UNITE"}

        assert request_json["Hold"] == {"value": False}
        assert request_json["LocationID"] == {"value": "PRINCIPAL"}
        assert request_json["PostPeriod"] == {"value": f"{invoice.date:%m%Y}"}
        assert request_json["Status"] == {"value": "Open"}
        assert request_json["TaxTotal"] == {"value": "0"}
        assert request_json["Terms"] == {"value": "30J"}
        assert request_json["Type"] == {"value": "INV"}
        assert request_json["Vendor"] == {"value": str(bank_account.id)}
        assert request_json["VendorRef"] == {"value": invoice.reference}

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_get_invoice(self, requests_mock, cegid_config):
        response_data = [
            {
                "Amount": {"value": 1222.8},
                "ApprovedForPayment": {"value": False},
                "Balance": {"value": 1222.8},
                "BranchID": {"value": "PASSCULT"},
                "CashAccount": {},
                "CurrencyID": {"value": "EUR"},
                "Date": {"value": "2024-12-18T00:00:00+00:00"},
                "Description": {"value": "Justificatif de remboursement"},
                "Details": [],
                "DueDate": {"value": "2025-01-17T00:00:00+00:00"},
                "Hold": {"value": False},
                "IsTaxValid": {},
                "LastModifiedDateTime": {"value": "2024-12-18T17:07:45.433+00:00"},
                "LocationID": {"value": "PRINCIPAL"},
                "PostPeriod": {"value": "122019"},
                "ReferenceNbr": {"value": "000014"},
                "Status": {"value": "Balanced"},
                "TaxTotal": {"value": 0.0},
                "Terms": {"value": "30J"},
                "Type": {"value": "Bill"},
                "Vendor": {"value": "200178"},  # BankAccount.id
                "VendorRef": {"value": "F240000095"},  # Invoice.reference
                "_links": {
                    "files:put": "/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.APInvoiceEntry/Document/7b89c293-62bd-ef11-a82c-000d3ae74153/{filename}",
                    "self": "/passculture/entity/eCommerce/23.200.001/Bill/7b89c293-62bd-ef11-a82c-000d3ae74153",
                },
                "custom": {},
                "id": "7b89c293-62bd-ef11-a82c-000d3ae74153",
                "note": {"value": ""},
                "rowNumber": 1,
            }
        ]
        request_matcher = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Bill",
            json=response_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )

        invoice_data = finance_backend.get_invoice("F240000095")
        assert request_matcher.call_count == 1
        assert invoice_data == response_data[0]

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_push_debit_note(self, cegid_config, requests_mock):
        test_date = "2025-01-25"
        with time_machine.travel(test_date, tick=False):
            now = datetime.datetime.utcnow()
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point="self",
            bank_account=bank_account,
        )
        booking = bookings_factories.UsedBookingFactory(
            user__deposit__type=finance_models.DepositType.GRANT_18,
            stock__offer__venue=venue,
        )
        pricing = finance_factories.PricingFactory(
            booking=booking,
            pricingPoint=venue,
            status=finance_models.PricingStatus.PROCESSED,
        )
        finance_factories.PricingLineFactory(
            pricing=pricing,
            category=finance_models.PricingLineCategory.OFFERER_REVENUE,
            amount=99_60,
        )
        cashflow = finance_factories.CashflowFactory(pricings=[pricing])
        invoice = finance_factories.InvoiceFactory(
            cashflows=[cashflow], bankAccount=bank_account, date=now, reference="A250000014"
        )

        #########################################
        # Mock the response from Cegid XRP Flex #
        #########################################
        response_data = {
            "Amount": {"value": 99.6},
            "ApprovedForPayment": {"value": False},
            "Balance": {"value": 99.6},
            "BranchID": {"value": "PASSCULT"},
            "CashAccount": {},
            "CurrencyID": {"value": "EUR"},
            "Date": {"value": "2024-12-18T00:00:00+00:00"},
            "Description": {"value": f"{invoice.reference} - 15/01-31/01"},
            "Details": [
                {
                    "Account": {"value": "604000"},
                    "Amount": {"value": 99.6},
                    "Branch": {"value": "PASSCULT"},
                    "CalculateDiscountsOnImport": {},
                    "Description": {"value": "Charges Pass Culture jeunes"},
                    "ExtendedCost": {"value": 99.6},
                    "InventoryID": {"value": "ORIND18P000"},
                    "POLine": {},
                    "POOrderNbr": {},
                    "POOrderType": {},
                    "POReceiptLine": {},
                    "POReceiptNbr": {},
                    "POReceiptType": {},
                    "Qty": {"value": 1.0},
                    "ReferenceNbr": {"value": "000014"},
                    "Subaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
                    "TaxCategory": {"value": "SERV TN"},
                    "TransactionDescription": {"value": "Réservations"},
                    "UOM": {"value": "UNITE"},
                    "UnitCost": {"value": 99.6},
                    "_links": {
                        "files:put": "/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.APInvoiceEntry/Transactions/8189c293-62bd-ef11-a82c-000d3ae74153/{filename}"
                    },
                    "custom": {},
                    "id": "8189c293-62bd-ef11-a82c-000d3ae74153",
                    "note": {"value": ""},
                    "rowNumber": 1,
                },
            ],
            "DueDate": {"value": "2025-01-17T00:00:00+00:00"},
            "Hold": {"value": False},
            "IsTaxValid": {},
            "LastModifiedDateTime": {"value": "2024-12-18T17:07:45.433+00:00"},
            "LocationID": {"value": "PRINCIPAL"},
            "PostPeriod": {"value": f"{invoice.date:%m%Y}"},
            "ReferenceNbr": {"value": "000014"},
            "Status": {"value": "Balanced"},
            "TaxTotal": {"value": 0.0},
            "Terms": {"value": "30J"},
            "Type": {"value": "Debit Adj."},
            "Vendor": {"value": "200178"},
            "VendorRef": {"value": "A250000014"},
            "_links": {
                "files:put": "/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.APInvoiceEntry/Document/7b89c293-62bd-ef11-a82c-000d3ae74153/{filename}",
                "self": "/passculture/entity/eCommerce/23.200.001/Bill/7b89c293-62bd-ef11-a82c-000d3ae74153",
            },
            "custom": {},
            "id": "7b89c293-62bd-ef11-a82c-000d3ae74153",
            "note": {"value": ""},
            "rowNumber": 1,
        }
        request_matcher = requests_mock.register_uri(
            "PUT",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Bill",
            json=response_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )
        with time_machine.travel(test_date, tick=False):
            invoice_data = finance_backend.push_invoice(invoice.id)

        assert request_matcher.call_count == 1
        assert invoice_data == response_data
        request_json = request_matcher.request_history[0].json()
        assert request_json["Amount"] == {"value": "99.60"}
        assert request_json["ApprovedForPayment"] == {"value": False}
        assert request_json["Balance"] == {"value": "99.60"}
        assert request_json["BranchID"] == {"value": "PASSCULT"}
        assert request_json["CurrencyID"] == {"value": "EUR"}
        assert request_json["Date"] == {"value": now.strftime("%Y-%m-%dT%H:%M:%S+00:00")}
        assert request_json["Description"] == {"value": f"{invoice.reference} - 16/01-31/01"}
        assert "Details" in request_json
        details = request_json["Details"]
        assert len(details) == 1

        details_line = [e for e in details if e["Description"]["value"] == "Réservations"][0]
        assert details_line["Amount"] == {"value": "99.60"}
        assert details_line["Branch"] == {"value": "PASSCULT"}
        assert details_line["InventoryID"] == {"value": "ORIND18P0000"}
        assert details_line["TransactionDescription"] == {"value": "Réservations"}
        assert details_line["Description"] == {"value": "Réservations"}
        assert details_line["Qty"] == {"value": 1}
        assert details_line["UnitCost"] == {"value": "99.60"}
        assert details_line["UOM"] == {"value": "UNITE"}
        assert details_line["Description"] == {"value": "Réservations"}

        assert request_json["Hold"] == {"value": False}
        assert request_json["LocationID"] == {"value": "PRINCIPAL"}
        assert request_json["PostPeriod"] == {"value": f"{invoice.date:%m%Y}"}
        assert request_json["Status"] == {"value": "Open"}
        assert request_json["TaxTotal"] == {"value": "0"}
        assert request_json["Terms"] == {"value": "30J"}
        assert request_json["Type"] == {"value": "ADR"}
        assert request_json["Vendor"] == {"value": str(bank_account.id)}
        assert request_json["VendorRef"] == {"value": invoice.reference}

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_get_invoice_not_found(self, requests_mock, cegid_config):
        request_matcher = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Bill",
            json=[],
            status_code=200,
            headers={"content-type": "application/json"},
        )
        with pytest.raises(finance_exceptions.FinanceBackendInvoiceNotFound):
            finance_backend.get_invoice("F0001")

        assert request_matcher.call_count == 1

    def test_cache_token(self, app, requests_mock, cegid_config, cegid_auth_token):
        redis = app.redis_client
        cache_key = "cache:cegid:token"
        token = redis.get(cache_key)

        assert token is None

        request_matcher_auth = requests_mock.register_uri(
            "POST",
            f"{cegid_config.CEGID_URL}/identity/connect/token",
            json=cegid_auth_token,
            status_code=200,
        )

        request_matcher_get_bank_account = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Vendor/5",
            json={},
            status_code=200,
            headers={"content-type": "application/json"},
        )

        backend = finance_backend.CegidFinanceBackend()
        backend.get_bank_account(5)
        assert request_matcher_auth.call_count == 1
        assert request_matcher_get_bank_account.call_count == 1
        token = redis.get(cache_key)
        assert token == cegid_auth_token["access_token"]

        backend.get_bank_account(5)
        assert request_matcher_auth.call_count == 1
        assert request_matcher_get_bank_account.call_count == 2

    def test_refresh_token(self, app, requests_mock, cegid_config, cegid_auth_token, mock_cegid_auth):
        redis = app.redis_client
        cache_key = "cache:cegid:token"
        backend = finance_backend.CegidFinanceBackend()
        url = f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Vendor/5"

        request_matcher_get_bank_account = requests_mock.register_uri(
            "GET",
            url,
            json={},
            status_code=200,
            headers={"content-type": "application/json"},
        )

        backend.get_bank_account(5)
        token = redis.get(cache_key)
        assert token == cegid_auth_token["access_token"]
        assert request_matcher_get_bank_account.call_count == 1

        requests_mock.reset()
        response_error = requests_mock.register_uri(
            "GET",
            url,
            response_list=[
                {"text": "", "status_code": 401},
                {"json": [], "status_code": 200},
            ],
        )
        backend.get_bank_account(5)
        assert mock_cegid_auth.call_count == 1
        assert response_error.call_count == 2

    def test_unauthorized_request(self, requests_mock, cegid_config, mock_cegid_auth):
        url = f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Vendor/5"
        requests_mock.reset()
        request_matcher = requests_mock.register_uri("GET", url, text="", status_code=401)
        backend = finance_backend.CegidFinanceBackend()
        with pytest.raises(finance_exceptions.FinanceBackendUnauthorized):
            backend.get_bank_account(5)

        assert request_matcher.call_count == 2
        assert mock_cegid_auth.call_count == 2

    def test_push_bank_account(self, cegid_config, requests_mock, mock_cegid_auth, faker):
        offerer = offerers_factories.OffererFactory(name="Structure avec de nombreux remboursements", siren="000009837")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        vendor_uuid = str(faker.uuid4())
        main_contact_uuid = str(faker.uuid4())
        iban_uuid = str(faker.uuid4())
        bic_uuid = str(faker.uuid4())

        iso_now = f"{datetime.datetime.utcnow().isoformat()}+00"

        response_data = {
            "APAccount": {"value": "467500"},
            "APSubaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
            "AccountRef": {},
            "CashAccount": {"value": "CD512000"},
            "CreatedDateTime": {"value": iso_now},
            "CurrencyID": {"value": "EUR"},
            "CurrencyRateType": {},
            "EnableCurrencyOverride": {"value": False},
            "EnableRateOverride": {"value": False},
            "FOBPoint": {},
            "LastModifiedDateTime": {"value": iso_now},
            "LeadTimedays": {},
            "LegalName": {"value": offerer.name},
            "LocationName": {"value": "Emplacement principal"},
            "MainContact": {
                "Address": None,
                "custom": {},
                "id": main_contact_uuid,
                "note": None,
                "rowNumber": 1,
            },
            "MaxReceipt": {"value": 100.0},
            "MinReceipt": {"value": 0.0},
            "NumTVAIntracom": {},
            "ParentAccount": {},
            "PaySeparately": {"value": False},
            "PaymentBy": {"value": "Due Date"},
            "PaymentInstructions": [
                {
                    "Description": {"value": "IBAN"},
                    "LocationID": {"value": 81724},
                    "PaymentInstructionsID": {"value": "IBAN"},
                    "PaymentMethod": {"value": "VSEPA"},
                    "Value": {"value": bank_account.iban},
                    "custom": {},
                    "id": iban_uuid,
                    "note": None,
                    "rowNumber": 1,
                },
                {
                    "Description": {"value": "BIC"},
                    "LocationID": {"value": 81724},
                    "PaymentInstructionsID": {"value": "BIC"},
                    "PaymentMethod": {"value": "VSEPA"},
                    "Value": {},
                    "custom": {},
                    "id": bic_uuid,
                    "note": None,
                    "rowNumber": 2,
                },
            ],
            "PaymentLeadTimedays": {"value": 0},
            "PaymentMethod": {"value": "VSEPA"},
            "PrintOrders": {"value": False},
            "ReceiptAction": {"value": "Accept but Warn"},
            "ReceivingBranch": {},
            "RemittanceAddressOverride": {"value": False},
            "RemittanceContactOverride": {"value": False},
            "SendOrdersbyEmail": {"value": False},
            "ShipVia": {},
            "ShippingAddressOverride": {"value": False},
            "ShippingContactOverride": {"value": False},
            "ShippingTerms": {},
            "Siret": {"value": "000009837"},
            "Status": {"value": "Active"},
            "TaxCalculationMode": {"value": "Net"},
            "TaxRegistrationID": {},
            "TaxZone": {"value": "EXO"},
            "Terms": {"value": "30J"},
            "ThresholdReceipt": {"value": 100.0},
            "VendorClass": {"value": "ACTEURCULT"},
            "VendorID": {"value": str(bank_account.id)},
            "VendorIsLaborUnion": {"value": False},
            "VendorIsTaxAgency": {"value": False},
            "VendorName": {"value": bank_account.label},
            "Zonedetaxes": {"value": "EXO"},
            "_links": {
                "files:put": f"/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.VendorMaint/BAccount/{vendor_uuid}/{{filename}}",
                "self": f"/passculture/entity/eCommerce/23.200.001/Vendor/{vendor_uuid}",
            },
            "custom": {},
            "id": vendor_uuid,
            "note": {"value": ""},
            "rowNumber": 1,
        }

        request_matcher_create_vendor = requests_mock.register_uri(
            "PUT",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Vendor",
            json=response_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )

        finance_backend.push_bank_account(bank_account.id)

        assert request_matcher_create_vendor.call_count == 1
        request_json = request_matcher_create_vendor.request_history[0].json()
        assert request_json["CashAccount"] == {"value": "CD512000"}
        assert request_json["CurrencyID"] == {"value": "EUR"}
        assert request_json["LegalName"] == {"value": "Structure avec de nombreux remboursements"}
        assert request_json["MainContact"] == {
            "Address": {
                "AddressID": {"value": "PRINCIPAL"},
                "AddressLine1": {"value": offerer.street},
                "City": {"value": offerer.city},
                "Country": {"value": "FR"},
                "PostalCode": {"value": offerer.postalCode},
                "State": {"value": offerer.departementCode},
            }
        }
        assert request_json["NatureEco"] == {"value": "Exempt operations"}
        assert request_json["PaymentMethod"] == {"value": "VSEPA"}
        assert request_json["Status"] == {"value": "Active"}
        assert request_json["TaxZone"] == {"value": "EXO"}
        assert request_json["Terms"] == {"value": "30J"}
        assert request_json["VendorClass"] == {"value": "ACTEURCULT"}
        assert request_json["VendorID"] == {"value": str(bank_account.id)}
        assert request_json["VendorName"] == {"value": bank_account.label}

    def test_authenticate(self, mock_cegid_auth):
        backend = finance_backend.CegidFinanceBackend()
        backend._authenticate()
        assert mock_cegid_auth.call_count == 1

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_get_bank_account(self, requests_mock, cegid_config, faker):
        offerer = offerers_factories.OffererFactory(name="Structure avec de nombreux remboursements", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        main_contact_uuid = str(faker.uuid4())
        vendor_uuid = str(faker.uuid4())
        iban_uuid = str(faker.uuid4())
        bic_uuid = str(faker.uuid4())
        iso_now = f"{datetime.datetime.utcnow().isoformat()}+00"

        response_vendor_data = {
            "APAccount": {"value": "467500"},
            "APSubaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
            "AccountRef": {},
            "Attributes": [],
            "CashAccount": {"value": "CD512000"},
            "CreatedDateTime": {"value": iso_now},
            "CurrencyID": {"value": "EUR"},
            "CurrencyRateType": {},
            "EnableCurrencyOverride": {"value": False},
            "EnableRateOverride": {"value": False},
            "FOBPoint": {},
            "LastModifiedDateTime": {"value": iso_now},
            "LeadTimedays": {},
            "LegalName": {"value": "Structure avec de nombreux remboursements"},
            "LocationName": {"value": "Emplacement principal"},
            "MainContact": {
                "Address": None,
                "custom": {},
                "id": main_contact_uuid,
                "note": None,
                "rowNumber": 1,
            },
            "MaxReceipt": {"value": 100.0},
            "MinReceipt": {"value": 0.0},
            "NumTVAIntracom": {},
            "ParentAccount": {},
            "PaySeparately": {"value": False},
            "PaymentBy": {"value": "Due Date"},
            "PaymentInstructions": [
                {
                    "Description": {"value": "IBAN"},
                    "LocationID": {"value": 81724},
                    "PaymentInstructionsID": {"value": "IBAN"},
                    "PaymentMethod": {"value": "VSEPA"},
                    "Value": {"value": bank_account.iban},
                    "custom": {},
                    "id": iban_uuid,
                    "note": None,
                    "rowNumber": 1,
                },
                {
                    "Description": {"value": "BIC"},
                    "LocationID": {"value": 81724},
                    "PaymentInstructionsID": {"value": "BIC"},
                    "PaymentMethod": {"value": "VSEPA"},
                    "Value": {},
                    "custom": {},
                    "id": bic_uuid,
                    "note": None,
                    "rowNumber": 2,
                },
            ],
            "PaymentLeadTimedays": {"value": 0},
            "PaymentMethod": {"value": "VSEPA"},
            "PrimaryContact": None,
            "PrintOrders": {"value": False},
            "ReceiptAction": {"value": "Accept but Warn"},
            "ReceivingBranch": {},
            "RemittanceAddressOverride": {"value": False},
            "RemittanceContactOverride": {"value": False},
            "SendOrdersbyEmail": {"value": False},
            "ShipVia": {},
            "ShippingAddressOverride": {"value": False},
            "ShippingContactOverride": {"value": False},
            "ShippingTerms": {},
            "Siret": {"value": "000009837"},
            "Status": {"value": "Active"},
            "TaxCalculationMode": {"value": "Net"},
            "TaxRegistrationID": {},
            "TaxZone": {"value": "EXO"},
            "Terms": {"value": "30J"},
            "ThresholdReceipt": {"value": 100.0},
            "VendorClass": {"value": "ACTEURCULT"},
            "VendorID": {"value": str(bank_account.id)},
            "VendorIsLaborUnion": {"value": False},
            "VendorIsTaxAgency": {"value": False},
            "VendorName": {"value": "Compte bancaire avec plein de remboursements #1746462948"},
            "Zonedetaxes": {"value": "EXO"},
            "_links": {
                "files:put": f"/passculture/entity/eCommerce/23.200.001/files/PX.Objects.AP.VendorMaint/BAccount/{vendor_uuid}/{{filename}}",
                "self": f"/passculture/entity/eCommerce/23.200.001/Vendor/{vendor_uuid}",
            },
            "custom": {},
            "id": vendor_uuid,
            "note": {"value": ""},
            "rowNumber": 1,
        }

        request_matcher_get_vendor = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Vendor/{bank_account.id}",
            json=response_vendor_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )

        finance_backend.get_bank_account(bank_account.id)
        assert request_matcher_get_vendor.call_count == 1

    def test_bank_account_not_found(self, cegid_config, mock_cegid_auth, requests_mock):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        response_not_found_data = {
            "exceptionMessage": "No entity satisfies the condition.",
            "exceptionType": "PX.Api.ContractBased.NoEntitySatisfiesTheConditionException",
            "message": "An error has occurred.",
            "stackTrace": "…",
        }
        request_matcher_get_vendor = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/eCommerce/23.200.001/Vendor/{bank_account.id}",
            json=response_not_found_data,
            status_code=500,
            headers={"content-type": "application/json"},
        )
        with pytest.raises(finance_exceptions.FinanceBackendBankAccountNotFound):
            finance_backend.get_bank_account(bank_account.id)

        assert request_matcher_get_vendor.call_count == 1

    def test_is_not_configured(self):
        backend = finance_backend.CegidFinanceBackend()
        assert not backend.is_configured

        with pytest.raises(finance_exceptions.FinanceBackendNotConfigured) as exc:
            finance_backend._get_backend()
        assert exc.value.args[0] == "Finance backend `CegidFinanceBackend` not correctly configured"

    @pytest.mark.usefixtures("cegid_config")
    def test_is_configured(self):
        backend = finance_backend.CegidFinanceBackend()
        assert backend.is_configured
