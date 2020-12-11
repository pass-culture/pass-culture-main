import datetime

import requests

from pcapi import settings
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImportSources


DEFAULT_JOUVE_SOURCE_ID = None


class ApiJouveException(Exception):
    pass


class BeneficiaryJouveRepository:
    def _get_authentication_token(self) -> str:
        expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
        response = requests.post(
            f"{settings.JOUVE_API_DOMAIN}/REST/server/authenticationtokens",
            headers={"Content-Type": "application/json"},
            json={
                "Username": settings.JOUVE_API_USERNAME,
                "Password": settings.JOUVE_API_PASSWORD,
                "VaultGuid": settings.JOUVE_API_VAULT_GUID,
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
            f"{settings.JOUVE_API_DOMAIN}/REST/vault/extensionmethod/VEM_GetJeuneByID",
            headers={
                "X-Authentication": token,
            },
            data=str(application_id),
        )

        if response.status_code != 200:
            raise ApiJouveException(
                f"Error {response.status_code} getting API jouve GetJouveByID with id: {application_id}"
            )

        content = response.json()
        return BeneficiaryPreSubscription(
            activity=content["activity"],
            address=content["address"],
            application_id=content["id"],
            city=content["city"],
            civility="Mme" if content["gender"] == "F" else "M.",
            date_of_birth=datetime.datetime.strptime(content["birthDate"], "%m/%d/%Y"),
            email=content["email"],
            first_name=content["firstName"],
            last_name=content["lastName"],
            phone_number=content["phoneNumber"],
            postal_code=content["postalCode"],
            source=BeneficiaryImportSources.jouve.value,
            source_id=DEFAULT_JOUVE_SOURCE_ID,
        )
