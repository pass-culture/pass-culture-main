from dataclasses import dataclass
import datetime
import logging
from typing import Any

import requests

from pcapi import settings
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImportSources
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries


logger = logging.getLogger(__name__)


DEFAULT_JOUVE_SOURCE_ID = None


class ApiJouveException(Exception):
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

    def _get_application_content(self, application_id: str) -> dict:
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

        return response.json()

    def get_application_by(self, application_id: int) -> BeneficiaryPreSubscription:
        content = self._get_application_content(application_id)
        fraud_fields = get_fraud_fields(content)

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
            fraud_fields=fraud_fields,
        )


@dataclass
class FraudDetectionItem:
    key: str
    value: Any
    valid: bool

    def __str__(self):
        return f"{self.key}: {self.value} - {self.valid}"


def get_boolean_fraud_detection_item(content: dict, key: str) -> FraudDetectionItem:
    value = content.get(key)
    valid = value.upper() != "KO" if value else True
    return FraudDetectionItem(key=key, value=value, valid=valid)


def get_threshold_fraud_detection_item(content: dict, key: str, threshold: int) -> FraudDetectionItem:
    value = content.get(key)

    try:
        valid = int(value) >= threshold if value else True
    except ValueError:
        valid = True

    return FraudDetectionItem(key=key, value=value, valid=valid)


def get_fraud_fields(content: dict) -> dict:
    if not feature_queries.is_active(FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS):
        return {
            "strict_controls": [],
            "non_blocking_controls": [],
        }

    return {
        "strict_controls": [
            get_boolean_fraud_detection_item(content, "posteCodeCtrl"),
            get_boolean_fraud_detection_item(content, "serviceCodeCtrl"),
        ],
        "non_blocking_controls": [
            get_threshold_fraud_detection_item(content, "bodyBirthDateLevel", 100),
            get_boolean_fraud_detection_item(content, "birthLocationCtrl"),
            get_threshold_fraud_detection_item(content, "bodyNameLevel", 50),
            get_boolean_fraud_detection_item(content, "bodyBirthDateCtrl"),
            get_boolean_fraud_detection_item(content, "bodyFirstNameCtrl"),
            get_threshold_fraud_detection_item(content, "bodyFirstNameLevel", 50),
            get_boolean_fraud_detection_item(content, "bodyNameCtrl"),
            get_boolean_fraud_detection_item(content, "bodyPieceNumberCtrl"),
            get_threshold_fraud_detection_item(content, "bodyPieceNumberLevel", 50),
            get_boolean_fraud_detection_item(content, "creatorCtrl"),
            get_boolean_fraud_detection_item(content, "initialNumberCtrl"),
            get_boolean_fraud_detection_item(content, "initialSizeCtrl"),
        ],
    }
