import datetime
import json
from typing import NamedTuple
import uuid

import pytest

from pcapi.core.finance import backend as finance_backend
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance.backend.dummy import bank_accounts as dummy_bank_accounts
from pcapi.core.finance.backend.dummy import invoices as dummy_invoices
from pcapi.core.offerers import factories as offerers_factories


pytestmark = [
    pytest.mark.usefixtures("db_session", "clean_dummy_backend_data"),
]


@pytest.fixture
def cegid_cookies(faker, cegid_config):
    return {
        ".ASPXAUTH": faker.binary(180).hex().upper(),
        "ASP.NET_SessionId": faker.binary(12).hex(),
        "CompanyID": cegid_config.CEGID_COMPANY,
        "Locale": "Culture=fr-FR&TimeZone=GMTE0000U",
        "UserBranch": "1",
        "requestid": faker.binary(16).hex().upper(),
    }


@pytest.fixture
def cegid_config(faker, settings):
    class Config(NamedTuple):
        CEGID_URL: str = faker.uri()
        CEGID_USERNAME: str = faker.user_name()
        CEGID_PASSWORD: str = faker.password()
        CEGID_COMPANY: str = "passculture"

    config = Config()
    settings.CEGID_URL = config.CEGID_URL
    settings.CEGID_USERNAME = config.CEGID_USERNAME
    settings.CEGID_PASSWORD = config.CEGID_PASSWORD
    settings.CEGID_COMPANY = config.CEGID_COMPANY
    yield config


@pytest.fixture
def mock_cegid_auth(cegid_config, requests_mock, cegid_cookies):
    yield requests_mock.register_uri(
        "POST",
        f"{cegid_config.CEGID_URL}/entity/auth/login",
        cookies=cegid_cookies,
        text="",
        status_code=204,
    )


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


@pytest.mark.settings(
    CEGID_URL="",
    CEGID_USERNAME="",
    CEGID_PASSWORD="",
    CEGID_COMPANY="",
    FINANCE_BACKEND="pcapi.core.finance.backend.cegid.CegidFinanceBackend",
)
class CegidFinanceBackendTest:
    def test_get_backend(self, cegid_config):
        current_backend = finance_backend._get_backend()
        assert isinstance(current_backend, finance_backend.CegidFinanceBackend)

    def test_push_invoice(self):
        # TODO
        pass

    def test_cache_cookies(self, app, requests_mock, cegid_config, cegid_cookies):
        redis = app.redis_client
        cache_key = "cache:cegid:cookies"
        cookies = redis.get(cache_key)

        assert cookies is None

        request_matcher_auth = requests_mock.register_uri(
            "POST",
            f"{cegid_config.CEGID_URL}/entity/auth/login",
            text="",
            cookies=cegid_cookies,
            status_code=204,
        )

        request_matcher_get_vendor_location = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB&$filter=VendorID%20eq%20'1'",
            json=[],
            status_code=200,
            headers={"content-type": "application/json"},
        )

        backend = finance_backend.CegidFinanceBackend()
        vendor_location = backend._get_vendor_location(1)
        assert vendor_location == {}
        assert request_matcher_auth.call_count == 1
        assert request_matcher_get_vendor_location.call_count == 1
        cookies = redis.get(cache_key)
        assert cookies is not None
        assert json.loads(cookies) == cegid_cookies

        vendor_location = backend._get_vendor_location(1)
        assert vendor_location == {}
        assert request_matcher_auth.call_count == 1
        assert request_matcher_get_vendor_location.call_count == 2

    def test_refresh_cookies(self, app, requests_mock, cegid_config, cegid_cookies, mock_cegid_auth):
        redis = app.redis_client
        cache_key = "cache:cegid:cookies"
        backend = finance_backend.CegidFinanceBackend()
        url = f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB&$filter=VendorID%20eq%20'1'"

        request_matcher_get_vendor_location = requests_mock.register_uri(
            "GET",
            url,
            json=[],
            status_code=200,
            headers={"content-type": "application/json"},
        )
        vendor_location = backend._get_vendor_location(1)
        assert vendor_location == {}
        cookies = redis.get(cache_key)
        assert json.loads(cookies) == cegid_cookies
        assert request_matcher_get_vendor_location.call_count == 1
        requests_mock.reset()
        response_error = requests_mock.register_uri(
            "GET",
            url,
            response_list=[
                {"text": "", "status_code": 401},
                {"json": [], "status_code": 200},
            ],
        )

        vendor_location = backend._get_vendor_location(1)
        assert vendor_location == {}
        assert mock_cegid_auth.call_count == 1
        assert response_error.call_count == 2

    def test_unauthorized_request(self, requests_mock, cegid_config, mock_cegid_auth):
        url = f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB&$filter=VendorID%20eq%20'1'"
        requests_mock.reset()
        request_matcher = requests_mock.register_uri("GET", url, text="", status_code=401)
        backend = finance_backend.CegidFinanceBackend()
        with pytest.raises(finance_exceptions.FinanceBackendUnauthorized):
            backend._get_vendor_location(1)

        assert request_matcher.call_count == 2
        assert mock_cegid_auth.call_count == 2

    def test_push_bank_account(self, cegid_config, requests_mock, mock_cegid_auth):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        vendor_uuid = str(uuid.uuid4())
        vendor_location_uuid = str(uuid.uuid4())
        main_contact_uuid = str(uuid.uuid4())

        iso_now = f"{datetime.datetime.utcnow().isoformat()}+00"

        response_data = {
            "APAccount": {"value": "401000"},
            "APSubaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
            "AccountRef": {},
            "CashAccount": {},
            "CreatedDateTime": {"value": iso_now},
            "CurrencyID": {"value": "EUR"},
            "CurrencyRateType": {},
            "EnableCurrencyOverride": {"value": False},
            "EnableRateOverride": {"value": False},
            "FOBPoint": {},
            "LastModifiedDateTime": {"value": iso_now},
            "LeadTimedays": {},
            "LegalName": {"value": offerer.name},
            "LocationName": {"value": "Primary Location"},
            "MainContact": {
                "Address": None,
                "custom": {},
                "id": main_contact_uuid,
                "note": None,
                "rowNumber": 1,
            },
            "MaxReceipt": {"value": 100.0},
            "MinReceipt": {"value": 0.0},
            "ParentAccount": {},
            "PaySeparately": {"value": False},
            "PaymentBy": {"value": "Due Date"},
            "PaymentLeadTimedays": {"value": 0},
            "PaymentMethod": {"value": "VSEPA"},
            "PrimaryContact": None,
            "PrintOrders": {"value": True},
            "ReceiptAction": {"value": "Accept but Warn"},
            "ReceivingBranch": {},
            "RemittanceAddressOverride": {"value": False},
            "RemittanceContactOverride": {"value": False},
            "SendOrdersbyEmail": {"value": True},
            "ShipVia": {},
            "ShippingAddressOverride": {"value": False},
            "ShippingContactOverride": {"value": False},
            "ShippingTerms": {},
            "Status": {"value": "Active"},
            "TaxCalculationMode": {"value": "Net"},
            "TaxRegistrationID": {},
            "TaxZone": {},
            "Terms": {"value": "30J"},
            "ThresholdReceipt": {"value": 100.0},
            "VendorClass": {"value": "STANDARD"},
            "VendorID": {"value": str(bank_account.id)},
            "VendorIsLaborUnion": {"value": False},
            "VendorIsTaxAgency": {"value": False},
            "VendorName": {"value": offerer.name},
            "_links": {
                "files:put": f"/passculture/entity/INTERFACES/23.200.001/files/PX.Objects.AP.VendorMaint/BAccount/{vendor_uuid}/{{filename}}",
                "self": f"/passculture/entity/INTERFACES/23.200.001/Vendor/{vendor_uuid}",
            },
            "custom": {},
            "id": vendor_uuid,
            "note": {"value": ""},
            "rowNumber": 1,
        }

        request_matcher_create_vendor = requests_mock.register_uri(
            "PUT",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/Vendor",
            json=response_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )

        request_matcher_get_vendor_location = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB&$filter=VendorID%20eq%20'{bank_account.id}'",
            json=[],
            status_code=200,
            headers={"content-type": "application/json"},
        )

        create_vendor_location_response_data = {
            "LocationID": {"value": "MAIN"},
            "RIB": [],
            "Status": {"value": "Active"},
            "VendorID": {"value": str(bank_account.id)},
            "_links": {
                "files:put": f"/passculture/entity/INTERFACES/23.200.001/files/PX.Objects.AP.VendorLocationMaint/Location/{vendor_location_uuid}/{{filename}}",
                "self": f"/passculture/entity/INTERFACES/23.200.001/VendorLocation/{vendor_location_uuid}",
            },
            "custom": {},
            "id": vendor_location_uuid,
            "note": None,
            "rowNumber": 1,
        }

        request_matcher_create_vendor_location = requests_mock.register_uri(
            "PUT",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB",
            json=create_vendor_location_response_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )

        finance_backend.push_bank_account(bank_account.id)

        assert request_matcher_create_vendor.call_count == 1
        assert request_matcher_get_vendor_location.call_count == 1
        assert request_matcher_create_vendor_location.call_count == 1

    def test_authenticate(self, mock_cegid_auth):
        backend = finance_backend.CegidFinanceBackend()
        backend._authenticate()
        assert mock_cegid_auth.call_count == 1

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_get_empty_vendor_location(self, requests_mock, cegid_config):
        backend = finance_backend.CegidFinanceBackend()
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        request_matcher_get_vendor_location = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB&$filter=VendorID%20eq%20'{bank_account.id}'",
            json=[],
            status_code=200,
            headers={"content-type": "application/json"},
        )
        vendor_list = backend._get_vendor_location(bank_account.id)
        assert vendor_list == {}
        assert request_matcher_get_vendor_location.call_count == 1

    def test_get_invoice(self):
        # TODO
        pass

    @pytest.mark.usefixtures("mock_cegid_auth")
    def test_get_bank_account(self, requests_mock, cegid_config):
        offerer = offerers_factories.OffererFactory(name="Association de coiffeurs", siren="853318459")
        bank_account = finance_factories.BankAccountFactory(offerer=offerer)
        vendor_uuid = str(uuid.uuid4())
        iban_uuid = str(uuid.uuid4())
        bic_uuid = str(uuid.uuid4())
        iso_now = f"{datetime.datetime.utcnow().isoformat()}+00"

        response_vendor_location_data = [
            {
                "LocationID": {"value": "MAIN"},
                "RIB": [
                    {
                        "Code": {"value": "IBAN"},
                        "PaymentMethod": {"value": "VSEPA"},
                        "Valeur": {"value": bank_account.iban},
                        "custom": {},
                        "id": iban_uuid,
                        "note": None,
                        "rowNumber": 1,
                    },
                    {
                        "Code": {"value": "BIC"},
                        "PaymentMethod": {"value": "VSEPA"},
                        "Valeur": {"value": "BDFEFRPP"},
                        "custom": {},
                        "id": bic_uuid,
                        "note": None,
                        "rowNumber": 2,
                    },
                ],
                "Status": {"value": "Active"},
                "VendorID": {"value": str(bank_account.id)},
                "_links": {
                    "files:put": f"/passculture/entity/INTERFACES/23.200.001/files/PX.Objects.AP.VendorLocationMaint/Location/{vendor_uuid}/{{filename}}",
                    "self": f"/passculture/entity/INTERFACES/23.200.001/VendorLocation/{vendor_uuid}",
                },
                "custom": {},
                "id": vendor_uuid,
                "note": {"value": ""},
                "rowNumber": 1,
            }
        ]

        response_vendor_data = {
            "APAccount": {"value": "401000"},
            "APSubaccount": {"value": "ZZZZZZZZZZZZZZZZZ"},
            "AccountRef": {},
            "Attributes": [],
            "CashAccount": {},
            "CreatedDateTime": {"value": iso_now},
            "CurrencyID": {"value": "EUR"},
            "CurrencyRateType": {},
            "EnableCurrencyOverride": {"value": False},
            "EnableRateOverride": {"value": False},
            "FOBPoint": {},
            "LastModifiedDateTime": {"value": iso_now},
            "LeadTimedays": {},
            "LegalName": {"value": offerer.name},
            "LocationName": {"value": "Primary Location"},
            "MaxReceipt": {"value": 100.0},
            "MinReceipt": {"value": 0.0},
            "ParentAccount": {},
            "PaySeparately": {"value": False},
            "PaymentBy": {"value": "Due Date"},
            "PaymentLeadTimedays": {"value": 0},
            "PaymentMethod": {"value": "VSEPA"},
            "PrintOrders": {"value": True},
            "ReceiptAction": {"value": "Accept but Warn"},
            "ReceivingBranch": {},
            "RemittanceAddressOverride": {"value": False},
            "RemittanceContactOverride": {"value": False},
            "SendOrdersbyEmail": {"value": True},
            "ShipVia": {},
            "ShippingAddressOverride": {"value": False},
            "ShippingContactOverride": {"value": False},
            "ShippingTerms": {},
            "Status": {"value": "Active"},
            "TaxCalculationMode": {"value": "Net"},
            "TaxRegistrationID": {},
            "TaxZone": {},
            "Terms": {"value": "30J"},
            "ThresholdReceipt": {"value": 100.0},
            "VendorClass": {"value": "STANDARD"},
            "VendorID": {"value": str(bank_account.id)},
            "VendorIsLaborUnion": {"value": False},
            "VendorIsTaxAgency": {"value": False},
            "VendorLocations": response_vendor_location_data,
            "VendorName": {"value": offerer.name},
            "_links": {
                "files:put": f"/passculture/entity/INTERFACES/23.200.001/files/PX.Objects.AP.VendorMaint/BAccount/{vendor_uuid}/{{filename}}",
                "self": f"/passculture/entity/INTERFACES/23.200.001/Vendor/{vendor_uuid}",
            },
            "custom": {},
            "id": vendor_uuid,
            "note": {"value": ""},
            "rowNumber": 1,
        }

        request_matcher_get_vendor_location = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/VendorLocation?$expand=RIB&$filter=VendorID%20eq%20'{bank_account.id}'",
            json=response_vendor_location_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )
        request_matcher_get_vendor = requests_mock.register_uri(
            "GET",
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/Vendor/{bank_account.id}",
            json=response_vendor_data,
            status_code=200,
            headers={"content-type": "application/json"},
        )

        finance_backend.get_bank_account(bank_account.id)
        assert request_matcher_get_vendor.call_count == 1
        assert request_matcher_get_vendor_location.call_count == 1

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
            f"{cegid_config.CEGID_URL}/entity/INTERFACES/23.200.001/Vendor/{bank_account.id}",
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
