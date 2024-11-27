import json
import logging
import typing

from pcapi import settings
from pcapi.core.finance import exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.backend.base import BaseFinanceBackend
from pcapi.utils import cache as cache_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)

COOKIES_CACHE_DURATION = 900  # in seconds = 15min
REDIS_COOKIES_CACHE_KEY = "cache:cegid:cookies"


class CegidFinanceBackend(BaseFinanceBackend):
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

    def _request(self, method: str, *args: typing.Any, **kwargs: typing.Any) -> requests.Response:
        """
        Private method to operate requests:
        - Automatically reconnects in case of cookies/token expiration
        - Use previously fetched cookies to authenticate requests
        """
        force_cache_update = False
        for _ in range(2):  # In case the cookies expire, delete the stored one and re-authenticate
            response = requests.request(method, *args, cookies=self._get_cookies(force_cache_update), **kwargs)
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
        response_json["vendor_location"] = self._get_vendor_location(bank_account_id)

        return response_json

    def push_bank_account(self, bank_account: finance_models.BankAccount) -> dict:
        """
        Create or update a bank account in Flex.
        The logic of storage in Flex is different: bank account model is split into 2 entities:
         - Vendor: the actual BankAccount
         - VendorLocation where the RIB information (IBAN and BIC) is stored
        In order to operate a creation/update operation we have to send 3 requests:
         - PUT Vendor
         - GET VendorLocation
         - PUT VendorLocation
        """
        url_vendor = f"{self.base_url}/{self._interface}/Vendor"

        body = {
            "CurrencyID": {"value": "EUR"},
            "VendorClass": {"value": "STANDARD"},
            "VendorID": {
                "value": str(bank_account.id),
            },
            "VendorName": {
                "value": bank_account.label,
            },
            "Status": {
                "value": "Active",
            },
            "LegalName": {
                "value": bank_account.offerer.name,
            },
            "MainContact": {
                "Address": {
                    "Country": {"value": "FR"},
                },
            },
            "NatureEco": {"value": "Exempt operations"},
            "PaymentMethod": {
                "value": "VSEPA",
            },
            "Terms": {"value": "30J"},
        }

        response = self._request("PUT", url_vendor, json=body)
        if response.status_code != 200:
            raise exceptions.FinanceBackendUnexpectedResponse(
                response, f"Couldn't create Vendor for BankAccount #{bank_account.id}"
            )

        response_json = response.json()
        response_json["vendor_location"] = self._upsert_vendor_location(bank_account)

        return response_json

    def _upsert_vendor_location(self, bank_account: finance_models.BankAccount) -> dict:
        """
        Create or update VendorLocation where the RIB parameters are stored (IBAN and BIC)
        To be able to update the values for an existing entry we have to:
         - First check if there is already an existing VendorLocation
         - If not any proceed to creation
         - If any, there must be only one entry as we only have one RIB per BankAccount. (cf. _get_vendor_location)
         - To avoid creating a new entry we have to get the VendorLocation's id as well as the id of IBAN and BIC rows
         - Inject them in the creation body to allow Flex to identify and update them
         - Send the body with ids to update the VendorLocation
        """
        iban = {
            "rowNumber": 1,
            "Code": {"value": "IBAN"},
            "PaymentMethod": {"value": "VSEPA"},
            "Valeur": {"value": bank_account.iban},
        }
        bic = {
            "rowNumber": 2,
            "Code": {"value": "BIC"},
            "PaymentMethod": {"value": "VSEPA"},
            "Valeur": {"value": bank_account.bic},
        }
        body = {
            "LocationID": {"value": "MAIN"},
            "PaymentMethod": {"value": "VSEPA"},
            "RIB": [iban, bic],
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

            old_bics = [e for e in old_rib if e.get("Code", {}).get("value") == "BIC"]
            if len(old_bics) == 1:  # It's certainly 1 bic as the check is done in `_get_vendor_location`
                old_bic = old_bics[0]
                # Inject existing row's "id" and "rowNumber" fields to operate and avoid creating a new one
                if "id" in old_bic:
                    bic["id"] = old_bic["id"]
                if "rowNumber" in old_bic:
                    bic["rowNumber"] = old_bic["rowNumber"]

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
                    response, f"Found multiple bic rows for VendorLocation of BankAccount #{bank_account_id}"
                )

            old_bics = [e for e in old_rib if e.get("Code", {}).get("value") == "BIC"]
            if len(old_bics) > 1:
                # Shouldn't happen either
                raise exceptions.FinanceBackendInconsistentDistantData(
                    response, f"Found multiple bic rows for VendorLocation of BankAccount #{bank_account_id}"
                )

            return vendor_location

        return {}

    def push_invoice(self, invoice: finance_models.Invoice) -> dict:
        # TODO: implement push invoice
        return {}

    def get_invoice(self, reference: str) -> dict:
        # TODO: implement get invoice
        return {}

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
