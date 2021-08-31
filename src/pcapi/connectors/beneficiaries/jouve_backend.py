from dataclasses import dataclass
import datetime
import logging
from typing import Any
from typing import Optional

from pydantic import ValidationError
import requests

from pcapi import settings
from pcapi.core.fraud.models import JouveContent
from pcapi.domain.beneficiary_pre_subscription.model import BeneficiaryPreSubscription
from pcapi.models import BeneficiaryImportSources
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


DEFAULT_JOUVE_SOURCE_ID = None


class ApiJouveException(Exception):
    def __init__(self, message, status_code, route):
        self.message = message
        self.status_code = status_code
        self.route = route
        super().__init__()


class JouveContentValidationError(Exception):
    def __init__(self, message, errors):
        self.message = message
        self.errors = errors
        super().__init__()


def _get_authentication_token() -> str:
    expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
    uri = "/REST/server/authenticationtokens"
    response = requests.post(
        f"{settings.JOUVE_API_DOMAIN}{uri}",
        headers={"Content-Type": "application/json"},
        json={
            "Username": settings.JOUVE_API_USERNAME,
            "Password": settings.JOUVE_API_PASSWORD,
            "VaultGuid": settings.JOUVE_API_VAULT_GUID,
            "Expiration": expiration.isoformat(),
        },
    )

    if response.status_code != 200:
        raise ApiJouveException(
            "Error getting API Jouve authentication token", route=uri, status_code=response.status_code
        )

    response_json = response.json()
    return response_json["Value"]


def _get_raw_content(application_id: str) -> dict:
    token = _get_authentication_token()

    uri = "/REST/vault/extensionmethod/VEM_GetJeuneByID"
    response = requests.post(
        f"{settings.JOUVE_API_DOMAIN}{uri}",
        headers={
            "X-Authentication": token,
        },
        data=str(application_id),
    )

    if response.status_code != 200:
        raise ApiJouveException("Error getting API jouve GetJeuneByID", route=uri, status_code=response.status_code)

    return response.json()


def get_application_content(application_id: str, ignore_id_piece_number_field: bool = False) -> JouveContent:
    application_content = _get_raw_content(application_id)

    try:
        jouve_content = JouveContent(**application_content)
    except ValidationError as exc:
        raise JouveContentValidationError(str(exc), exc.errors)

    if ignore_id_piece_number_field:
        jouve_content.bodyPieceNumber = None

    return jouve_content


def get_subscription_from_content(content: JouveContent) -> BeneficiaryPreSubscription:
    fraud_fields = get_fraud_fields(content)

    return BeneficiaryPreSubscription(
        activity=content.activity,
        address=content.address,
        application_id=content.id,
        city=content.city,
        civility="Mme" if content.gender == "F" else "M.",
        date_of_birth=content.birthDateTxt,
        email=content.email,
        first_name=content.firstName,
        id_piece_number=content.bodyPieceNumber,
        last_name=content.lastName,
        phone_number=content.phoneNumber,
        postal_code=content.postalCode,
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


def get_boolean_fraud_detection_item(value: Optional[str], key: str) -> FraudDetectionItem:
    valid = False
    if value and value == "OK":
        valid = True
    return FraudDetectionItem(key=key, value=value, valid=valid)


def get_threshold_fraud_detection_item(value: Optional[int], key: str, threshold: int) -> FraudDetectionItem:
    valid = False
    try:
        valid = int(value) >= threshold
    except (ValueError, TypeError):
        valid = False

    return FraudDetectionItem(key=key, value=value, valid=valid)


def get_fraud_fields(content: dict) -> dict:
    if not FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS.is_active():
        return {
            "strict_controls": [],
            "non_blocking_controls": [],
        }

    return {
        "strict_controls": [],
        "non_blocking_controls": [
            get_boolean_fraud_detection_item(content.birthLocationCtrl, "birthLocationCtrl"),
            get_threshold_fraud_detection_item(content.bodyBirthDateLevel, "bodyBirthDateLevel", 100),
            get_threshold_fraud_detection_item(content.bodyNameLevel, "bodyNameLevel", 50),
            get_boolean_fraud_detection_item(content.bodyBirthDateCtrl, "bodyBirthDateCtrl"),
            get_boolean_fraud_detection_item(content.bodyNameCtrl, "bodyNameCtrl"),
            get_boolean_fraud_detection_item(content.bodyPieceNumberCtrl, "bodyPieceNumberCtrl"),
            get_threshold_fraud_detection_item(content.bodyPieceNumberLevel, "bodyPieceNumberLevel", 50),
        ],
    }
