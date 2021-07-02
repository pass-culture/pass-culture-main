import logging
from typing import List
from typing import Optional

from sqlalchemy import func

from pcapi.core.users.models import User
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.user_queries import matching

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


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


def on_identity_fraud_check_result(user: User, beneficiary_fraud_check: models.BeneficiaryFraudCheck):
    if user.isBeneficiary:
        raise exceptions.UserAlreadyBeneficiary()
    if not user.isEmailValidated:
        raise exceptions.UserEmailNotValidated()
    if FeatureToggle.FORCE_PHONE_VALIDATION.is_active() and not user.is_phone_validated:
        raise exceptions.UserPhoneNotValidated()

    jouve_content = models.JouveContent(**beneficiary_fraud_check.resultContent)

    fraud_items = []

    fraud_items.append(_duplicate_user_fraud_item(jouve_content))
    fraud_items.append(_duplicate_id_piece_number_fraud_item(jouve_content))
    fraud_items.extend(_id_check_fraud_items(jouve_content))

    if all(fraud_item.status == models.FraudStatus.OK for fraud_item in fraud_items):
        status = models.FraudStatus.OK
    elif any(fraud_item.status == models.FraudStatus.KO for fraud_item in fraud_items):
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    fraud_result = models.BeneficiaryFraudResult(
        user=user,
        status=status,
        reason=" ; ".join(
            fraud_item.detail for fraud_item in fraud_items if fraud_item.status != models.FraudStatus.OK
        ),
    )
    repository.save(fraud_result)


def _duplicate_user_fraud_item(jouve_content: models.JouveContent) -> models.FraudItem:
    duplicate_user = User.query.filter(
        matching(User.firstName, jouve_content.firstName)
        & (matching(User.lastName, jouve_content.lastName))
        & (func.DATE(User.dateOfBirth) == jouve_content.birthDateTxt)
        & (User.isBeneficiary == True)
    ).first()

    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"Duplicat de l'utilisateur {duplicate_user.id}" if duplicate_user else None,
    )


def _duplicate_id_piece_number_fraud_item(jouve_content: models.JouveContent) -> models.FraudItem:
    duplicate_user = User.query.filter(User.idPieceNumber == jouve_content.bodyPieceNumber).first()
    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS if duplicate_user else models.FraudStatus.OK,
        detail=f"Le n° de cni {jouve_content.bodyPieceNumber} est déjà pris par l'utilisateur {duplicate_user.id}"
        if duplicate_user
        else None,
    )


def _id_check_fraud_items(content: models.JouveContent) -> List[models.FraudItem]:
    if not FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS.is_active():
        return []

    fraud_items = []

    fraud_items.append(_get_boolean_id_fraud_item(content.birthLocationCtrl, "birthLocationCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyBirthDateCtrl, "bodyBirthDateCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyFirstnameCtrl, "bodyFirstnameCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyNameCtrl, "bodyNameCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.bodyPieceNumberCtrl, "bodyPieceNumberCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.creatorCtrl, "creatorCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.initialNumberCtrl, "initialNumberCtrl", False))
    fraud_items.append(_get_boolean_id_fraud_item(content.initialSizeCtrl, "initialSizeCtrl", False))

    fraud_items.append(_get_threshold_id_fraud_item(content.bodyBirthDateLevel, "bodyBirthDateLevel", 100, False))
    fraud_items.append(_get_threshold_id_fraud_item(content.bodyNameLevel, "bodyNameLevel", 50, False))
    fraud_items.append(_get_threshold_id_fraud_item(content.bodyFirstnameLevel, "bodyFirstnameLevel", 50, False))
    fraud_items.append(_get_threshold_id_fraud_item(content.bodyPieceNumberLevel, "bodyPieceNumberLevel", 50, False))

    return fraud_items


def _get_boolean_id_fraud_item(value: Optional[str], key: str, is_strict_ko: bool) -> models.FraudItem:
    is_valid = value.upper() != "KO" if value else True
    if is_valid:
        status = models.FraudStatus.OK
    elif is_strict_ko:
        status = models.FraudStatus.KO
    else:
        status = models.FraudStatus.SUSPICIOUS

    return models.FraudItem(status=status, detail=f"Le champ {key} est {value}")


def _get_threshold_id_fraud_item(
    value: Optional[int], key: str, threshold: int, is_strict_ko: bool
) -> models.FraudItem:
    try:
        is_valid = int(value) >= threshold if value else True
    except ValueError:
        is_valid = True
    if is_valid:
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
    mapped_class = {models.FraudCheckType.JOUVE: models.JouveContent}
    fraud_check_type = (
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.userId == user.id,
            models.BeneficiaryFraudCheck.type.in_([models.FraudCheckType.JOUVE]),
        )
        .order_by(models.BeneficiaryFraudCheck.dateCreated.desc())
        .first()
    )
    return mapped_class[fraud_check_type.type](**fraud_check_type.resultContent)
