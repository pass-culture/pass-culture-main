import datetime
import itertools
import logging
import re

import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.utils as fraud_utils
import pcapi.core.mails.transactional as transaction_mails
from pcapi import settings
from pcapi.core.fraud import exceptions as fraud_exceptions
from pcapi.core.fraud import repository as fraud_repository
from pcapi.core.mails.transactional.users import fraud_emails
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import api as users_api
from pcapi.core.users import constants
from pcapi.core.users import eligibility_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.models.feature import DisabledFeatureError
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.user_queries import matching
from pcapi.utils.email import anonymize_email

from . import models
from .common import models as common_models
from .ubble import api as ubble_api


logger = logging.getLogger(__name__)

FRAUD_RESULT_REASON_SEPARATOR = ";"


class FraudCheckError(fraud_exceptions.FraudException):
    pass


class EligibilityError(fraud_exceptions.FraudException):
    pass


class DuplicateIdPieceNumber(fraud_exceptions.FraudException):
    def __init__(self, id_piece_number: str, duplicate_user_id: int) -> None:
        self.id_piece_number = id_piece_number
        self.duplicate_user_id = duplicate_user_id
        super().__init__()


class DuplicateIneHash(fraud_exceptions.FraudException):
    def __init__(self, ine_hash: str, duplicate_user_id: int) -> None:
        self.ine_hash = ine_hash
        self.duplicate_user_id = duplicate_user_id
        super().__init__()


def on_educonnect_result(
    user: users_models.User, educonnect_content: models.EduconnectContent
) -> models.BeneficiaryFraudCheck:
    fraud_check = subscription_api.initialize_identity_fraud_check(
        eligibility_type=educonnect_content.get_eligibility_type_at_registration(),
        fraud_check_type=models.FraudCheckType.EDUCONNECT,
        identity_content=educonnect_content,
        third_party_id=str(educonnect_content.educonnect_id),
        user=user,
    )
    on_identity_fraud_check_result(user, fraud_check)
    repository.save(fraud_check)
    return fraud_check


def on_dms_fraud_result(user: users_models.User, fraud_check: models.BeneficiaryFraudCheck) -> None:
    on_identity_fraud_check_result(user, fraud_check)


def educonnect_fraud_checks(
    user: users_models.User, educonnect_content: models.EduconnectContent
) -> list[models.FraudItem]:
    fraud_items = []
    fraud_items.append(_underage_user_fraud_item(educonnect_content.get_birth_date(), user.departementCode))
    fraud_items.append(_duplicate_ine_hash_fraud_item(educonnect_content.ine_hash, user.id))

    return fraud_items


def dms_fraud_checks(user: users_models.User, content: models.DMSContent) -> list[models.FraudItem]:
    fraud_items = []
    id_piece_number = content.get_id_piece_number()
    fraud_items.append(validate_id_piece_number_format_fraud_item(id_piece_number, content.procedure_number))
    if id_piece_number:
        fraud_items.append(duplicate_id_piece_number_fraud_item(user, id_piece_number))
    return fraud_items


def on_identity_fraud_check_result(
    user: users_models.User,
    beneficiary_fraud_check: models.BeneficiaryFraudCheck,
) -> list[models.FraudItem]:
    fraud_items: list[models.FraudItem] = []
    identity_content: common_models.IdentityCheckContent = beneficiary_fraud_check.source_data()

    if beneficiary_fraud_check.type == models.FraudCheckType.UBBLE:
        assert isinstance(identity_content, models.UbbleContent)
        fraud_items += ubble_api.ubble_fraud_checks(user, identity_content)

    elif beneficiary_fraud_check.type == models.FraudCheckType.DMS:
        assert isinstance(identity_content, models.DMSContent)
        fraud_items += dms_fraud_checks(user, identity_content)

    elif beneficiary_fraud_check.type == models.FraudCheckType.EDUCONNECT:
        assert isinstance(identity_content, models.EduconnectContent)
        fraud_items += educonnect_fraud_checks(user, identity_content)

    else:
        raise ValueError("The fraud_check type is not known")

    content_first_name = identity_content.get_first_name()
    content_last_name = identity_content.get_last_name()
    content_birth_date = identity_content.get_birth_date()

    # Check for duplicate only when Id Check returns identity details
    if content_first_name and content_last_name and content_birth_date:
        fraud_items.append(
            _duplicate_user_fraud_item(
                first_name=content_first_name,
                last_name=content_last_name,
                married_name=identity_content.get_married_name(),
                birth_date=content_birth_date,
                excluded_user_id=user.id,
            )
        )
        fraud_items.append(_check_user_names_valid(content_first_name, content_last_name))
        fraud_items.append(_check_user_eligibility(user, beneficiary_fraud_check.eligibilityType))
    else:
        fraud_items.append(_missing_data_fraud_item())

    fraud_items.append(_check_user_email_is_validated(user))

    return validate_frauds(fraud_items, beneficiary_fraud_check)


def validate_id_piece_number_format_fraud_item(
    id_piece_number: str | None, procedure_number: int | None = None
) -> models.FraudItem:
    if procedure_number == settings.DMS_ENROLLMENT_PROCEDURE_ID_ET:  # Pièce d'identité étrangère
        return models.FraudItem(status=models.FraudStatus.OK, detail="La pièce d'identité n'est pas française.")
    if not id_piece_number or not id_piece_number.strip():
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail="Le numéro de la pièce d'identité est vide",
            reason_codes=[models.FraudReasonCode.EMPTY_ID_PIECE_NUMBER],
        )

    # Outil de test de regex: https://regex101.com/ FTW
    # Doc des formats acceptés: https://www.notion.so/passcultureapp/Tableau-des-ID-trang-res-sur-FA-440ab8cbb31d4ae9a16debe3eb5aab24
    regexp = "|".join(
        (
            # --- ID Européenne (dont française) ---
            r"^[A-Z0-9]{12}$",
            # --- Nouvelle carte d'identité française ---
            r"^[A-Z0-9]{9}$",
            # --- Passeport Français ---
            r"^\d{2}[a-zA-Z]{2}\d{5}$",
        )
    )

    match = re.match(regexp, format_id_piece_number(id_piece_number))
    if not match:
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail="Le format du numéro de la pièce d'identité n'est pas valide",
            reason_codes=[models.FraudReasonCode.INVALID_ID_PIECE_NUMBER],
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="Le numéro de pièce d'identité est valide")


def _duplicate_user_fraud_item(
    first_name: str,
    last_name: str,
    married_name: str | None,
    birth_date: datetime.date,
    excluded_user_id: int,
) -> models.FraudItem:
    duplicate_user = find_duplicate_beneficiary(first_name, last_name, married_name, birth_date, excluded_user_id)

    if duplicate_user:
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail=f"Duplicat de l'utilisateur {duplicate_user.id}",
            reason_codes=[models.FraudReasonCode.DUPLICATE_USER],
            extra_data={"duplicate_id": duplicate_user.id},
        )

    return models.FraudItem(status=models.FraudStatus.OK, detail="Utilisateur non dupliqué")


def _missing_data_fraud_item() -> models.FraudItem:
    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS,
        reason_codes=[models.FraudReasonCode.MISSING_REQUIRED_DATA],
        detail="Des informations obligatoires (prénom, nom ou date de naissance) sont absentes du dossier",
    )


def find_duplicate_beneficiary(
    first_name: str,
    last_name: str,
    married_name: str | None,
    birth_date: datetime.date,
    excluded_user_id: int,
) -> users_models.User | None:
    base_query = db.session.query(users_models.User).filter(
        (users_models.User.validatedBirthDate == birth_date)
        & matching(users_models.User.firstName, first_name)
        & (users_models.User.is_beneficiary)
        & (users_models.User.id != excluded_user_id)
    )

    duplicate_last_name_vs_last_name = base_query.filter(matching(users_models.User.lastName, last_name)).first()

    if duplicate_last_name_vs_last_name:
        return duplicate_last_name_vs_last_name

    duplicate_last_name_vs_married_name = base_query.filter(matching(users_models.User.married_name, last_name)).first()

    if duplicate_last_name_vs_married_name:
        return duplicate_last_name_vs_married_name

    if married_name:
        return base_query.filter(matching(users_models.User.lastName, married_name)).first()

    return None


def duplicate_id_piece_number_fraud_item(user: users_models.User, id_piece_number: str) -> models.FraudItem:
    duplicate_user = find_duplicate_id_piece_number_user(id_piece_number, user.id)

    if duplicate_user:
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail=f"La pièce d'identité n°{id_piece_number} est déjà prise par l'utilisateur {duplicate_user.id}",
            reason_codes=[models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER],
            extra_data={"duplicate_id": duplicate_user.id},
        )

    return models.FraudItem(status=models.FraudStatus.OK, detail="La pièce d'identité n'est pas déjà utilisée")


def format_id_piece_number(id_piece_number: str) -> str:
    return re.sub(r"[\W^_]", "", id_piece_number.upper())


def find_duplicate_id_piece_number_user(id_piece_number: str | None, excluded_user_id: int) -> users_models.User | None:
    if not id_piece_number:
        return None
    return (
        db.session.query(users_models.User)
        .filter(
            users_models.User.id != excluded_user_id,
            users_models.User.idPieceNumber.is_not(None),
            users_models.User.idPieceNumber == format_id_piece_number(id_piece_number),
        )
        .first()
    )


def _duplicate_ine_hash_fraud_item(ine_hash: str, excluded_user_id: int) -> models.FraudItem:
    duplicate_user = find_duplicate_ine_hash_user(ine_hash, excluded_user_id)

    if duplicate_user:
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail=f"L'INE {ine_hash} est déjà pris par l'utilisateur {duplicate_user.id}",
            reason_codes=[models.FraudReasonCode.DUPLICATE_INE],
        )

    return models.FraudItem(status=models.FraudStatus.OK, detail="L'INE n'est pas déjà pris")


def find_duplicate_ine_hash_user(ine_hash: str, excluded_user_id: int) -> users_models.User | None:
    return (
        db.session.query(users_models.User)
        .filter(users_models.User.id != excluded_user_id, users_models.User.ineHash == ine_hash)
        .first()
    )


def _check_user_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.FraudItem:
    if not eligibility:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail="L'âge indiqué dans le dossier indique que l'utilisateur n'est pas éligible",
            reason_codes=[models.FraudReasonCode.NOT_ELIGIBLE],
        )

    return models.FraudItem(
        status=models.FraudStatus.OK, detail="L'utilisateur est éligible à un nouveau statut bénéficiaire"
    )


def is_subscription_name_valid(name: str | None) -> bool:
    if settings.ENABLE_PERMISSIVE_NAME_VALIDATION:
        return True
    if not name:
        return False
    stripped_name = name.strip()
    try:
        fraud_utils.validate_name(stripped_name)
    except ValueError:
        return False

    return True


def _check_user_names_valid(first_name: str | None, last_name: str | None) -> models.FraudItem:
    incorrect_fields = None
    is_valid_first_name = is_subscription_name_valid(first_name)
    is_valid_last_name = is_subscription_name_valid(last_name)

    if not is_valid_first_name and not is_valid_last_name:
        incorrect_fields = "un prénom et un nom de famille"
    elif not is_valid_first_name:
        incorrect_fields = "un prénom"
    elif not is_valid_last_name:
        incorrect_fields = "un nom de famille"

    if incorrect_fields:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail=f"L'utilisateur a {incorrect_fields} avec des caractères invalides",
            reason_codes=[models.FraudReasonCode.NAME_INCORRECT],
        )
    return models.FraudItem(
        status=models.FraudStatus.OK, detail="L'utilisateur a un nom et prénom avec des caractères valides"
    )


def _check_user_email_is_validated(user: users_models.User) -> models.FraudItem:
    if not user.isEmailValidated:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail="L'email de l'utilisateur n'est pas validé",
            reason_codes=[models.FraudReasonCode.EMAIL_NOT_VALIDATED],
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="L'email est validé")


def _underage_user_fraud_item(birth_date: datetime.date, department_code: str | None = None) -> models.FraudItem:
    age = users_utils.get_age_from_birth_date(birth_date, department_code)
    if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
        return models.FraudItem(
            status=models.FraudStatus.OK,
            detail=f"L'âge de l'utilisateur est valide ({age} ans).",
        )
    return models.FraudItem(
        status=models.FraudStatus.KO,
        detail=f"L'âge de l'utilisateur est invalide ({age} ans). Il devrait être parmi {constants.ELIGIBILITY_UNDERAGE_RANGE}",
        reason_codes=[models.FraudReasonCode.AGE_NOT_VALID],
    )


def _create_failed_phone_validation_fraud_check(
    user: users_models.User,
    fraud_check_data: models.PhoneValidationFraudData,
    reason: str,
    reason_codes: list[models.FraudReasonCode],
) -> models.BeneficiaryFraudCheck:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        reason=reason,
        reasonCodes=reason_codes,
        type=models.FraudCheckType.PHONE_VALIDATION,
        thirdPartyId=f"PC-{user.id}",
        resultContent=fraud_check_data.dict(),
        eligibilityType=user.eligibility,
        status=models.FraudCheckStatus.KO,
    )

    repository.save(fraud_check)
    return fraud_check


def handle_phone_already_exists(user: users_models.User, phone_number: str) -> models.BeneficiaryFraudCheck:
    orig_user_id = (
        db.session.query(users_models.User)
        .filter(users_models.User.phoneNumber == phone_number, users_models.User.is_phone_validated)
        .one()
        .id
    )
    reason = f"Le numéro est déjà utilisé par l'utilisateur {orig_user_id}"
    reason_codes = [models.FraudReasonCode.PHONE_ALREADY_EXISTS]
    fraud_check_data = models.PhoneValidationFraudData(phone_number=phone_number)

    return _create_failed_phone_validation_fraud_check(user, fraud_check_data, reason, reason_codes)


def handle_blacklisted_sms_recipient(user: users_models.User, phone_number: str) -> models.BeneficiaryFraudCheck:
    reason = "Le numéro saisi est interdit"
    reason_codes = [models.FraudReasonCode.BLACKLISTED_PHONE_NUMBER]
    fraud_check_data = models.PhoneValidationFraudData(phone_number=phone_number)

    return _create_failed_phone_validation_fraud_check(user, fraud_check_data, reason, reason_codes)


def handle_invalid_country_code(user: users_models.User, phone_number: str) -> models.BeneficiaryFraudCheck:
    reason = "L'indicatif téléphonique est invalide"
    reason_codes = [models.FraudReasonCode.INVALID_PHONE_COUNTRY_CODE]
    fraud_check_data = models.PhoneValidationFraudData(phone_number=phone_number)

    return _create_failed_phone_validation_fraud_check(user, fraud_check_data, reason, reason_codes)


def handle_sms_sending_limit_reached(user: users_models.User) -> None:
    reason = "Le nombre maximum de sms envoyés est atteint"
    reason_codes = [models.FraudReasonCode.SMS_SENDING_LIMIT_REACHED]
    fraud_check_data = models.PhoneValidationFraudData(phone_number=user.phoneNumber)

    _create_failed_phone_validation_fraud_check(user, fraud_check_data, reason, reason_codes)


def handle_phone_validation_attempts_limit_reached(user: users_models.User, attempts_count: int) -> None:
    reason = f"Le nombre maximum de tentatives de validation est atteint: {attempts_count}"
    reason_codes = [models.FraudReasonCode.PHONE_VALIDATION_ATTEMPTS_LIMIT_REACHED]
    fraud_check_data = models.PhoneValidationFraudData(phone_number=user.phoneNumber)

    _create_failed_phone_validation_fraud_check(user, fraud_check_data, reason, reason_codes)


def _handle_duplicate(fraud_items: list[models.FraudItem], fraud_check: models.BeneficiaryFraudCheck) -> None:
    duplicate_beneficiary_id = next(
        (
            fraud_item.get_duplicate_beneficiary_id()
            for fraud_item in fraud_items
            if models.FraudReasonCode.DUPLICATE_USER in fraud_item.reason_codes
            or models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in fraud_item.reason_codes
        ),
        None,
    )
    if not duplicate_beneficiary_id:
        return

    user = fraud_check.user
    if not user.deposit or user.deposit.type != finance_models.DepositType.GRANT_15_17:
        return

    duplicate_beneficiary = db.session.get(users_models.User, duplicate_beneficiary_id)
    if not duplicate_beneficiary:
        return

    duplicate_had_underage_credit = any(
        deposit for deposit in duplicate_beneficiary.deposits if deposit.type == finance_models.DepositType.GRANT_15_17
    )
    if not duplicate_had_underage_credit:
        return

    users_api.suspend_account(
        user,
        reason=constants.SuspensionReason.FRAUD_SUSPICION,
        actor=None,
        comment="Compte automatiquement suspendu pour suspicion de doublon",
    )
    users_api.suspend_account(
        duplicate_beneficiary,
        reason=constants.SuspensionReason.FRAUD_SUSPICION,
        actor=None,
        comment="Compte automatiquement suspendu pour suspicion de doublon",
    )
    fraud_emails.send_duplicate_fraud_detection_mail(user, duplicate_beneficiary)


def validate_frauds(
    fraud_items: list[models.FraudItem],
    fraud_check: models.BeneficiaryFraudCheck,
) -> list[models.FraudItem]:
    if all(fraud_item.status == models.FraudStatus.OK for fraud_item in fraud_items):
        fraud_check_status = models.FraudCheckStatus.OK
    elif any(fraud_item.status == models.FraudStatus.KO for fraud_item in fraud_items):
        fraud_check_status = models.FraudCheckStatus.KO
    else:
        fraud_check_status = models.FraudCheckStatus.SUSPICIOUS

    reason = f" {FRAUD_RESULT_REASON_SEPARATOR} ".join(
        fraud_item.detail for fraud_item in fraud_items if fraud_item.status != models.FraudStatus.OK
    )
    reason_codes = set(
        itertools.chain.from_iterable(
            fraud_item.reason_codes for fraud_item in fraud_items if fraud_item.status != models.FraudStatus.OK
        )
    )

    _handle_duplicate(fraud_items, fraud_check)

    fraud_check.status = fraud_check_status
    fraud_check.reason = reason
    fraud_check.reasonCodes = list(reason_codes)
    repository.save(fraud_check)

    return fraud_items


def has_user_pending_identity_check(user: users_models.User) -> bool:
    return db.session.query(
        db.session.query(models.BeneficiaryFraudCheck)
        .filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.status == models.FraudCheckStatus.PENDING,
            models.BeneficiaryFraudCheck.type.in_(models.IDENTITY_CHECK_TYPES),
            models.BeneficiaryFraudCheck.eligibilityType == user.eligibility,
        )
        .exists()
    ).scalar()


def has_user_performed_identity_check(user: users_models.User) -> bool:
    if user.is_beneficiary and not eligibility_api.is_eligible_for_next_recredit_activation_steps(user):
        return True

    user_subscription_state = subscription_api.get_user_subscription_state(user)
    return user_subscription_state.fraud_status not in (
        subscription_models.SubscriptionItemStatus.TODO,
        subscription_models.SubscriptionItemStatus.VOID,
    )


def get_last_filled_identity_fraud_check(user: users_models.User) -> models.BeneficiaryFraudCheck | None:
    user_identity_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in models.IDENTITY_CHECK_TYPES
        and fraud_check.resultContent is not None
        and fraud_check.source_data().get_last_name() is not None
        and fraud_check.source_data().get_first_name() is not None
        and fraud_check.source_data().get_birth_date() is not None
    ]

    return (
        max(user_identity_fraud_checks, key=lambda fraud_check: fraud_check.dateCreated)
        if user_identity_fraud_checks
        else None
    )


def create_honor_statement_fraud_check(
    user: users_models.User, origin: str, eligibility_type: users_models.EligibilityType | None = None
) -> None:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.HONOR_STATEMENT,
        status=models.FraudCheckStatus.OK,
        reason=origin,
        thirdPartyId=f"internal_check_{user.id}",
        eligibilityType=eligibility_type if eligibility_type else user.eligibility,
    )
    db.session.add(fraud_check)
    db.session.commit()


def handle_ok_manual_review(
    user: users_models.User,
    _review: models.BeneficiaryFraudReview,
    eligibility: users_models.EligibilityType | None,
) -> None:
    fraud_check = get_last_filled_identity_fraud_check(user)
    if not fraud_check:
        raise FraudCheckError("Pas de vérification d'identité effectuée")

    source_data: common_models.IdentityCheckContent = fraud_check.source_data()
    id_piece_number = user.idPieceNumber or source_data.get_id_piece_number()
    try:
        _check_id_piece_number_unicity(user, id_piece_number)
        _check_ine_hash_unicity(user, source_data.get_ine_hash())
    except DuplicateIdPieceNumber as err:
        raise FraudCheckError(
            f"Le numéro de CNI {err.id_piece_number} est déjà utilisé par l'utilisateur {err.duplicate_user_id}"
        ) from err
    except DuplicateIneHash as err:
        raise FraudCheckError(
            f"Le numéro INE {err.ine_hash} est déjà utilisé par l'utilisateur {err.duplicate_user_id}"
        ) from err

    users_api.update_user_information_from_external_source(user, source_data, id_piece_number=id_piece_number)

    if eligibility is None:
        eligibility = eligibility_api.get_pre_decree_or_current_eligibility(user)
        if not eligibility:
            raise EligibilityError("Aucune éligibilité trouvée. Veuillez renseigner une éligibilité.")

    try:
        subscription_api.activate_beneficiary_for_eligibility(user, fraud_check.get_detailed_source(), eligibility)

    except subscription_exceptions.InvalidAgeException as err:
        err_msg = (
            "L'âge de l'utilisateur à l'inscription n'a pas pu être déterminé"
            if err.age is None
            else f"L'âge de l'utilisateur à l'inscription ({err.age} ans) est incompatible avec l'éligibilité choisie"
        )
        raise EligibilityError(err_msg) from err

    except subscription_exceptions.CannotUpgradeBeneficiaryRole as err:
        raise EligibilityError(f"L'utilisateur ne peut pas être promu au rôle {eligibility.value}") from err

    except finance_exceptions.UserHasAlreadyActiveDeposit as err:
        raise EligibilityError(
            f"L'utilisateur bénéficie déjà d'un crédit non expiré du type '{eligibility.value}'"
        ) from err

    except finance_exceptions.DepositTypeAlreadyGrantedException as err:
        raise EligibilityError("Un crédit identique a déjà été accordé à l'utilisateur") from err


def handle_dms_redirection_review(
    user: users_models.User,
    review: models.BeneficiaryFraudReview,
    _eligibility: users_models.EligibilityType | None,
) -> None:
    if review.reason is None:
        review.reason = "Redirigé vers DMS"
    else:
        review.reason += " ; Redirigé vers DMS"

    transaction_mails.send_subscription_document_error_email(user.email, models.FraudReasonCode.ID_CHECK_UNPROCESSABLE)


REVIEW_HANDLERS = {
    models.FraudReviewStatus.OK: handle_ok_manual_review,
    models.FraudReviewStatus.REDIRECTED_TO_DMS: handle_dms_redirection_review,
    models.FraudReviewStatus.KO: None,
}


def validate_beneficiary(
    user: users_models.User,
    reviewer: users_models.User,
    reason: str,
    review: models.FraudReviewStatus,
    reviewed_eligibility: users_models.EligibilityType | None,
) -> models.BeneficiaryFraudReview:
    if not FeatureToggle.BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS.is_active():
        raise DisabledFeatureError("Cannot validate beneficiary because the feature is disabled")

    review = models.BeneficiaryFraudReview(
        user=user,
        author=reviewer,
        reason=reason,
        review=review,
        eligibilityType=(
            user.eligibility if reviewed_eligibility is None else reviewed_eligibility
        ),  # needed condition to keep flask admin review behavior
    )

    if review.review is not None:
        handler = REVIEW_HANDLERS.get(models.FraudReviewStatus(review.review))
        if handler:
            handler(user, review, None if user.eligibility is None else reviewed_eligibility)

    repository.save(review)
    return review


def _check_id_piece_number_unicity(user: users_models.User, id_piece_number: str | None) -> None:
    if not id_piece_number:
        return

    duplicate_user = find_duplicate_id_piece_number_user(id_piece_number, user.id)

    if duplicate_user:
        raise DuplicateIdPieceNumber(id_piece_number, duplicate_user.id)


def _check_ine_hash_unicity(user: users_models.User, ine_hash: str | None) -> None:
    if not ine_hash:
        return

    duplicate_user = find_duplicate_ine_hash_user(ine_hash, user.id)

    if duplicate_user:
        raise DuplicateIneHash(ine_hash, duplicate_user.id)


def create_profile_completion_fraud_check(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
    fraud_check_content: models.ProfileCompletionContent,
) -> None:
    if fraud_repository.get_completed_profile_check(user, eligibility) is not None:
        logger.warning(
            "Profile completion fraud check for user already exists.",
            extra={"user_id": user.id},
        )
        return
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.PROFILE_COMPLETION,
        resultContent=fraud_check_content.dict(),
        status=models.FraudCheckStatus.OK,
        thirdPartyId=f"profile-completion-{user.id}",
        eligibilityType=eligibility,
        reason=fraud_check_content.origin,
    )
    repository.save(fraud_check)


def get_duplicate_beneficiary(fraud_check: models.BeneficiaryFraudCheck) -> users_models.User | None:
    identity_content = fraud_check.source_data()

    if not isinstance(identity_content, common_models.IdentityCheckContent):
        raise ValueError("Invalid fraud check identity content type")

    first_name = identity_content.get_first_name()
    last_name = identity_content.get_last_name()
    birth_date = identity_content.get_birth_date()

    if not first_name or not last_name or not birth_date:
        raise ValueError("Invalid fraud check identity data")

    return find_duplicate_beneficiary(
        first_name,
        last_name,
        identity_content.get_married_name(),
        birth_date,
        fraud_check.userId,
    )


def invalidate_fraud_check_for_duplicate_user(
    fraud_check: models.BeneficiaryFraudCheck, duplicate_user_id: int
) -> None:
    fraud_check.status = models.FraudCheckStatus.SUSPICIOUS
    if not fraud_check.reasonCodes:
        fraud_check.reasonCodes = []
    fraud_check.reasonCodes.append(models.FraudReasonCode.DUPLICATE_USER)
    fraud_check.reason = f"Fraud check invalidé: duplicat de l'utilisateur {duplicate_user_id}"

    repository.save(fraud_check)


def get_duplicate_beneficiary_anonymized_email(
    rejected_user: users_models.User,
    identity_content: common_models.IdentityCheckContent,
    duplicate_reason_code: models.FraudReasonCode,
) -> str | None:
    duplicate_beneficiary = None

    if duplicate_reason_code == models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER:
        duplicate_beneficiary = find_duplicate_id_piece_number_user(
            identity_content.get_id_piece_number(), rejected_user.id
        )
    elif duplicate_reason_code == models.FraudReasonCode.DUPLICATE_USER:
        first_name = identity_content.get_first_name()
        last_name = identity_content.get_last_name()
        birth_date = identity_content.get_birth_date()
        if first_name and last_name and birth_date:
            duplicate_beneficiary = find_duplicate_beneficiary(
                first_name,
                last_name,
                identity_content.get_married_name(),
                birth_date,
                rejected_user.id,
            )
    elif duplicate_reason_code == models.FraudReasonCode.DUPLICATE_INE:
        ine_hash = identity_content.get_ine_hash()
        if ine_hash:
            duplicate_beneficiary = find_duplicate_ine_hash_user(ine_hash, rejected_user.id)

    if not duplicate_beneficiary:
        logger.error(
            "No duplicate beneficiary found", extra={"user_id": rejected_user.id, "code": duplicate_reason_code}
        )
        return None

    return anonymize_email(duplicate_beneficiary.email)
