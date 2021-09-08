import datetime
import logging
import re
from typing import Optional
from typing import Union

import sqlalchemy

from pcapi.connectors.beneficiaries import jouve_backend
from pcapi.core.users.models import User
from pcapi.models.db import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.user_queries import matching

from . import models


logger = logging.getLogger(__name__)

FRAUD_RESULT_REASON_SEPARATOR = ";"


def on_jouve_result(user: User, jouve_content: models.JouveContent):
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


def on_dms_fraud_check(
    user: User,
    dms_content: models.DMSContent,
) -> None:

    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.DMS,
        thirdPartyId=str(dms_content.application_id),
        resultContent=dms_content,
    )

    db.session.add(fraud_check)
    db.session.commit()
    on_identity_fraud_check_result(user, fraud_check)


def admin_update_identity_fraud_check_result(
    user: User, id_piece_number: str
) -> Union[models.BeneficiaryFraudCheck, None]:
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


def jouve_fraud_checks(beneficiary_fraud_check: models.BeneficiaryFraudCheck) -> list[models.FraudItem]:
    jouve_content = models.JouveContent(**beneficiary_fraud_check.resultContent)

    fraud_items = []
    fraud_items.append(
        _duplicate_user_fraud_item(
            first_name=jouve_content.firstName,
            last_name=jouve_content.lastName,
            birth_date=jouve_content.birthDateTxt,
        )
    )

    fraud_items.append(_validate_id_piece_number_format_fraud_item(jouve_content.bodyPieceNumber))
    fraud_items.append(_duplicate_id_piece_number_fraud_item(jouve_content.bodyPieceNumber))
    fraud_items.extend(_id_check_fraud_items(jouve_content))
    return fraud_items


def dms_fraud_checks(beneficiary_fraud_check: models.BeneficiaryFraudCheck) -> list[models.FraudItem]:
    dms_content = models.DMSContent(**beneficiary_fraud_check.resultContent)

    fraud_items = []
    fraud_items.append(
        _duplicate_user_fraud_item(
            first_name=dms_content.first_name,
            last_name=dms_content.last_name,
            birth_date=dms_content.birth_date,
        )
    )
    fraud_items.append(_duplicate_id_piece_number_fraud_item(dms_content.id_piece_number))
    return fraud_items


def on_identity_fraud_check_result(
    user: User,
    beneficiary_fraud_check: models.BeneficiaryFraudCheck,
) -> models.BeneficiaryFraudResult:
    fraud_items: list[models.FraudItem] = []

    fraud_items.append(_check_user_already_beneficiary(user))
    fraud_items.append(_check_user_email_is_validated(user))
    fraud_items.append(_check_user_phone_is_validated(user))

    if beneficiary_fraud_check.type == models.FraudCheckType.JOUVE:
        fraud_items += jouve_fraud_checks(beneficiary_fraud_check)
    elif beneficiary_fraud_check.type == models.FraudCheckType.DMS:
        fraud_items += dms_fraud_checks(beneficiary_fraud_check)

    fraud_result = validate_frauds(user, fraud_items)
    repository.save(fraud_result)
    return fraud_result


def _validate_id_piece_number_format_fraud_item(id_piece_number):
    if not id_piece_number or not id_piece_number.strip():
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS, detail="Le numéro de la pièce d'identité est vide"
        )
    if not re.fullmatch(r"^\w{9,10}|\w{12}$", id_piece_number):
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS, detail="Le format du numéro de la pièce d'identité n'est pas valide"
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail=None)


def _duplicate_user_fraud_item(first_name: str, last_name: str, birth_date: datetime.date) -> models.FraudItem:
    duplicate_user = User.query.filter(
        matching(User.firstName, first_name)
        & (matching(User.lastName, last_name))
        & (sqlalchemy.func.DATE(User.dateOfBirth) == birth_date)
        & (User.isBeneficiary == True)
    ).first()

    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"Duplicat de l'utilisateur {duplicate_user.id}" if duplicate_user else None,
    )


def _duplicate_id_piece_number_fraud_item(document_id_number: str) -> models.FraudItem:
    duplicate_user = User.query.filter(User.idPieceNumber == document_id_number).first()
    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"Le n° de cni {document_id_number} est déjà pris par l'utilisateur {duplicate_user.id}"
        if duplicate_user
        else None,
    )


def _check_user_already_beneficiary(user: User) -> models.FraudItem:
    if user.isBeneficiary:
        return models.FraudItem(status=models.FraudStatus.KO, detail="L'utilisateur est déjà bénéficiaire")
    return models.FraudItem(status=models.FraudStatus.OK, detail=None)


def _check_user_email_is_validated(user: User) -> models.FraudItem:
    if not user.isEmailValidated:
        return models.FraudItem(status=models.FraudStatus.KO, detail="L'email de l'utilisateur n'est pas validé")
    return models.FraudItem(status=models.FraudStatus.OK, detail=None)


def _check_user_phone_is_validated(user: User) -> models.FraudItem:
    if FeatureToggle.FORCE_PHONE_VALIDATION.is_active() and not user.is_phone_validated:
        return models.FraudItem(
            status=models.FraudStatus.KO, detail="Le n° de téléphone de l'utilisateur n'est pas validé"
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail=None)


def _id_check_fraud_items(content: models.JouveContent) -> list[models.FraudItem]:
    if not FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS.is_active():
        return []

    fraud_items = []
    fraud_items.append(_get_boolean_id_fraud_item(content.birthLocationCtrl, "birthLocationCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyBirthDateCtrl, "bodyBirthDateCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyNameCtrl, "bodyNameCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyPieceNumberCtrl, "bodyPieceNumberCtrl", False))

    fraud_items.append(_get_threshold_id_fraud_item(content.bodyBirthDateLevel, "bodyBirthDateLevel", 100, False))
    fraud_items.append(_get_threshold_id_fraud_item(content.bodyNameLevel, "bodyNameLevel", 50, False))
    fraud_items.append(_get_threshold_id_fraud_item(content.bodyPieceNumberLevel, "bodyPieceNumberLevel", 50, False))

    return fraud_items


def _get_boolean_id_fraud_item(value: Optional[str], key: str, is_strict_ko: bool) -> models.FraudItem:
    # TODO: move those functions when using fraud v2 journey only
    item = jouve_backend.get_boolean_fraud_detection_item(value, key)

    if item.valid:
        status = models.FraudStatus.OK
    elif is_strict_ko:
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    return models.FraudItem(status=status, detail=f"Le champ {key} est {value}")


def _get_threshold_id_fraud_item(
    value: Optional[int], key: str, threshold: int, is_strict_ko: bool
) -> models.FraudItem:
    # TODO: move those functions when using fraud v2 journey only
    item = jouve_backend.get_threshold_fraud_detection_item(value, key, threshold)
    if item.valid:
        status = models.FraudStatus.OK
    elif is_strict_ko:
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    return models.FraudItem(status=status, detail=f"Le champ {key} a le score {value} (minimum {threshold})")


def create_user_profiling_check(
    user: User, profiling_infos: models.UserProfilingFraudData
) -> models.BeneficiaryFraudCheck:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.USER_PROFILING,
        thirdPartyId=profiling_infos.session_id,
        resultContent=profiling_infos,
    )
    repository.save(fraud_check)
    return fraud_check


def get_source_data(user: User) -> models.JouveContent:
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


def upsert_suspicious_fraud_result(user: User, reason: str) -> models.BeneficiaryFraudResult:
    """
    If the user has no fraud result: create one suspicious fraud result with
    the given reason. If it already has one: update the result's reason.
    """
    fraud_result = models.BeneficiaryFraudResult.query.filter_by(userId=user.id).one_or_none()

    if not fraud_result:
        fraud_result = models.BeneficiaryFraudResult(user=user, status=models.FraudStatus.SUSPICIOUS, reason=reason)
    else:
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
    user: User, fraud_check_data: models.InternalReviewFraudData
) -> models.BeneficiaryFraudCheck:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.INTERNAL_REVIEW,
        thirdPartyId=f"PC-{user.id}",
        resultContent=fraud_check_data,
    )

    repository.save(fraud_check)
    return fraud_check


def handle_phone_already_exists(user: User, phone_number: str) -> models.BeneficiaryFraudCheck:
    orig_user_id = User.query.filter(User.phoneNumber == phone_number, User.is_phone_validated).one().id
    reason = f"Le numéro est déjà utilisé par l'utilisateur {orig_user_id}"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.PHONE_ALREADY_EXISTS, message=reason, phone_number=phone_number
    )

    return create_internal_review_fraud_check(user, fraud_check_data)


def handle_blacklisted_sms_recipient(user: User, phone_number: str) -> models.BeneficiaryFraudCheck:
    reason = "Le numéro saisi est interdit"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.BLACKLISTED_PHONE_NUMBER, message=reason, phone_number=phone_number
    )

    return create_internal_review_fraud_check(user, fraud_check_data)


def handle_sms_sending_limit_reached(user: User) -> models.BeneficiaryFraudResult:
    reason = "Le nombre maximum de sms envoyés est atteint"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.SMS_SENDING_LIMIT_REACHED,
        message=reason,
        phone_number=user.phoneNumber,
    )

    create_internal_review_fraud_check(user, fraud_check_data)
    return upsert_suspicious_fraud_result(user, reason)


def handle_phone_validation_attempts_limit_reached(user: User, attempts_count: int) -> models.BeneficiaryFraudResult:
    reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
    fraud_check_data = models.InternalReviewFraudData(
        source=models.InternalReviewSource.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED,
        message=reason,
        phone_number=user.phoneNumber,
    )

    create_internal_review_fraud_check(user, fraud_check_data)
    return upsert_suspicious_fraud_result(user, reason)


def handle_document_validation_error(email: str, code: str) -> None:
    user = User.query.filter(User.email == email).one_or_none()
    if user:
        fraud_check_data = models.InternalReviewFraudData(
            source=models.InternalReviewSource.DOCUMENT_VALIDATION_ERROR,
            message=f"Erreur de lecture du document : {code}",
        )
        create_internal_review_fraud_check(user, fraud_check_data)
    else:
        logger.warning("fraud internal validation : Cannot find user with email %s", email)


def validate_frauds(user: User, fraud_items: list[models.FraudItem]) -> models.BeneficiaryFraudResult:
    if all(fraud_item.status == models.FraudStatus.OK for fraud_item in fraud_items):
        status = models.FraudStatus.OK
    elif any(fraud_item.status == models.FraudStatus.KO for fraud_item in fraud_items):
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    if user.beneficiaryFraudResult:
        fraud_result = user.beneficiaryFraudResult
        # ensure we never overwrite a previously validated status
        if fraud_result.status != models.FraudStatus.OK:
            fraud_result.status = status
    else:
        fraud_result = models.BeneficiaryFraudResult(
            userId=user.id,
            status=status,
        )
    fraud_result.reason = f" {FRAUD_RESULT_REASON_SEPARATOR} ".join(
        fraud_item.detail for fraud_item in fraud_items if fraud_item.status != models.FraudStatus.OK
    )

    return fraud_result
