import logging
import re

from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.ubble import models as ubble_subsciption_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils


UBBLE_TEST_EMAIL_RE = re.compile(r"^.+(\+ubble_test@.+|@yeswehack.ninja)$")

logger = logging.getLogger(__name__)


def on_ubble_result(fraud_check: fraud_models.BeneficiaryFraudCheck) -> None:
    fraud_api.on_identity_fraud_check_result(fraud_check.user, fraud_check)


def _ubble_readable_score(score: float | None) -> str:
    return ubble_fraud_models.UbbleScore(score).name if score is not None else "AUCUN"


def _ubble_result_fraud_item(user: users_models.User, content: fraud_models.UbbleContent) -> fraud_models.FraudItem:
    status = None
    reason_codes = set(content.reason_codes or [])
    detail = f"Ubble score {_ubble_readable_score(content.score)}: {content.comment}"
    for reason_code in reason_codes:
        match reason_code:
            case fraud_models.FraudReasonCode.BLURRY_VIDEO:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.BLURRY_VIDEO.value
            case fraud_models.FraudReasonCode.DOCUMENT_DAMAGED:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.DOCUMENT_DAMAGED.value
            case fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.ID_CHECK_UNPROCESSABLE.value
            case fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.ID_CHECK_DATA_MATCH.value
            case fraud_models.FraudReasonCode.ID_CHECK_EXPIRED:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.ID_CHECK_EXPIRED.value
            case fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.ID_CHECK_NOT_AUTHENTIC.value
            case fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.ID_CHECK_NOT_SUPPORTED.value
            case fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.LACK_OF_LUMINOSITY.value
            case fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE:
                detail += " | " + ubble_subsciption_models.UbbleDetailMessage.NETWORK_CONNECTION_ISSUE.value

    if reason_codes:
        status = fraud_models.FraudStatus.SUSPICIOUS

    # Decision from identification/score
    if content.score == ubble_fraud_models.UbbleScore.VALID.value:
        id_provider_detected_eligibility = subscription_api.get_id_provider_detected_eligibility(user, content)
        if id_provider_detected_eligibility is None:
            status = fraud_models.FraudStatus.KO
            birth_date = content.get_birth_date()
            registration_datetime = content.get_registration_datetime()
            assert birth_date and registration_datetime  # helps mypy next line
            age = users_utils.get_age_at_date(birth_date, registration_datetime)
            if age < min(users_constants.ELIGIBILITY_UNDERAGE_RANGE):
                reason_codes.add(fraud_models.FraudReasonCode.AGE_TOO_YOUNG)
                detail = ubble_subsciption_models.UbbleDetailMessage.AGE_TOO_YOUNG.value.format(age=age)
            elif age > users_constants.ELIGIBILITY_AGE_18:
                reason_codes.add(fraud_models.FraudReasonCode.AGE_TOO_OLD)
                detail = ubble_subsciption_models.UbbleDetailMessage.AGE_TOO_OLD.value.format(age=age)
        else:
            status = fraud_models.FraudStatus.OK
    elif content.score == ubble_fraud_models.UbbleScore.INVALID.value:
        # Decision from reference-data-check/score
        if content.reference_data_check_score == ubble_fraud_models.UbbleScore.INVALID.value:
            reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH)
            status = fraud_models.FraudStatus.SUSPICIOUS
        elif content.supported == ubble_fraud_models.UbbleScore.INVALID.value:
            # Decision from documents-check/supported
            reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED)
            status = fraud_models.FraudStatus.SUSPICIOUS
        elif content.expiry_date_score == ubble_fraud_models.UbbleScore.INVALID.value:
            # Decision from documents-check/expiry-date-score
            reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_EXPIRED)
            status = fraud_models.FraudStatus.SUSPICIOUS
        elif content.ove_score == ubble_fraud_models.UbbleScore.INVALID.value:
            reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC)
            status = fraud_models.FraudStatus.SUSPICIOUS
        elif not status:
            status = fraud_models.FraudStatus.KO
            reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER)
            detail += (
                f" | reference-data-check score {_ubble_readable_score(content.reference_data_check_score)}"
                f" | document supported {_ubble_readable_score(content.supported)}"
                f" | expiry-date-score {_ubble_readable_score(content.expiry_date_score)}"
            )
    elif content.score == ubble_fraud_models.UbbleScore.UNDECIDABLE.value:
        status = fraud_models.FraudStatus.SUSPICIOUS
        reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE)
        detail += " | " + ubble_subsciption_models.UbbleDetailMessage.ID_CHECK_UNPROCESSABLE.value

    if status is None:
        # This should never happen
        logger.error("Unexpected case in _ubble_result_fraud_item", extra={"content": content, "score": content.score})
        status = fraud_models.FraudStatus.KO
        reason_codes.add(fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER)

    return fraud_models.FraudItem(status=status, detail=detail, reason_codes=list(reason_codes))


def ubble_fraud_checks(user: users_models.User, content: fraud_models.UbbleContent) -> list[fraud_models.FraudItem]:
    ubble_fraud_models_item = _ubble_result_fraud_item(user, content)
    fraud_items = [ubble_fraud_models_item]

    id_piece_number = content.get_id_piece_number()

    if ubble_fraud_models_item.status == fraud_models.FraudStatus.OK or id_piece_number:
        fraud_items.append(fraud_api.validate_id_piece_number_format_fraud_item(id_piece_number))
        if id_piece_number:
            fraud_items.append(fraud_api.duplicate_id_piece_number_fraud_item(user, id_piece_number))

    return fraud_items


def get_ubble_fraud_check(identification_id: str) -> fraud_models.BeneficiaryFraudCheck | None:
    fraud_check = (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
        )
        .filter(fraud_models.BeneficiaryFraudCheck.thirdPartyId == identification_id)
        .one_or_none()
    )
    return fraud_check


def does_match_ubble_test_email(email: str) -> re.Match | None:
    # This function MUST ALWAYS return None in production environment
    if settings.IS_PROD:
        return None

    return UBBLE_TEST_EMAIL_RE.match(email)


def get_restartable_identity_checks(user: users_models.User) -> fraud_models.BeneficiaryFraudCheck | None:
    started_fraud_check = (
        fraud_models.BeneficiaryFraudCheck.query.filter(
            fraud_models.BeneficiaryFraudCheck.user == user,
            fraud_models.BeneficiaryFraudCheck.status == fraud_models.FraudCheckStatus.STARTED,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
            fraud_models.BeneficiaryFraudCheck.eligibilityType == user.eligibility,
        )
        .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
        .first()
    )
    return started_fraud_check
