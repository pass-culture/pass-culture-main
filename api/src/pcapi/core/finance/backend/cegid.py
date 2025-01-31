import datetime
import json
import logging
import typing

from pcapi import settings
from pcapi.core.finance import exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.finance.backend.base import BaseFinanceBackend
from pcapi.utils import cache as cache_utils
from pcapi.utils import date as date_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)

COOKIES_CACHE_DURATION = 900  # in seconds = 15min
REDIS_COOKIES_CACHE_KEY = "cache:cegid:cookies"

INVENTORY_IDS = {
    "ORINDGRANT_18": "ORIND18P0000",
    "OCINDGRANT_18": "CTIND18P0000",
    "CGINDGRANT_18": "CGIND18P0000",
    "ORINDGRANT_15_17": "ORIND18M0000",
    "OCINDGRANT_15_17": "CTIND18M0000",
    "CGINDGRANT_15_17": "CGIND18M0000",
    "ORCOLEDUC_NAT": "ORCOLEDU0000",
    "CGCOLEDUC_NAT": "CGCOLEDU0000",
    "ORCOLAGRI": "ORCOLAGR0000",
    "CGCOLAGRI": "CGCOLAGR0000",
    "ORCOLARMEES": "ORCOLARM0000",
    "CGCOLARMEES": "CGCOLARM0000",
    "ORCOLMER": "ORCOLMER0000",
    "CGCOLMER": "CGCOLMER0000",
    "ORCOLMEG": "ORCOLMEG0000",
    "CGCOLMEG": "CGCOLMEG0000",
}


class CegidFinanceBackend(BaseFinanceBackend):
    timeout = 20  # seconds

    def __init__(self) -> None:
        self.base_url = settings.CEGID_URL
        self._interface = "entity/INTERFACES/23.200.001"
        self._cookies: dict = {}

    def _authenticate(self) -> str:
        username = settings.CEGID_USERNAME
        password = settings.CEGID_PASSWORD
        company = settings.CEGID_COMPANY

        response = requests.post(
            f"{self.base_url}/entity/auth/login",
            json={
                "name": username,
                "password": password,
                "company": company,
            },
        )
        if self._get_exception_type(response) in ("PX.Data.PXException", "PX.Data.PXUndefinedCompanyException"):
            raise exceptions.FinanceBackendInvalidCredentials(response, "Invalid credentials")

        if response.status_code != 204:
            raise exceptions.FinanceBackendUnexpectedResponse(response, "Couldn't authenticate")

        return json.dumps(response.cookies.get_dict())

    def _request(self, method: str, url: str, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """
        Private method to operate requests:
        - Automatically reconnects in case of cookies/token expiration
        - Use previously fetched cookies to authenticate requests
        """
        force_cache_update = False
        for _ in range(2):  # In case the cookies expire, delete the stored one and re-authenticate
            try:
                response = requests.request(method, url, *args, cookies=self._get_cookies(force_cache_update), **kwargs)
            except requests.exceptions.RequestException as exc:
                raise exceptions.FinanceBackendApiError(f"Network error on Cegid API: {url}") from exc
            if response.status_code == 422:
                raise exceptions.FinanceBackendBadRequest(response, "Invalid data body")
            if response.status_code != 401:
                return response
            force_cache_update = True

        raise exceptions.FinanceBackendUnauthorized(response, "Unauthorized request")

    def _get_cookies(self, force_cache_update: bool) -> dict:
        cached_cookies = cache_utils.get_from_cache(
            retriever=self._authenticate,
            key_template=REDIS_COOKIES_CACHE_KEY,
            expire=COOKIES_CACHE_DURATION,
            force_update=force_cache_update,
        )
        self._cookies = json.loads(str(cached_cookies))
        return self._cookies

    def get_bank_account(self, bank_account_id: int) -> dict:
        url = f"{self.base_url}/{self._interface}/Vendor/{bank_account_id}"
        params = {"$expand": "MainContact/Address,PrimaryContact,Attributes"}
        response = self._request("GET", url, params=params)

        if self._get_exception_type(response) == "PX.Api.ContractBased.NoEntitySatisfiesTheConditionException":
            raise exceptions.FinanceBackendBankAccountNotFound(
                response, f"Couldn't find Vendor for BankAccount #{bank_account_id}"
            )
        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Unexpected response when getting Vendor related to BankAccount #{bank_account_id}"
            )

        response_json = response.json()
        response_json["VendorLocation"] = self._get_vendor_location(bank_account_id)

        return response_json

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict:
        """
        Create or update a bank account in Flex.
        The logic of storage in Flex is different: bank account model is split into 2 entities:
         - Vendor: the actual BankAccount
         - VendorLocation where the RIB information (IBAN) is stored
        In order to operate a creation/update operation we have to send 3 requests:
         - PUT Vendor
         - GET VendorLocation
         - PUT VendorLocation
         Missing : SIEN (aka siret dans cegid), famille de fournisseur (VendorClassID)
        """
        url_vendor = f"{self.base_url}/{self._interface}/Vendor"

        body = {
            "CashAccount": {"value": "CD512000"},
            "CurrencyID": {"value": "EUR"},
            "LegalName": {
                "value": bank_account.offerer.name[:70],
            },
            "MainContact": {
                "Address": {
                    "Country": {"value": "FR"},
                    "City": {"value": bank_account.offerer.city},
                    "PostalCode": {"value": bank_account.offerer.postalCode},
                    "AddressLine1": {"value": bank_account.offerer.street[:50]},
                    "State": {"value": bank_account.offerer.departementCode},
                },
            },
            "NatureEco": {"value": "Exempt operations"},
            "PaymentMethod": {
                "value": "VSEPA",
            },
            "Siret": {"value": bank_account.offerer.siren},
            "Status": {
                "value": "Active",
            },
            "TaxZone": {"value": "EXO"},
            "Terms": {"value": "30J"},
            "VendorClass": {"value": "ACTEURCULT"},
            "VendorID": {
                "value": str(bank_account.id),
            },
            "VendorName": {
                "value": bank_account.label,
            },
        }

        response = self._request("PUT", url_vendor, json=body)
        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Couldn't create Vendor for BankAccount #{bank_account.id}"
            )

        response_json = response.json()
        response_json["VendorLocation"] = self._upsert_vendor_location(bank_account)

        return response_json

    def _upsert_vendor_location(self, bank_account: finance_models.BankAccount) -> dict:
        """
        Create or update VendorLocation where the RIB parameter is stored (IBAN)
        To be able to update the values for an existing entry we have to:
         - First check if there is already an existing VendorLocation
         - If not any proceed to creation
         - If any, there must be only one entry as we only have one RIB per BankAccount. (cf. _get_vendor_location)
         - To avoid creating a new entry we have to get the VendorLocation's id as well as the id of IBAN row
         - Inject it in the creation body to allow Flex to identify and update it
         - Send the body with ids to update the VendorLocation
        """
        iban = {
            "rowNumber": 1,
            "Code": {"value": "IBAN"},
            "PaymentMethod": {"value": "VSEPA"},
            "Valeur": {"value": bank_account.iban},
        }
        body = {
            "LocationID": {"value": "MAIN"},
            "PaymentMethod": {"value": "VSEPA"},
            "RIB": [iban],
            "Status": {"value": "Active"},
            "VendorID": {"value": str(bank_account.id)},
        }
        vendor_location = self._get_vendor_location(bank_account.id)
        if vendor_location:  # Update existing VendorLocation
            # Inject the VendorLocation id to allow Flex to identify it and update it
            body["id"] = vendor_location["id"]

            del body["LocationID"]

            old_rib = vendor_location.get("RIB", [])

            old_ibans = [e for e in old_rib if e.get("Code", {}).get("value") == "IBAN"]
            if old_ibans:
                old_iban = old_ibans[0]  # It's certainly 1 iban as the check is done in `_get_vendor_location`
                # Inject existing row's "id" and "rowNumber" fields to operate and avoid creating a new one
                if "id" in old_iban:
                    iban["id"] = old_iban["id"]
                if "rowNumber" in old_iban:
                    iban["rowNumber"] = old_iban["rowNumber"]

        url_vendor_location = f"{self.base_url}/{self._interface}/VendorLocation"
        params_vendor_location = {"$expand": "RIB"}
        response = self._request("PUT", url_vendor_location, params=params_vendor_location, json=body)
        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Couldn't update VendorLocation for BankAccount #{bank_account.id}"
            )
        return response.json()

    def _get_vendor_location(self, bank_account_id: int) -> dict:
        url = f"{self.base_url}/{self._interface}/VendorLocation"
        params = {"$expand": "RIB", "$filter": f"VendorID eq '{bank_account_id}'"}
        response = self._request("GET", url, params=params)
        response_json = response.json()

        if self._get_exception_type(response) == "PX.Api.ContractBased.NoEntitySatisfiesTheConditionException":
            raise exceptions.FinanceBackendBankAccountNotFound(
                response, f"Wrong query to get VendorLocation for BankAccount #{bank_account_id}"
            )
        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Unexpected response for VendorLocation query of BankAccount #{bank_account_id}"
            )
        if len(response_json) > 1:
            raise exceptions.FinanceBackendInconsistentDistantData(
                response, f"Found more than 1 VendorLocation for Vendor {bank_account_id}"
            )

        if len(response_json) == 1:
            vendor_location = response_json[0]
            old_rib = vendor_location.get("RIB", [])

            old_ibans = [e for e in old_rib if e.get("Code", {}).get("value") == "IBAN"]
            if len(old_ibans) > 1:
                # Shouldn't happen
                raise exceptions.FinanceBackendInconsistentDistantData(
                    response, f"Found multiple iban rows for VendorLocation of BankAccount #{bank_account_id}"
                )

            return vendor_location

        return {}

    def push_invoice(self, invoice: finance_models.Invoice) -> dict:
        """
        Create a new invoice.
        """
        assert invoice.bankAccountId  # helps mypy
        url = f"{self.base_url}/{self._interface}/Bill?$expand=Details"
        invoice_lines = self.get_invoice_lines(invoice)
        lines = [
            {
                "Amount": {"value": str(finance_utils.cents_to_full_unit(line["amount"]))},
                "Branch": {"value": "PASSCULT"},
                "InventoryID": {"value": INVENTORY_IDS[line["product_id"]]},
                "TransactionDescription": {"value": line["title"]},
                "Description": {"value": line["title"]},
                "Qty": {"value": 1},
                "UnitCost": {"value": str(finance_utils.cents_to_full_unit(line["amount"]))},
                "UOM": {"value": "UNITE"},
            }
            for line in invoice_lines
        ]

        vendor_location = self._get_vendor_location(invoice.bankAccountId)
        total_amount = -sum(e["amount"] for e in invoice_lines)
        invoice_date_range = self._get_formatted_invoice_description(invoice.date)
        body = {
            "Amount": {"value": str(-finance_utils.cents_to_full_unit(total_amount))},
            "ApprovedForPayment": {"value": False},
            "Balance": {"value": str(-finance_utils.cents_to_full_unit(total_amount))},
            "BranchID": {"value": "PASSCULT"},
            "CurrencyID": {"value": "EUR"},
            "Date": {"value": self.format_datetime(invoice.date)},
            "Description": {"value": f"{invoice.reference} - {invoice_date_range}"},  # F25xxxx - <01/12-15/12>
            "Details": lines,
            "Hold": {"value": False},
            "LocationID": {"value": vendor_location["LocationID"]["value"]},
            "PostPeriod": {"value": f"{invoice.date:%m%Y}"},
            # "ReferenceNbr": {"value": invoice.reference},  # This has no effect because XRP generates an incremental ID that cannot be overriden
            "RefNbr": {"value": invoice.reference},
            "Status": {"value": "Open"},
            "TaxTotal": {"value": "0"},
            "Terms": {"value": "30J"},
            "Type": {"value": "ADR" if invoice.reference.startswith("A") else "INV"},
            "Vendor": {"value": str(invoice.bankAccountId)},
            "VendorRef": {"value": invoice.reference},
        }

        response = self._request("PUT", url, json=body)

        if (
            response.status_code == 500
            and self._get_exception_type(response) == "PX.Api.ContractBased.OutcomeEntityHasErrorsException"
        ):
            raise exceptions.FinanceBackendInvoiceAlreadyExists(
                response, f"Invoice '{invoice.reference}' already pushed"
            )

        if response.status_code != 200:
            raise exceptions.FinanceBackendBadRequest(response, "Error in invoice creation payload")

        return response.json()

    def format_datetime(self, source_datetime: datetime.datetime) -> str:
        utc_source_datetime = date_utils.make_timezone_aware_utc(source_datetime)

        formatted_datetime = utc_source_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        formatted_offset = date_utils.format_offset(utc_source_datetime.utcoffset())
        return f"{formatted_datetime}{formatted_offset}"

    def _get_formatted_invoice_description(self, invoice_date: datetime.datetime) -> str:
        start_date, end_date = self._get_invoice_daterange(invoice_date)
        return f"{start_date:%d/%m}-{end_date:%d/%m}"

    def get_invoice(self, reference: str) -> dict:
        url = f"{self.base_url}/{self._interface}/Bill"
        # Search by using VendorRef instead of ReferenceNbr because ReferenceNbr is automatically generated by
        # XRP Flex when creating the invoice and it's an incremental ID.
        # We keep using VendorRef to represent the backend's reference eg. F24xxxx
        response = self._request("GET", url, params={"$filter": f"VendorRef eq '{reference}'", "$expand": "Details"})

        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Unexpected response for Bill query of invoice '{reference}'"
            )

        response_json = response.json()

        if len(response_json) < 1:
            raise exceptions.FinanceBackendInvoiceNotFound(
                response, f"Couldn't find invoice with reference: '{reference}'"
            )

        if len(response_json) > 1:
            raise exceptions.FinanceBackendInconsistentDistantData(
                response, f"Found multiple invoices with the same reference: '{reference}'"
            )

        return response_json[0]

    @property
    def is_configured(self) -> bool:
        return all(
            bool(e)
            for e in (settings.CEGID_URL, settings.CEGID_USERNAME, settings.CEGID_PASSWORD, settings.CEGID_COMPANY)
        )

    def _get_exception_type(self, response: requests.Response) -> str | None:
        if response.status_code == 500 and ("application/json" in response.headers.get("content-type", "")):
            return response.json().get("exceptionType")
        return None

    @property
    def time_to_sleep_between_two_sync_requests(self) -> int:
        # In seconds
        return 10
