import datetime
import logging
import re
import typing

import pydantic
import pytz
import sqlalchemy

from pcapi.connectors.beneficiaries import jouve_backend
from pcapi.core.fraud import exceptions
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.exceptions import BeneficiaryFraudResultCannotBeDowngraded
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.user_queries import matching

from . import ubble as ubble_api
from .. import exceptions
from .. import models
from .. import repository as fraud_repository
from ..models import ubble as ubble_models


logger = logging.getLogger(__name__)

FRAUD_RESULT_REASON_SEPARATOR = ";"

USER_PROFILING_RISK_MAPPING = {
    models.UserProfilingRiskRating.TRUSTED: models.FraudStatus.OK,
    models.UserProfilingRiskRating.NEUTRAL: models.FraudStatus.OK,
    models.UserProfilingRiskRating.LOW: models.FraudStatus.OK,
    models.UserProfilingRiskRating.MEDIUM: models.FraudStatus.SUSPICIOUS,
    models.UserProfilingRiskRating.HIGH: models.FraudStatus.KO,
}


def on_educonnect_result(user: users_models.User, educonnect_content: models.EduconnectContent) -> None:
    fraud_check = models.BeneficiaryFraudCheck.query.filter(
        models.BeneficiaryFraudCheck.user == user,
        models.BeneficiaryFraudCheck.type == models.FraudCheckType.EDUCONNECT,
    ).one_or_none()

    if fraud_check:
        fraud_check.thirdPartyId = str(educonnect_content.educonnect_id)
        fraud_check.resultContent = educonnect_content.dict()
    else:
        fraud_check = models.BeneficiaryFraudCheck(
            user=user,
            type=models.FraudCheckType.EDUCONNECT,
            thirdPartyId=str(educonnect_content.educonnect_id),
            resultContent=educonnect_content.dict(),
        )
    on_identity_fraud_check_result(user, fraud_check)
    repository.save(fraud_check)


def on_jouve_result(user: users_models.User, jouve_content: models.JouveContent) -> None:
    if (
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.type.in_([models.FraudCheckType.JOUVE, models.FraudCheckType.DMS]),
        ).count()
        > 0
    ):
        # TODO: raise error and do not allow 2 DMS/Jouve FraudChecks
        return

    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.JOUVE,
        thirdPartyId=str(jouve_content.id),
        resultContent=jouve_content.dict(),
    )
    repository.save(fraud_check)

    # TODO: save user fields from jouve_content
    on_identity_fraud_check_result(user, fraud_check)


def on_dms_fraud_result(
    user: users_models.User,
    dms_content: models.DMSContent,
) -> models.BeneficiaryFraudResult:

    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.DMS,
        thirdPartyId=str(dms_content.application_id),
        resultContent=dms_content,
    )

    db.session.add(fraud_check)
    db.session.commit()
    return on_identity_fraud_check_result(user, fraud_check)


def admin_update_identity_fraud_check_result(
    user: users_models.User, id_piece_number: str
) -> typing.Union[models.BeneficiaryFraudCheck, None]:
    fraud_check = (
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.userId == user.id,
            models.BeneficiaryFraudCheck.type.in_(
                [
                    models.FraudCheckType.JOUVE,
                    models.FraudCheckType.DMS,
                ]
            ),
        )
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )
    if not fraud_check:
        return None
    content = fraud_check.source_data()
    if fraud_check.type == models.FraudCheckType.JOUVE:
        content.bodyPieceNumber = id_piece_number
        content.bodyPieceNumberCtrl = "OK"
        content.bodyPieceNumberLevel = 100
    if fraud_check.type == models.FraudCheckType.DMS:
        content.id_piece_number = id_piece_number
    fraud_check.resultContent = content.dict()
    repository.save(fraud_check)
    return fraud_check


def educonnect_fraud_checks(
    user: users_models.User, beneficiary_fraud_check: models.BeneficiaryFraudCheck
) -> list[models.FraudItem]:
    educonnect_content = beneficiary_fraud_check.source_data()
    fraud_items = []
    # TODO: factorise in on_identity_fraud_check_result for the 4 *_fraud_checks
    fraud_items.append(
        _duplicate_user_fraud_item(
            first_name=educonnect_content.first_name,
            last_name=educonnect_content.last_name,
            birth_date=educonnect_content.birth_date,
            excluded_user_id=user.id,
        )
    )
    fraud_items.append(_underage_user_fraud_item(educonnect_content.birth_date))
    fraud_items.append(_duplicate_ine_hash_fraud_item(educonnect_content.ine_hash, user.id))
    if FeatureToggle.ENABLE_INE_WHITELIST_FILTER.is_active():
        fraud_items.append(_whitelisted_ine_fraud_item(educonnect_content.ine_hash))

    return fraud_items


def jouve_fraud_checks(
    user: users_models.User, beneficiary_fraud_check: models.BeneficiaryFraudCheck
) -> list[models.FraudItem]:
    jouve_content = models.JouveContent(**beneficiary_fraud_check.resultContent)

    fraud_items = []
    fraud_items.append(_check_user_phone_is_validated(user))
    # TODO: factorise in on_identity_fraud_check_result for the 4 *_fraud_checks
    fraud_items.append(
        _duplicate_user_fraud_item(
            first_name=jouve_content.firstName,
            last_name=jouve_content.lastName,
            birth_date=jouve_content.birthDateTxt,
            excluded_user_id=user.id,
        )
    )

    fraud_items.append(validate_id_piece_number_format_fraud_item(jouve_content.bodyPieceNumber))
    fraud_items.append(_duplicate_id_piece_number_fraud_item(user, jouve_content.bodyPieceNumber))
    fraud_items.extend(_id_check_fraud_items(jouve_content))
    return fraud_items


def dms_fraud_checks(
    user: users_models.User, beneficiary_fraud_check: models.BeneficiaryFraudCheck
) -> list[models.FraudItem]:
    dms_content = models.DMSContent(**beneficiary_fraud_check.resultContent)

    fraud_items = []
    fraud_items.append(_check_user_phone_is_validated(user))
    # TODO: factorise in on_identity_fraud_check_result for the 4 *_fraud_checks
    fraud_items.append(
        _duplicate_user_fraud_item(
            first_name=dms_content.first_name,
            last_name=dms_content.last_name,
            birth_date=dms_content.birth_date,
            excluded_user_id=user.id,
        )
    )
    fraud_items.append(_duplicate_id_piece_number_fraud_item(user, dms_content.id_piece_number))
    return fraud_items


def get_eligibility_type(data: models.SubscriptionContentType) -> typing.Optional[users_models.EligibilityType]:
    from pcapi.core.users import api as users_api

    if isinstance(data, models.EduconnectContent):
        registration_datetime = data.registration_datetime
        birth_date = data.birth_date
    elif isinstance(data, models.JouveContent):
        registration_datetime = data.registrationDate
        birth_date = data.birthDateTxt.date() if data.birthDateTxt else None
    elif isinstance(data, fraud_models.ubble.UbbleContent):
        registration_datetime = data.registration_datetime
        birth_date = data.birth_date
    elif isinstance(data, models.DMSContent):
        registration_datetime = data.registration_datetime.astimezone(pytz.utc).replace(tzinfo=None)
        birth_date = data.birth_date
    else:
        raise exceptions.InvalidContentTypeException()

    if registration_datetime is None or birth_date is None:
        return None

    return users_api.get_eligibility_at_date(birth_date, registration_datetime)


def on_identity_fraud_check_result(
    user: users_models.User,
    beneficiary_fraud_check: models.BeneficiaryFraudCheck,
) -> models.BeneficiaryFraudResult:
    fraud_items: list[models.FraudItem] = []

    eligibilityType = get_eligibility_type(beneficiary_fraud_check.source_data())

    if beneficiary_fraud_check.type == models.FraudCheckType.JOUVE:
        fraud_items += jouve_fraud_checks(user, beneficiary_fraud_check)

    elif beneficiary_fraud_check.type == models.FraudCheckType.UBBLE:
        fraud_items += ubble_api.ubble_fraud_checks(user, beneficiary_fraud_check)

    elif beneficiary_fraud_check.type == models.FraudCheckType.DMS:
        fraud_items += dms_fraud_checks(user, beneficiary_fraud_check)

    elif beneficiary_fraud_check.type == models.FraudCheckType.EDUCONNECT:
        fraud_items += educonnect_fraud_checks(user, beneficiary_fraud_check)

    else:
        raise Exception("The fraud_check type is not known")

    fraud_items.append(_check_user_has_no_active_deposit(user, eligibilityType))
    fraud_items.append(_check_user_email_is_validated(user))
    fraud_items.append(_check_user_not_already_beneficiary(user, eligibilityType))

    fraud_result = validate_frauds(user, fraud_items, beneficiary_fraud_check, eligibilityType)
    if (
        beneficiary_fraud_check.type == models.FraudCheckType.JOUVE
        and FeatureToggle.PAUSE_JOUVE_SUBSCRIPTION.is_active()
    ):
        fraud_result.status = models.FraudStatus.SUBSCRIPTION_ON_HOLD
    repository.save(fraud_result)

    return fraud_result


def validate_id_piece_number_format_fraud_item(id_piece_number: str) -> models.FraudItem:
    if not id_piece_number or not id_piece_number.strip():
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail="Le numéro de la pièce d'identité est vide",
            reason_code=models.FraudReasonCode.EMPTY_ID_PIECE_NUMBER,
        )

    regexp = "|".join(
        (
            r"(^\d{18}$)",  # ID Algérienne
            r"(^[\w]{8,12}|[\s\w]{14}$)",  # ID Europeene ID Française
            r"(^\w{1}\d{6}$)",  # ID Tunisienne
            r"(^\w{1}\ *\d{8}$)",  # ID Turque
            r"(^\w{2}\ *\d{7}$)",  # Ancienne ID Italienne
            r"(^\d{3}\-\d{7}\-\d{2}$)",  # ID Belge
            r"(^\d{7}$)",  # ID Congolaise, Camerounaise, Mauricienne
        )
    )

    if not re.fullmatch(
        regexp,
        id_piece_number,
    ):
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail="Le format du numéro de la pièce d'identité n'est pas valide",
            reason_code=models.FraudReasonCode.INVALID_ID_PIECE_NUMBER,
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="Le numéro de pièce d'identité est valide")


def _duplicate_user_fraud_item(
    first_name: str, last_name: str, birth_date: datetime.date, excluded_user_id: int
) -> models.FraudItem:
    duplicate_user = users_models.User.query.filter(
        matching(users_models.User.firstName, first_name)
        & (matching(users_models.User.lastName, last_name))
        & (sqlalchemy.func.DATE(users_models.User.dateOfBirth) == birth_date)
        & (users_models.User.is_beneficiary == True)
        & (users_models.User.id != excluded_user_id)
    ).first()

    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"Duplicat de l'utilisateur {duplicate_user.id}" if duplicate_user else "Utilisateur non dupliqué",
        reason_code=models.FraudReasonCode.DUPLICATE_USER if duplicate_user else None,
    )


def _duplicate_id_piece_number_fraud_item(user: users_models.User, document_id_number: str) -> models.FraudItem:
    duplicate_user = users_models.User.query.filter(
        users_models.User.id != user.id, users_models.User.idPieceNumber == document_id_number
    ).first()
    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"Le n° de cni {document_id_number} est déjà pris par l'utilisateur {duplicate_user.id}"
        if duplicate_user
        else "Le numéro de CNI n'est pas déjà utilisé",
        reason_code=models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER if duplicate_user else None,
    )


def _duplicate_ine_hash_fraud_item(ine_hash: str, excluded_user_id: int) -> models.FraudItem:
    duplicate_user = users_models.User.query.filter(
        users_models.User.ineHash == ine_hash, users_models.User.id != excluded_user_id
    ).first()
    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"L'INE {ine_hash} est déjà pris par l'utilisateur {duplicate_user.id}"
        if duplicate_user
        else "L'INE est OK",
        reason_code=models.FraudReasonCode.DUPLICATE_INE if duplicate_user else None,
    )


def _whitelisted_ine_fraud_item(ine_hash: str) -> models.FraudItem:
    is_ine_whitelisted = db.session.query(models.IneHashWhitelist.query.filter_by(ine_hash=ine_hash).exists()).scalar()

    return models.FraudItem(
        # TODO: ask if it is considered as KO or SUSPICIOUS
        status=models.FraudStatus.OK if is_ine_whitelisted else models.FraudStatus.SUSPICIOUS,
        detail=f"L'INE {ine_hash} n'est pas whitelisté" if not is_ine_whitelisted else "L'INE est whitelisté",
        reason_code=models.FraudReasonCode.INE_NOT_WHITELISTED if not is_ine_whitelisted else None,
    )


def _check_user_has_no_active_deposit(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> models.FraudItem:
    if user.has_active_deposit:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail=(
                "L’utilisateur est déjà bénéfiaire, avec un portefeuille non expiré. "
                f"Il ne peut pas prétendre au pass culture {'15-17 ans' if eligibility == users_models.EligibilityType.UNDERAGE else '18 ans'}"
            ),
            reason_code=models.FraudReasonCode.ALREADY_HAS_ACTIVE_DEPOSIT,
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="L'utilisateur n'a pas déjà un deposit actif")


def _check_user_not_already_beneficiary(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> models.FraudItem:
    if not user.is_eligible_for_beneficiary_upgrade(eligibility):
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail=(
                f"L’utilisateur est déjà bénéfiaire du pass {eligibility.name}"
                if eligibility
                else "L'utilisateur n'est pas éligible"
            ),
            reason_code=models.FraudReasonCode.ALREADY_BENEFICIARY,
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="L'utilisateur n'est pas déjà bénéficaire")


def _check_user_email_is_validated(user: users_models.User) -> models.FraudItem:
    if not user.isEmailValidated:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail="L'email de l'utilisateur n'est pas validé",
            reason_code=models.FraudReasonCode.EMAIL_NOT_VALIDATED,
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="L'email est validé")


def _check_user_phone_is_validated(user: users_models.User) -> models.FraudItem:
    if FeatureToggle.FORCE_PHONE_VALIDATION.is_active() and not user.is_phone_validated:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail="Le n° de téléphone de l'utilisateur n'est pas validé",
            reason_code=models.FraudReasonCode.PHONE_NOT_VALIDATED,
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="Le numéro de téléphone est validé")


def _id_check_fraud_items(content: models.JouveContent) -> list[models.FraudItem]:
    if not FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS.is_active():
        return []

    fraud_items = []
    fraud_items.append(
        _get_boolean_id_fraud_item(
            content.birthLocationCtrl, "birthLocationCtrl", models.FraudReasonCode.ID_CHECK_INVALID, False
        )
    )
    fraud_items.append(
        _get_boolean_id_fraud_item(
            content.bodyBirthDateCtrl, "bodyBirthDateCtrl", models.FraudReasonCode.ID_CHECK_INVALID, False
        )
    )
    fraud_items.append(
        _get_boolean_id_fraud_item(content.bodyNameCtrl, "bodyNameCtrl", models.FraudReasonCode.ID_CHECK_INVALID, False)
    )
    fraud_items.append(
        _get_boolean_id_fraud_item(
            content.bodyPieceNumberCtrl, "bodyPieceNumberCtrl", models.FraudReasonCode.ID_CHECK_INVALID, False
        )
    )

    fraud_items.append(
        _get_threshold_id_fraud_item(
            content.bodyBirthDateLevel, "bodyBirthDateLevel", 100, models.FraudReasonCode.ID_CHECK_INVALID, False
        )
    )
    fraud_items.append(
        _get_threshold_id_fraud_item(
            content.bodyNameLevel, "bodyNameLevel", 50, models.FraudReasonCode.ID_CHECK_INVALID, False
        )
    )
    fraud_items.append(
        _get_threshold_id_fraud_item(
            content.bodyPieceNumberLevel, "bodyPieceNumberLevel", 50, models.FraudReasonCode.ID_CHECK_INVALID, False
        )
    )

    return fraud_items


def _get_boolean_id_fraud_item(
    value: typing.Optional[str], key: str, fail_reason: models.FraudReasonCode, is_strict_ko: bool
) -> models.FraudItem:
    # TODO: move those functions when using fraud v2 journey only
    item = jouve_backend.get_boolean_fraud_detection_item(value, key)

    if item.valid:
        status = models.FraudStatus.OK
    elif is_strict_ko:
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    return models.FraudItem(
        status=status,
        detail=f"Le champ {key} est {value}",
        reason_code=None if status == models.FraudStatus.OK else fail_reason,
    )


def _get_threshold_id_fraud_item(
    value: typing.Optional[int], key: str, threshold: int, fail_reason: models.FraudReasonCode, is_strict_ko: bool
) -> models.FraudItem:
    # TODO: move those functions when using fraud v2 journey only
    item = jouve_backend.get_threshold_fraud_detection_item(value, key, threshold)
    if item.valid:
        status = models.FraudStatus.OK
    elif is_strict_ko:
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    return models.FraudItem(
        status=status,
        detail=f"Le champ {key} a le score {value} (minimum {threshold})",
        reason_code=None if status == models.FraudStatus.OK else fail_reason,
    )


def _underage_user_fraud_item(birth_date: datetime.date) -> models.FraudItem:
    age = users_utils.get_age_from_birth_date(birth_date)
    if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
        return models.FraudItem(
            status=models.FraudStatus.OK,
            detail=f"L'age de l'utilisateur est valide ({age} ans).",
        )
    return models.FraudItem(
        status=models.FraudStatus.KO,
        detail=f"L'age de l'utilisateur est invalide ({age} ans). Il devrait être parmi {constants.ELIGIBILITY_UNDERAGE_RANGE}",
        reason_code=models.FraudReasonCode.AGE_NOT_VALID,
    )


def on_user_profiling_result(
    user: users_models.User, profiling_infos: models.UserProfilingFraudData
) -> models.BeneficiaryFraudCheck:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.USER_PROFILING,
        thirdPartyId=profiling_infos.session_id,
        resultContent=profiling_infos,
    )
    repository.save(fraud_check)
    on_user_profiling_check_result(user, profiling_infos)
    return fraud_check


def on_user_profiling_check_result(
    user: users_models.User,
    tmx_content: models.UserProfilingFraudData,
) -> None:
    risk_rating = tmx_content.risk_rating
    user_profiling_status = USER_PROFILING_RISK_MAPPING[risk_rating]
    if not user_profiling_status == models.FraudStatus.OK:
        user.validate_profiling_failed()
        upsert_fraud_result(
            user, user_profiling_status, user.eligibility, f"threat-metrix risk rating is {risk_rating.value}"
        )

        from pcapi.core.subscription import messages as subscription_messages

        subscription_messages.on_user_subscription_journey_stopped(user)
    else:
        user.validate_profiling()

    repository.save(user)


def get_source_data(user: users_models.User) -> pydantic.BaseModel:
    mapped_class = {models.FraudCheckType.DMS: models.DMSContent, models.FraudCheckType.JOUVE: models.JouveContent}
    fraud_check_type = (
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.userId == user.id,
            models.BeneficiaryFraudCheck.type.in_([models.FraudCheckType.JOUVE, models.FraudCheckType.DMS]),
        )
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )
    return mapped_class[fraud_check_type.type](**fraud_check_type.resultContent)


def upsert_fraud_result(
    user: users_models.User,
    status: models.FraudStatus,
    eligibilityType: typing.Optional[users_models.EligibilityType],
    reason: str = None,
) -> models.BeneficiaryFraudResult:
    """
    If the user has no fraud result: create one fraud result with status and the given reason.
    If it already has one: append the reason to the already recorded ones.
    """
    if not eligibilityType:
        eligibilityType = users_models.EligibilityType.AGE18
    reason = reason or ""
    if status != models.FraudStatus.OK and not reason:
        raise ValueError(f"a reason should be provided when setting fraud result to {status.value}")

    fraud_result = fraud_repository.get_current_beneficiary_fraud_result(user, eligibilityType)

    if not fraud_result:
        fraud_result = models.BeneficiaryFraudResult(
            user=user, status=status, reason=reason, eligibilityType=eligibilityType
        )
    else:
        fraud_result.status = status
        # if this function is called twice (or more) in a row with the same
        # reason, do not update the reason column with the same reason repeated
        # over and over. It makes the reason less readable and therefore less
        # useful.
        last_reason = fraud_result.reason.split(FRAUD_RESULT_REASON_SEPARATOR)[-1].strip() if fraud_result else None
        if last_reason != reason:
            fraud_result.reason = f"{fraud_result.reason} {FRAUD_RESULT_REASON_SEPARATOR} {reason}"

    repository.save(fraud_result)
    return fraud_result


def create_internal_review_fraud_check(
    user: users_models.User, fraud_check_data: models.InternalReviewFraudData
) -> models.BeneficiaryFraudCheck:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.INTERNAL_REVIEW,
        thirdPartyId=f"PC-{user.id}",
        resultContent=fraud_check_data,
    )

    repository.save(fraud_check)
    return fraud_check


def handle_phone_already_exists(user: users_models.User, phone_number: str) -> models.BeneficiaryFraudCheck:
    orig_user_id = (
        users_models.User.query.filter(
            users_models.User.phoneNumber == phone_number, users_models.User.is_phone_validated
        )
        .one()
        .id
    )
    reason = f"Le numéro est déjà utilisé par l'utilisateur {orig_user_id}"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.PHONE_ALREADY_EXISTS, message=reason, phone_number=phone_number
    )

    return create_internal_review_fraud_check(user, fraud_check_data)


def handle_blacklisted_sms_recipient(user: users_models.User, phone_number: str) -> models.BeneficiaryFraudCheck:
    reason = "Le numéro saisi est interdit"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.BLACKLISTED_PHONE_NUMBER, message=reason, phone_number=phone_number
    )

    return create_internal_review_fraud_check(user, fraud_check_data)


def handle_sms_sending_limit_reached(user: users_models.User) -> models.BeneficiaryFraudResult:
    reason = "Le nombre maximum de sms envoyés est atteint"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.SMS_SENDING_LIMIT_REACHED,
        message=reason,
        phone_number=user.phoneNumber,
    )

    create_internal_review_fraud_check(user, fraud_check_data)
    return upsert_fraud_result(user, models.FraudStatus.SUSPICIOUS, user.eligibility, reason)


def handle_phone_validation_attempts_limit_reached(
    user: users_models.User, attempts_count: int
) -> models.BeneficiaryFraudResult:
    reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED,
        message=reason,
        phone_number=user.phoneNumber,
    )

    create_internal_review_fraud_check(user, fraud_check_data)
    return upsert_fraud_result(user, models.FraudStatus.SUSPICIOUS, user.eligibility, reason)


def handle_document_validation_error(email: str, code: str) -> None:
    user = users_models.User.query.filter(users_models.User.email == email).one_or_none()
    if user:
        fraud_check_data = models.InternalReviewFraudData(
            source=models.InternalReviewSource.DOCUMENT_VALIDATION_ERROR,
            message=f"Erreur de lecture du document : {code}",
        )
        create_internal_review_fraud_check(user, fraud_check_data)
    else:
        logger.warning("fraud internal validation : Cannot find user with email %s", email)


def validate_frauds(
    user: users_models.User,
    fraud_items: list[models.FraudItem],
    fraud_check: models.BeneficiaryFraudCheck,
    eligibilityType: users_models.EligibilityType,
) -> models.BeneficiaryFraudResult:
    if all(fraud_item.status == models.FraudStatus.OK for fraud_item in fraud_items):
        status = models.FraudStatus.OK
        fraud_check_status = models.FraudCheckStatus.OK
    elif any(fraud_item.status == models.FraudStatus.KO for fraud_item in fraud_items):
        status = models.FraudStatus.KO
        fraud_check_status = models.FraudCheckStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS
        fraud_check_status = models.FraudCheckStatus.SUSPICIOUS

    reason = f" {FRAUD_RESULT_REASON_SEPARATOR} ".join(
        fraud_item.detail for fraud_item in fraud_items if fraud_item.status != models.FraudStatus.OK
    )
    reason_codes = [
        fraud_item.reason_code
        for fraud_item in fraud_items
        if fraud_item.status != models.FraudStatus.OK and fraud_item.reason_code is not None
    ]

    fraud_check.status = fraud_check_status
    fraud_check.reason = reason
    fraud_check.reasonCodes = reason_codes
    repository.save(fraud_check)

    fraud_result = update_or_create_fraud_result(user, status, reason, reason_codes, eligibilityType)

    return fraud_result


def update_or_create_fraud_result(
    user: users_models.User,
    status: models.FraudStatus,
    reason: str,
    reason_codes: list[models.FraudReasonCode],
    eligibility_type: users_models.EligibilityType,
):
    existing_fraud_result = fraud_repository.get_current_beneficiary_fraud_result(user, eligibility_type)
    if existing_fraud_result:
        fraud_result = existing_fraud_result

        if fraud_result.status == models.FraudStatus.OK and status != models.FraudStatus.OK:
            raise BeneficiaryFraudResultCannotBeDowngraded()

        fraud_result.status = status
    else:
        fraud_result = models.BeneficiaryFraudResult(user=user, status=status, eligibilityType=eligibility_type)
    fraud_result.reason = reason
    fraud_result.reason_codes = reason_codes
    return fraud_result


def has_user_performed_identity_check(user: users_models.User) -> bool:
    return db.session.query(
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.status.is_distinct_from(models.FraudCheckStatus.CANCELED),
            models.BeneficiaryFraudCheck.type.in_(models.IDENTITY_CHECK_TYPES),
        ).exists()
    ).scalar()


def has_user_performed_ubble_check(user: users_models.User) -> bool:
    """
    Look for any Ubble identification already started, processed or not, but not aborted.
    There should not be more than one result in the database (later this function can count if limit is greater than 1).
    """
    return db.session.query(
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.status.is_distinct_from(models.FraudCheckStatus.CANCELED),
            models.BeneficiaryFraudCheck.type == models.FraudCheckType.UBBLE,
        ).exists()
    ).scalar()


def is_risky_user_profile(user: users_models.User) -> bool:
    user_profiling = (
        models.BeneficiaryFraudCheck.query.filter(models.BeneficiaryFraudCheck.user == user)
        .filter(models.BeneficiaryFraudCheck.type == models.FraudCheckType.USER_PROFILING)
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )

    if user_profiling and user_profiling.source_data().risk_rating == models.UserProfilingRiskRating.HIGH:
        return True

    if not (user_profiling or FeatureToggle.ALLOW_EMPTY_USER_PROFILING.is_active()):
        # unprofiled user and forbidden empty profiling -> risky
        return True

    return False


def is_user_fraudster(user: users_models.User) -> bool:
    return any(
        beneficiary_fraud_result.status != models.FraudStatus.OK
        for beneficiary_fraud_result in user.beneficiaryFraudResults
    )


def start_fraud_check(
    user: users_models.User,
    application_id: str,
    source_data: typing.Union[models.DMSContent, ubble_models.UbbleIdentificationResponse] = None,
) -> models.BeneficiaryFraudCheck:

    source_type = models.FRAUD_CONTENT_MAPPING[type(source_data)]

    fraud_check = models.BeneficiaryFraudCheck.query.filter(
        models.BeneficiaryFraudCheck.user == user,
        models.BeneficiaryFraudCheck.type == source_type,
        models.BeneficiaryFraudCheck.thirdPartyId == application_id,
    ).one_or_none()
    if fraud_check:
        raise exceptions.ApplicationValidationAlreadyStarted()

    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=source_type,
        thirdPartyId=application_id,
        resultContent=source_data.dict(),
        status=models.FraudCheckStatus.PENDING,
    )

    repository.save(fraud_check)

    return fraud_check


def mark_fraud_check_failed(
    user: users_models.User,
    application_id: str,
    source_data: typing.Union[models.DMSContent, ubble_models.UbbleIdentificationResponse],
    reasons: list[models.FraudItem],
) -> None:
    source_type = models.FRAUD_CONTENT_MAPPING[type(source_data)]
    fraud_check = models.BeneficiaryFraudCheck.query.filter(
        models.BeneficiaryFraudCheck.user == user,
        models.BeneficiaryFraudCheck.type == source_type,
        models.BeneficiaryFraudCheck.thirdPartyId == application_id,
        ~models.BeneficiaryFraudCheck.status.in_([models.FraudCheckStatus.OK, models.FraudCheckStatus.KO]),
    ).one_or_none()

    if not fraud_check:
        fraud_check = models.BeneficiaryFraudCheck(
            user=user,
            type=source_type,
            thirdPartyId=application_id,
            resultContent=source_data.dict(),
            status=models.FraudCheckStatus.PENDING,
        )

    fraud_check.status = models.FraudCheckStatus.KO
    fraud_check.reasonCodes = reasons

    repository.save(fraud_check)
