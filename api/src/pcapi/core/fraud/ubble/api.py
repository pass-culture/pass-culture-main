import logging
import re

from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.models import SubscriptionItemStatus
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db


UBBLE_TEST_EMAIL_RE = re.compile(r"^.+\+ubble_test@.+$")

logger = logging.getLogger(__name__)


def on_ubble_result(fraud_check: fraud_models.BeneficiaryFraudCheck) -> None:
    fraud_api.on_identity_fraud_check_result(fraud_check.user, fraud_check)


def _ubble_readable_score(score: float | None) -> str:
    return ubble_fraud_models.UbbleScore(score).name if score is not None else "AUCUN"


def _ubble_result_fraud_item(
    user: users_models.User, content: ubble_fraud_models.UbbleContent
) -> fraud_models.FraudItem:
    status = None
    reason_code = None
    detail = f"Ubble score {_ubble_readable_score(content.score)}: {content.comment}"

    # Decision from identification/score
    if content.score == ubble_fraud_models.UbbleScore.VALID.value:
        id_provider_detected_eligibility = subscription_api.get_id_provider_detected_eligibility(user, content)
        if id_provider_detected_eligibility is None:
            status = fraud_models.FraudStatus.KO
            age = users_utils.get_age_at_date(content.get_birth_date(), content.get_registration_datetime())  # type: ignore [arg-type]
            if age < min(users_constants.ELIGIBILITY_UNDERAGE_RANGE):
                reason_code = fraud_models.FraudReasonCode.AGE_TOO_YOUNG
                detail = f"L'utilisateur n'a pas encore l'âge requis ({age} ans)"
            elif age > users_constants.ELIGIBILITY_AGE_18:
                reason_code = fraud_models.FraudReasonCode.AGE_TOO_OLD
                detail = f"L'utilisateur a dépassé l'âge maximum ({age} ans)"
        else:
            status = fraud_models.FraudStatus.OK
    elif content.score == ubble_fraud_models.UbbleScore.INVALID.value:
        # Decision from reference-data-check/score
        if content.reference_data_check_score == ubble_fraud_models.UbbleScore.INVALID.value:
            status = fraud_models.FraudStatus.SUSPICIOUS
            reason_code = fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH
            detail += " | Les informations de la pièce d'identité ne correspondent pas"
        else:
            # Decision from documents-check/supported
            if content.supported == ubble_fraud_models.UbbleScore.INVALID.value:
                status = fraud_models.FraudStatus.SUSPICIOUS
                reason_code = fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED
                detail += " | Le document d'identité n'est pas supporté"
            else:
                # Decision from documents-check/expiry-date-score
                if content.expiry_date_score == ubble_fraud_models.UbbleScore.INVALID.value:
                    status = fraud_models.FraudStatus.SUSPICIOUS
                    reason_code = fraud_models.FraudReasonCode.ID_CHECK_EXPIRED
                    detail += " | Le document d'identité est expiré"
                elif content.ove_score == ubble_fraud_models.UbbleScore.INVALID.value:
                    status = fraud_models.FraudStatus.SUSPICIOUS
                    reason_code = fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC
                    detail += " | Le document d'identité n'est pas authentique"
                else:
                    status = fraud_models.FraudStatus.KO
                    reason_code = fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER
                    detail += (
                        f" | reference-data-check score {_ubble_readable_score(content.reference_data_check_score)}"
                        f" | document supported {_ubble_readable_score(content.supported)}"
                        f" | expiry-date-score {_ubble_readable_score(content.expiry_date_score)}"
                    )
    elif content.score == ubble_fraud_models.UbbleScore.UNDECIDABLE.value:
        status = fraud_models.FraudStatus.SUSPICIOUS
        reason_code = fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE
        detail += " | Ubble n'a pas réussi à lire le document"

    if status is None:
        # This should never happen
        logger.error("Unexpected case in _ubble_result_fraud_item", extra={"content": content, "score": content.score})
        status = fraud_models.FraudStatus.KO
        reason_code = fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER

    return fraud_models.FraudItem(status=status, detail=detail, reason_code=reason_code)


def ubble_fraud_checks(
    user: users_models.User, content: ubble_fraud_models.UbbleContent
) -> list[fraud_models.FraudItem]:
    ubble_fraud_models_item = _ubble_result_fraud_item(user, content)
    fraud_items = [ubble_fraud_models_item]

    id_piece_number = content.get_id_piece_number()

    if ubble_fraud_models_item.status == fraud_models.FraudStatus.OK or id_piece_number:
        fraud_items.append(fraud_api.validate_id_piece_number_format_fraud_item(id_piece_number))
        if id_piece_number:
            fraud_items.append(fraud_api.duplicate_id_piece_number_fraud_item(user, id_piece_number))

    return fraud_items


def start_ubble_fraud_check(user: users_models.User, ubble_content: ubble_fraud_models.UbbleContent) -> None:
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_models.FraudCheckType.UBBLE,
        thirdPartyId=str(ubble_content.identification_id),
        resultContent=ubble_content,  # type: ignore [arg-type]
        status=fraud_models.FraudCheckStatus.STARTED,
        eligibilityType=user.eligibility,
    )
    db.session.add(fraud_check)
    db.session.commit()


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


def is_user_allowed_to_perform_ubble_check(
    user: users_models.User, eligibility_type: users_models.EligibilityType | None
) -> bool:
    from pcapi.core.subscription.ubble import api as ubble_subscription_api

    # Ubble check must be performed for an eligible credit
    if not eligibility_type:
        return False

    fraud_checks = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.user == user,
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.UBBLE,
        fraud_models.BeneficiaryFraudCheck.eligibilityType == eligibility_type,
    ).all()

    status = ubble_subscription_api.get_ubble_subscription_item_status(user, eligibility_type, fraud_checks)

    return status == SubscriptionItemStatus.TODO


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
