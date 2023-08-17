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


def _ubble_message_from_code(code: fraud_models.FraudReasonCode) -> str:
    return ubble_subsciption_models.UBBLE_CODE_ERROR_MAPPING[code].detail_message


def _ubble_result_fraud_item(user: users_models.User, content: fraud_models.UbbleContent) -> fraud_models.FraudItem:
    status = None
    reason_codes = set(content.reason_codes or [])
    detail = f"Ubble score {_ubble_readable_score(content.score)}: {content.comment}"
    for reason_code in reason_codes:
        ubble_error = ubble_subsciption_models.UBBLE_CODE_ERROR_MAPPING.get(reason_code)
        if ubble_error:
            detail += " | " + ubble_error.detail_message

    if reason_codes:
        status = fraud_models.FraudStatus.SUSPICIOUS

    # Decision from identification/score
    if content.score == ubble_fraud_models.UbbleScore.VALID.value:
        id_provider_detected_eligibility = subscription_api.get_id_provider_detected_eligibility(user, content)
        if id_provider_detected_eligibility:
            status = fraud_models.FraudStatus.OK
        else:
            status = fraud_models.FraudStatus.KO
            birth_date = content.get_birth_date()
            registration_datetime = content.get_registration_datetime()
            assert birth_date and registration_datetime  # helps mypy next line
            age = users_utils.get_age_at_date(birth_date, registration_datetime)
            if age < min(users_constants.ELIGIBILITY_UNDERAGE_RANGE):
                reason_codes.add(fraud_models.FraudReasonCode.AGE_TOO_YOUNG)
                detail = _ubble_message_from_code(fraud_models.FraudReasonCode.AGE_TOO_YOUNG).format(age=age)
            elif age > users_constants.ELIGIBILITY_AGE_18:
                reason_codes.add(fraud_models.FraudReasonCode.AGE_TOO_OLD)
                detail = _ubble_message_from_code(fraud_models.FraudReasonCode.AGE_TOO_OLD).format(age=age)
    elif content.score == ubble_fraud_models.UbbleScore.INVALID.value:
        for score, reason_code in [
            (content.reference_data_check_score, fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH),
            (content.supported, fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED),
            (content.expiry_date_score, fraud_models.FraudReasonCode.ID_CHECK_EXPIRED),
            (content.ove_score, fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC),
        ]:
            if score == ubble_fraud_models.UbbleScore.INVALID.value:
                status = fraud_models.FraudStatus.SUSPICIOUS
                reason_codes.add(reason_code)

        if not status:
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
        detail += " | " + _ubble_message_from_code(fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE)

    if not status:
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
