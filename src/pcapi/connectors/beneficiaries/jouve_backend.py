import datetime
import logging

import requests

from pcapi import settings
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImportSources


logger = logging.getLogger(__name__)


DEFAULT_JOUVE_SOURCE_ID = None


class ApiJouveException(Exception):
    pass


class FraudControlException(Exception):
    pass


class BeneficiaryJouveBackend:
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

        self._fraud_validation(content, application_id)

        # There is a bug in Jouve that invert first_name and last_name (only testing and staging env)
        # More explanations here: https://passculture.atlassian.net/secure/RapidBoard.jspa?rapidView=34&modal=detail&selectedIssue=PC-7845&quickFilter=278
        # TODO 05/2021: remove this code when Jouve fixed the bug
        first_name = content["lastName"] if settings.IS_TESTING or settings.IS_STAGING else content["firstName"]
        last_name = content["firstName"] if settings.IS_TESTING or settings.IS_STAGING else content["lastName"]

        return BeneficiaryPreSubscription(
            activity=content["activity"],
            address=content["address"],
            application_id=content["id"],
            city=content["city"],
            civility="Mme" if content["gender"] == "F" else "M.",
            date_of_birth=datetime.datetime.strptime(content["birthDate"], "%m/%d/%Y"),
            email=content["email"],
            first_name=first_name,
            last_name=last_name,
            phone_number=content["phoneNumber"],
            postal_code=content["postalCode"],
            source=BeneficiaryImportSources.jouve.value,
            source_id=DEFAULT_JOUVE_SOURCE_ID,
        )

    def _fraud_validation(self, content, application_id):
        controls = {
            "poste_code_ok": content.get("posteCodeCtrl", "OK").upper() != "KO",
            "service_code_ok": content.get("serviceCodeCtrl", "OK").upper() != "KO",
        }

        if not all(controls.values()):
            logger.warning("Id check fraud control ko", extra={"application_id": application_id, "controls": controls})
            raise FraudControlException()
