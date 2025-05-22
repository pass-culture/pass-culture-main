import datetime
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

TOKEN_CACHE_DURATION = 3600  # in seconds = 1h
REDIS_TOKEN_CACHE_KEY = "cache:cegid:token"

INVENTORY_IDS = {
    "ORINDGRANT_18": "ORIND18P0000",
    "OCINDGRANT_18": "CTIND18P0000",
    "CGINDGRANT_18": "CGIND18P0000",
    "ORINDGRANT_15_17": "ORIND18M0000",
    "OCINDGRANT_15_17": "CTIND18M0000",
    "CGINDGRANT_15_17": "CGIND18M0000",
    "ORINDGRANT_18_V3": "ORIND18PPR00",
    "OCINDGRANT_18_V3": "CTIND18PPR00",
    "CGINDGRANT_18_V3": "CGIND18PPR00",
    "ORINDGRANT_17_V3": "ORIND18MPR00",
    "OCINDGRANT_17_V3": "CTIND18MPR00",
    "CGINDGRANT_17_V3": "CGIND18MPR00",
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
        self._interface = "entity/eCommerce/23.200.001"

    def _authenticate(self) -> str:
        username = settings.CEGID_USERNAME
        password = settings.CEGID_PASSWORD
        client_id = settings.CEGID_CLIENT_ID
        client_secret = settings.CEGID_CLIENT_SECRET

        response = requests.post(
            f"{self.base_url}/identity/connect/token",
            headers={
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded",
            },
            data={
                "username": username,
                "password": password,
                "grant_type": "password",
                "scope": "api",
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )

        if response.status_code != 200:
            raise exceptions.FinanceBackendInvalidCredentials(response, "Couldn't authenticate")

        response_json = response.json()
        if response_json.get("token_type") != "Bearer" or not response_json.get("access_token"):
            raise exceptions.FinanceBackendInvalidCredentials(response, "Unexpected authentication response")

        return response_json["access_token"]

    def _request(self, method: str, url: str, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """
        Private method to operate requests:
        - Automatically reconnects in case of token expiration
        - Use previously fetched cookies to authenticate requests
        """
        force_cache_update = False
        for _ in range(2):  # In case the token expires, delete the stored one and re-authenticate
            try:
                headers = kwargs.pop("headers", {})
                token = self._get_token(force_cache_update)
                headers["Authorization"] = f"Bearer {token}"
                response = requests.request(method, url, *args, headers=headers, **kwargs)
            except requests.exceptions.RequestException as exc:
                raise exceptions.FinanceBackendApiError(f"Network error on Cegid API: {url}") from exc
            if response.status_code == 422:
                raise exceptions.FinanceBackendBadRequest(response, "Invalid data body")
            if response.status_code != 401:
                return response
            force_cache_update = True

        raise exceptions.FinanceBackendUnauthorized(response, "Unauthorized request")

    def _get_token(self, force_cache_update: bool) -> str:
        token = cache_utils.get_from_cache(
            retriever=self._authenticate,
            key_template=REDIS_TOKEN_CACHE_KEY,
            expire=TOKEN_CACHE_DURATION,
            force_update=force_cache_update,
        )
        return str(token)  # Cast as string here to help mypy

    def get_bank_account(self, bank_account_id: int) -> dict:
        url = f"{self.base_url}/{self._interface}/Vendor/{bank_account_id}"
        params = {"$expand": "MainContact/Address,PrimaryContact,Attributes,PaymentInstructions"}
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

        return response_json

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict:
        """
        Create or update a bank account in Flex.
        """
        url_vendor = f"{self.base_url}/{self._interface}/Vendor"
        params = {"$expand": "PaymentInstructions"}

        body = {
            "CashAccount": {"value": "CD512000"},
            "CurrencyID": {"value": "EUR"},
            "LegalName": {"value": finance_utils.clean_names_for_SEPA(bank_account.offerer.name)[:70]},
            "LocationName": {"value": "Emplacement principal"},
            "MainContact": {
                "Address": {
                    "AddressID": {"value": "PRINCIPAL"},
                    "Country": {"value": "FR"},
                    "City": {"value": bank_account.offerer.city},
                    "PostalCode": {"value": bank_account.offerer.postalCode},
                    "AddressLine1": {"value": bank_account.offerer.street[:50]},
                    "State": {"value": bank_account.offerer.departementCode},
                },
            },
            "NatureEco": {"value": "Exempt operations"},
            "PaymentMethod": {"value": "VSEPA"},
            "PaymentInstructions": [
                {
                    "Description": {"value": "IBAN"},
                    "PaymentInstructionsID": {"value": "IBAN"},
                    "PaymentMethod": {"value": "VSEPA"},
                    "Value": {"value": bank_account.iban},
                    "custom": {},
                },
            ],
            "Siret": {"value": bank_account.offerer.siren},
            "Status": {"value": "Active"},
            "TaxZone": {"value": "EXO"},
            "Terms": {"value": "30J"},
            "VendorClass": {"value": "ACTEURCULT"},
            "VendorID": {"value": str(bank_account.id)},
            "VendorName": {"value": bank_account.label},
        }

        response = self._request("PUT", url_vendor, params=params, json=body)
        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Couldn't create Vendor for BankAccount #{bank_account.id}"
            )

        response_json = response.json()
        return response_json

    @staticmethod
    def _format_amount(amount_in_cent: int) -> str:
        """Convert from amount in cents (integer) to formatted unsigned string in full unit"""
        amount = finance_utils.cents_to_full_unit(amount_in_cent)
        abs_amount = abs(amount)
        return str(abs_amount)

    def push_invoice(self, invoice: finance_models.Invoice) -> dict:
        """
        Create a new invoice.
        """
        assert invoice.bankAccountId  # helps mypy
        url = f"{self.base_url}/{self._interface}/Bill"
        params = {"$expand": "Details"}
        invoice_lines = self.get_invoice_lines(invoice)
        lines = [
            {
                "Amount": {"value": self._format_amount(line["amount"])},
                "Branch": {"value": "PASSCULT"},
                "InventoryID": {"value": INVENTORY_IDS[line["product_id"]]},
                "TransactionDescription": {"value": line["title"]},
                "Description": {"value": line["title"]},
                "Qty": {"value": 1},
                "UnitCost": {"value": self._format_amount(line["amount"])},
                "UOM": {"value": "UNITE"},
            }
            for line in invoice_lines
        ]

        total_amount_str = self._format_amount(sum(e["amount"] for e in invoice_lines))
        invoice_date_range = self._get_formatted_invoice_description(invoice.date)
        body = {
            "Amount": {"value": total_amount_str},
            "ApprovedForPayment": {"value": False},
            "Balance": {"value": total_amount_str},
            "BranchID": {"value": "PASSCULT"},
            "CurrencyID": {"value": "EUR"},
            "Date": {"value": self.format_datetime(invoice.date)},
            "Description": {"value": f"{invoice.reference} - {invoice_date_range}"},  # F25xxxx - <01/12-15/12>
            "Details": lines,
            "Hold": {"value": False},
            "LocationID": {"value": "PRINCIPAL"},
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

        response = self._request("PUT", url, params=params, json=body)

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
            for e in (
                settings.CEGID_URL,
                settings.CEGID_USERNAME,
                settings.CEGID_PASSWORD,
                settings.CEGID_CLIENT_ID,
                settings.CEGID_CLIENT_SECRET,
            )
        )

    def _get_exception_type(self, response: requests.Response) -> str | None:
        if response.status_code == 500 and ("application/json" in response.headers.get("content-type", "")):
            return response.json().get("exceptionType")
        return None
