import datetime
import os

import requests

from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_repository import (
    BeneficiaryPreSubscriptionRepository,
)
from pcapi.infrastructure.repository.beneficiary import beneficiary_jouve_converter


JOUVE_API_DOMAIN = os.environ.get("JOUVE_API_DOMAIN")
JOUVE_PASSWORD = os.environ.get("JOUVE_PASSWORD")
JOUVE_USERNAME = os.environ.get("JOUVE_USERNAME")
JOUVE_VAULT_GUID = os.environ.get("JOUVE_VAULT_GUID")


class ApiJouveException(Exception):
    pass


class BeneficiaryJouveRepository(BeneficiaryPreSubscriptionRepository):
    def _get_authentication_token(self) -> str:
        expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
        response = requests.post(
            f"{JOUVE_API_DOMAIN}/REST/server/authenticationtokens",
            headers={"Content-Type": "application/json"},
            json={
                "Username": JOUVE_USERNAME,
                "Password": JOUVE_PASSWORD,
                "VaultGuid": JOUVE_VAULT_GUID,
                "Expiration": expiration.isoformat(),
            },
        )

        if response.status_code != 200:
            raise ApiJouveException(f"Error {response.status_code} getting API jouve authentication token")

        response_json = response.json()
        return response_json["Value"]

    def get_application_by(self, application_id: int) -> BeneficiaryPreSubscription:
        token = self._get_authentication_token()

        response = requests.post(
            f"{JOUVE_API_DOMAIN}/REST/vault/extensionmethod/VEM_GetJeuneByID",
            headers={
                "X-Authentication": token,
            },
            data=str(application_id),
        )

        if response.status_code != 200:
            raise ApiJouveException(
                f"Error {response.status_code} getting API jouve GetJouveByID with id: {application_id}"
            )

        return beneficiary_jouve_converter.to_domain(response.json())
