import datetime
import logging
import re
import typing

import sqlalchemy
from sqlalchemy.orm import Query

from pcapi import settings
from pcapi.core.fraud.utils import is_latin
import pcapi.core.mails.transactional as transaction_mails
from pcapi.core.payments import exceptions as payments_exceptions
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import api as users_api
from pcapi.core.users import constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.models.feature import DisabledFeatureError
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.user_queries import matching

from . import models
from .common.models import IdentityCheckContent
from .ubble import api as ubble_api


logger = logging.getLogger(__name__)

FRAUD_RESULT_REASON_SEPARATOR = ";"

USER_PROFILING_RISK_MAPPING = {
    models.UserProfilingRiskRating.TRUSTED: models.FraudStatus.OK,
    models.UserProfilingRiskRating.NEUTRAL: models.FraudStatus.OK,
    models.UserProfilingRiskRating.LOW: models.FraudStatus.OK,
    models.UserProfilingRiskRating.MEDIUM: models.FraudStatus.SUSPICIOUS,
    models.UserProfilingRiskRating.HIGH: models.FraudStatus.KO,
}

USER_PROFILING_FRAUD_CHECK_STATUS_RISK_MAPPING = {
    models.UserProfilingRiskRating.TRUSTED: models.FraudCheckStatus.OK,
    models.UserProfilingRiskRating.NEUTRAL: models.FraudCheckStatus.OK,
    models.UserProfilingRiskRating.LOW: models.FraudCheckStatus.OK,
    models.UserProfilingRiskRating.MEDIUM: models.FraudCheckStatus.SUSPICIOUS,
    models.UserProfilingRiskRating.HIGH: models.FraudCheckStatus.KO,
}


class FraudCheckError(Exception):
    pass


class EligibilityError(Exception):
    pass


class DuplicateIdPieceNumber(Exception):
    def __init__(self, id_piece_number: str, duplicate_user_id: int) -> None:
        self.id_piece_number = id_piece_number
        self.duplicate_user_id = duplicate_user_id
        super().__init__()


class DuplicateIneHash(Exception):
    def __init__(self, ine_hash: str, duplicate_user_id: int) -> None:
        self.ine_hash = ine_hash
        self.duplicate_user_id = duplicate_user_id
        super().__init__()


def on_educonnect_result(
    user: users_models.User, educonnect_content: models.EduconnectContent
) -> models.BeneficiaryFraudCheck:
    eligibility_type = educonnect_content.get_eligibility_type_at_registration()

    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.EDUCONNECT,
        thirdPartyId=str(educonnect_content.educonnect_id),
        resultContent=educonnect_content.dict(),
        eligibilityType=eligibility_type,
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
    fraud_items.append(_underage_user_fraud_item(educonnect_content.get_birth_date()))
    fraud_items.append(_duplicate_ine_hash_fraud_item(educonnect_content.ine_hash, user.id))

    return fraud_items


def dms_fraud_checks(user: users_models.User, content: models.DMSContent) -> list[models.FraudItem]:
    fraud_items = []
    id_piece_number = content.get_id_piece_number()
    fraud_items.append(validate_id_piece_number_format_fraud_item(id_piece_number))
    if id_piece_number:
        fraud_items.append(duplicate_id_piece_number_fraud_item(user, id_piece_number))
    return fraud_items


def on_identity_fraud_check_result(
    user: users_models.User,
    beneficiary_fraud_check: models.BeneficiaryFraudCheck,
) -> list[models.FraudItem]:
    fraud_items: list[models.FraudItem] = []
    identity_content: models.IdentityCheckContent = beneficiary_fraud_check.source_data()  # type: ignore [name-defined]

    if beneficiary_fraud_check.type == models.FraudCheckType.UBBLE:
        fraud_items += ubble_api.ubble_fraud_checks(user, identity_content)

    elif beneficiary_fraud_check.type == models.FraudCheckType.DMS:
        fraud_items += dms_fraud_checks(user, identity_content)

    elif beneficiary_fraud_check.type == models.FraudCheckType.EDUCONNECT:
        fraud_items += educonnect_fraud_checks(user, identity_content)

    else:
        raise Exception("The fraud_check type is not known")

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

    fraud_items.append(_check_user_has_no_active_deposit(user, beneficiary_fraud_check.eligibilityType))  # type: ignore [arg-type]
    fraud_items.append(_check_user_email_is_validated(user))

    return validate_frauds(fraud_items, beneficiary_fraud_check)


def validate_id_piece_number_format_fraud_item(id_piece_number: str | None) -> models.FraudItem:
    if not id_piece_number or not id_piece_number.strip():
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail="Le numéro de la pièce d'identité est vide",
            reason_code=models.FraudReasonCode.EMPTY_ID_PIECE_NUMBER,
        )

    # https://regex101.com/ FTW
    regexp = "|".join(
        (
            r"^\d{18}$",  # ID Algérienne
            r"^\w{8,12}$",  # ID Europeene
            r"^[\s\w]{14}$",  # ID Française
            r"^\w{1}\d{6}$",  # ID Tunisienne
            r"^\w{1} *\d{8}$",  # ID Turque
            r"^\w{2} *\d{7}$",  # Ancienne ID Italienne
            r"^\d{3}-\d{7}-\d{2}$",  # ID Belge
            r"^\d{7}$",  # ID Congolaise, Camerounaise, Mauricienne
            r"^\w{3} *\d{6}$",  # ID Polonaise
            r"^(\d *){17}$",  # ID Sénégalaise
            r"^\d{6}\w{1}$",  # Titre de séjour français
            r"^\d{6,8}-\d{4}$",  # ID Suédoise
        )
    )
    match = re.match(regexp, id_piece_number)
    if not match or match.group(0) != id_piece_number:
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail="Le format du numéro de la pièce d'identité n'est pas valide",
            reason_code=models.FraudReasonCode.INVALID_ID_PIECE_NUMBER,
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
            reason_code=models.FraudReasonCode.DUPLICATE_USER,
        )

    return models.FraudItem(status=models.FraudStatus.OK, detail="Utilisateur non dupliqué")


def _missing_data_fraud_item() -> models.FraudItem:
    return models.FraudItem(
        status=models.FraudStatus.SUSPICIOUS,
        reason_code=models.FraudReasonCode.MISSING_REQUIRED_DATA,
        detail="Des informations obligatoires (prénom, nom ou date de naissance) sont absentes du dossier",
    )


def find_duplicate_beneficiary(
    first_name: str,
    last_name: str,
    married_name: str | None,
    birth_date: datetime.date,
    excluded_user_id: int,
) -> users_models.User | None:
    base_query = users_models.User.query.filter(
        matching(users_models.User.firstName, first_name)
        & (sqlalchemy.func.DATE(users_models.User.dateOfBirth) == birth_date)
        & (users_models.User.is_beneficiary == True)
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
            reason_code=models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER,
        )

    return models.FraudItem(status=models.FraudStatus.OK, detail="La pièce d'identité n'est pas déjà utilisée")


def find_duplicate_id_piece_number_user(id_piece_number: str | None, excluded_user_id: int) -> users_models.User | None:
    if not id_piece_number:
        return None
    return users_models.User.query.filter(
        users_models.User.id != excluded_user_id,
        users_models.User.idPieceNumber.isnot(None),
        sqlalchemy.sql.func.replace(
            users_models.User.idPieceNumber,
            " ",
            "",
        )
        == id_piece_number.replace(" ", ""),
    ).first()


def _duplicate_ine_hash_fraud_item(ine_hash: str, excluded_user_id: int) -> models.FraudItem:
    duplicate_user = find_duplicate_ine_hash_user(ine_hash, excluded_user_id)

    if duplicate_user:
        return models.FraudItem(
            status=models.FraudStatus.SUSPICIOUS,
            detail=f"L'INE {ine_hash} est déjà pris par l'utilisateur {duplicate_user.id}",
            reason_code=models.FraudReasonCode.DUPLICATE_INE,
        )

    return models.FraudItem(status=models.FraudStatus.OK, detail="L'INE n'est pas déjà pris")


def find_duplicate_ine_hash_user(ine_hash: str, excluded_user_id: int) -> users_models.User | None:
    return users_models.User.query.filter(
        users_models.User.id != excluded_user_id, users_models.User.ineHash == ine_hash
    ).first()


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


def _check_user_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.FraudItem:
    if not eligibility:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail="L'âge indiqué dans le dossier indique que l'utilisateur n'est pas éligible",
            reason_code=models.FraudReasonCode.NOT_ELIGIBLE,
        )

    if not users_api.is_eligible_for_beneficiary_upgrade(user, eligibility):
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail=(f"L’utilisateur est déjà bénéfiaire du pass {eligibility.name}"),
            reason_code=models.FraudReasonCode.ALREADY_BENEFICIARY,
        )

    return models.FraudItem(
        status=models.FraudStatus.OK, detail="L'utilisateur est éligible à un nouveau statut bénéficiaire"
    )


def is_subscription_name_valid(name: str | None) -> bool:
    if (
        FeatureToggle.DISABLE_USER_NAME_AND_FIRST_NAME_VALIDATION_IN_TESTING_AND_STAGING.is_active()
        and not settings.IS_PROD
    ):
        return True
    if not name:
        return False
    stripped_name = name.strip()
    return is_latin(stripped_name)


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
            reason_code=models.FraudReasonCode.NAME_INCORRECT,
        )
    return models.FraudItem(
        status=models.FraudStatus.OK, detail="L'utilisateur a un nom et prénom avec des caractères valides"
    )


def _check_user_email_is_validated(user: users_models.User) -> models.FraudItem:
    if not user.isEmailValidated:
        return models.FraudItem(
            status=models.FraudStatus.KO,
            detail="L'email de l'utilisateur n'est pas validé",
            reason_code=models.FraudReasonCode.EMAIL_NOT_VALIDATED,
        )
    return models.FraudItem(status=models.FraudStatus.OK, detail="L'email est validé")


def _underage_user_fraud_item(birth_date: datetime.date) -> models.FraudItem:
    age = users_utils.get_age_from_birth_date(birth_date)
    if age in constants.ELIGIBILITY_UNDERAGE_RANGE:
        return models.FraudItem(
            status=models.FraudStatus.OK,
            detail=f"L'âge de l'utilisateur est valide ({age} ans).",
        )
    return models.FraudItem(
        status=models.FraudStatus.KO,
        detail=f"L'âge de l'utilisateur est invalide ({age} ans). Il devrait être parmi {constants.ELIGIBILITY_UNDERAGE_RANGE}",
        reason_code=models.FraudReasonCode.AGE_NOT_VALID,
    )


def on_user_profiling_result(
    user: users_models.User, profiling_infos: models.UserProfilingFraudData
) -> models.BeneficiaryFraudCheck:
    risk_rating = profiling_infos.risk_rating
    fraud_check_status = USER_PROFILING_FRAUD_CHECK_STATUS_RISK_MAPPING[risk_rating]
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.USER_PROFILING,
        thirdPartyId=profiling_infos.session_id,
        resultContent=profiling_infos,  # type: ignore [arg-type]
        status=fraud_check_status,
        eligibilityType=user.eligibility,
    )
    repository.save(fraud_check)
    on_user_profiling_check_result(user, risk_rating)
    return fraud_check


def on_user_profiling_check_result(
    user: users_models.User,
    risk_rating: models.UserProfilingRiskRating,
) -> None:
    user_profiling_status = USER_PROFILING_RISK_MAPPING[risk_rating]

    if not user_profiling_status == models.FraudStatus.OK:
        subscription_messages.on_user_subscription_journey_stopped(user)


def _create_failed_phone_validation_fraud_check(
    user: users_models.User,
    fraud_check_data: models.PhoneValidationFraudData,
    reason: str,
    reason_codes: list[models.FraudReasonCode],
) -> models.BeneficiaryFraudCheck:
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        reason=reason,
        reasonCodes=reason_codes,  # type: ignore [arg-type]
        type=models.FraudCheckType.PHONE_VALIDATION,
        thirdPartyId=f"PC-{user.id}",
        resultContent=fraud_check_data,  # type: ignore [arg-type]
        eligibilityType=user.eligibility,
        status=models.FraudCheckStatus.KO,
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
    reason_codes = [
        fraud_item.reason_code
        for fraud_item in fraud_items
        if fraud_item.status != models.FraudStatus.OK and fraud_item.reason_code is not None
    ]

    fraud_check.status = fraud_check_status
    fraud_check.reason = reason
    fraud_check.reasonCodes = reason_codes  # type: ignore [assignment]
    repository.save(fraud_check)

    return fraud_items


def has_user_pending_identity_check(user: users_models.User) -> bool:
    return db.session.query(
        models.BeneficiaryFraudCheck.query.filter(
            models.BeneficiaryFraudCheck.user == user,
            models.BeneficiaryFraudCheck.status == models.FraudCheckStatus.PENDING,
            models.BeneficiaryFraudCheck.type.in_(models.IDENTITY_CHECK_TYPES),
            models.BeneficiaryFraudCheck.eligibilityType == user.eligibility,
        ).exists()
    ).scalar()


def has_user_performed_identity_check(user: users_models.User) -> bool:
    if user.is_beneficiary and not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        return True

    status = subscription_api.get_identity_check_subscription_status(
        user, user.eligibility or users_models.EligibilityType.AGE18
    )
    return status not in (
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


def has_performed_honor_statement(user: users_models.User, eligibility_type: users_models.EligibilityType) -> bool:
    fraud_checks = user.beneficiaryFraudChecks
    return any(
        fraud_check.type == models.FraudCheckType.HONOR_STATEMENT
        and fraud_check.eligibilityType == eligibility_type
        and fraud_check.status == models.FraudCheckStatus.OK
        for fraud_check in fraud_checks
    )


def decide_eligibility(
    user: users_models.User,
    birth_date: datetime.date | datetime.datetime | None,
    registration_datetime: datetime.datetime | None,
) -> users_models.EligibilityType | None:
    """Returns the applicable eligibility of the user.
    It may be the current eligibility of the user if the age is between 15 and 18, or it may be the eligibility AGE18
    if the user is over 19 and had previously tried to register when the age was 18.
    """
    if birth_date is None:
        return None

    user_age_today = users_utils.get_age_from_birth_date(birth_date)
    if user_age_today < 15:
        return None
    if user_age_today < 18:
        return users_models.EligibilityType.UNDERAGE
    if user_age_today == 18:
        return users_models.EligibilityType.AGE18

    eligibility_today = users_api.get_eligibility_at_date(birth_date, datetime.datetime.utcnow())

    if eligibility_today == users_models.EligibilityType.AGE18:
        return users_models.EligibilityType.AGE18

    eligibility_at_registration = (
        users_api.get_eligibility_at_date(birth_date, registration_datetime) if registration_datetime else None
    )
    if eligibility_at_registration is None and eligibility_today is None and user_age_today == 19:
        earliest_identity_check_date = subscription_api.get_first_registration_date(
            user, birth_date, users_models.EligibilityType.AGE18
        )
        if earliest_identity_check_date:
            return users_api.get_eligibility_at_date(birth_date, earliest_identity_check_date)

    return eligibility_at_registration


UserGenerator = typing.Generator[users_models.User, None, None]


def get_suspended_upon_user_request_accounts_since(expiration_delta_in_days: int) -> Query:
    start = datetime.date.today() - datetime.timedelta(days=expiration_delta_in_days)

    # distinct keeps the first row if duplicates are found. Since rows
    # are ordered by userId and eventDate, this query will fetch the
    # latest event for each userId.
    user_ids_and_latest_events = (
        users_models.User.query.distinct(users_models.UserSuspension.userId)
        .join(users_models.User.suspension_history)
        .order_by(users_models.UserSuspension.userId, users_models.UserSuspension.eventDate.desc())
        .with_entities(
            users_models.User.id,
            users_models.UserSuspension.eventDate,
            users_models.UserSuspension.eventType,
            users_models.UserSuspension.reasonCode,
        )
    ).subquery()

    # Deletion is a special case of suspension, no need to delete again
    # an already deleted account.
    query = users_models.User.query.join(
        user_ids_and_latest_events, users_models.User.id == user_ids_and_latest_events.c.id
    ).filter(
        user_ids_and_latest_events.c.eventDate <= start,
        user_ids_and_latest_events.c.eventType == users_models.SuspensionEventType.SUSPENDED,
        user_ids_and_latest_events.c.reasonCode == users_models.SuspensionReason.UPON_USER_REQUEST,
    )

    return query


def handle_ok_manual_review(
    user: users_models.User,
    _review: models.BeneficiaryFraudReview,
    eligibility: users_models.EligibilityType | None,
) -> None:
    fraud_check = get_last_filled_identity_fraud_check(user)
    if not fraud_check:
        raise FraudCheckError("Pas de vérification d'identité effectuée")

    source_data: IdentityCheckContent = fraud_check.source_data()  # type: ignore[assignment]
    try:
        _check_id_piece_number_unicity(user, source_data.get_id_piece_number())
        _check_ine_hash_unicity(user, source_data.get_ine_hash())
    except DuplicateIdPieceNumber as err:
        raise FraudCheckError(
            f"Le numéro de CNI {err.id_piece_number} est déjà utilisé par l'utilisateur {err.duplicate_user_id}"
        ) from err
    except DuplicateIneHash as err:
        raise FraudCheckError(
            f"Le numéro INE {err.ine_hash} est déjà utilisé par l'utilisateur {err.duplicate_user_id}"
        ) from err

    users_api.update_user_information_from_external_source(user, source_data)

    if eligibility is None:
        eligibility = decide_eligibility(user, source_data.get_birth_date(), source_data.get_registration_datetime())
        if not eligibility:
            raise EligibilityError("Aucune éligibilité trouvée. Veuillez renseigner une éligibilité.")

    try:
        subscription_api.activate_beneficiary_for_eligibility(user, fraud_check.get_detailed_source(), eligibility)

    except subscription_exceptions.InvalidEligibilityTypeException as err:
        raise EligibilityError(f"L'égibilité '{eligibility.value}' n'existe pas !") from err

    except subscription_exceptions.InvalidAgeException as err:
        err_msg = (
            "L'âge de l'utilisateur à l'inscription n'a pas pu être déterminé"
            if err.age is None
            else f"L'âge de l'utilisateur à l'inscription ({err.age} ans) est incompatible avec l'éligibilité choisie"
        )
        raise EligibilityError(err_msg) from err

    except subscription_exceptions.CannotUpgradeBeneficiaryRole as err:
        raise EligibilityError(f"L'utilisateur ne peut pas être promu au rôle {eligibility.value}") from err

    except payments_exceptions.UserHasAlreadyActiveDeposit as err:
        raise EligibilityError(
            f"L'utilisateur bénéficie déjà d'un déposit non expiré du type '{eligibility.value}'"
        ) from err

    except payments_exceptions.DepositTypeAlreadyGrantedException as err:
        raise EligibilityError("Un déposit de ce type a déjà été créé") from err


def handle_dms_redirection_review(
    user: users_models.User,
    review: models.BeneficiaryFraudReview,
    _eligibility: users_models.EligibilityType | None,
) -> None:
    if review.reason is None:
        review.reason = "Redirigé vers DMS"
    else:
        review.reason += " ; Redirigé vers DMS"

    transaction_mails.send_subscription_document_error_email(user.email, "unread-document")
    subscription_messages.on_redirect_to_dms_from_idcheck(user)


def handle_ko_review(
    user: users_models.User,
    _review: models.BeneficiaryFraudReview,
    _eligibility: users_models.EligibilityType | None,
) -> None:
    subscription_messages.on_fraud_review_ko(user)


REVIEW_HANDLERS = {
    models.FraudReviewStatus.OK: handle_ok_manual_review,
    models.FraudReviewStatus.REDIRECTED_TO_DMS: handle_dms_redirection_review,
    models.FraudReviewStatus.KO: handle_ko_review,
}


def validate_beneficiary(
    user: users_models.User,
    reviewer: users_models.User,
    reason: str,
    review: models.FraudReviewStatus,
    eligibility: users_models.EligibilityType | None,
) -> models.BeneficiaryFraudReview:
    if not FeatureToggle.BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS.is_active():
        raise DisabledFeatureError("Cannot validate beneficiary because the feature is disabled")

    review = models.BeneficiaryFraudReview(user=user, author=reviewer, reason=reason, review=review.value)  # type: ignore [arg-type]

    if review.review is not None:
        handler = REVIEW_HANDLERS.get(models.FraudReviewStatus(review.review))
        if handler:
            handler(user, review, eligibility)

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
    if subscription_api.has_completed_profile(user, eligibility):
        logger.warning(
            "Profile completion fraud check for user already exists.",
            extra={"user_id": user.id},
        )
        return
    fraud_check = models.BeneficiaryFraudCheck(
        user=user,
        type=models.FraudCheckType.PROFILE_COMPLETION,
        resultContent=fraud_check_content,  # type: ignore [arg-type]
        status=models.FraudCheckStatus.OK,
        thirdPartyId=f"profile-completion-{user.id}",
        eligibilityType=eligibility,
        reason=fraud_check_content.origin,
    )
    repository.save(fraud_check)


def invalidate_fraud_check_if_duplicate(fraud_check: models.BeneficiaryFraudCheck) -> None:
    identity_content = fraud_check.source_data()

    if not isinstance(identity_content, IdentityCheckContent):
        raise ValueError("Invalid fraud check identity content type")

    first_name = identity_content.get_first_name()
    last_name = identity_content.get_last_name()
    birth_date = identity_content.get_birth_date()

    if not first_name or not last_name or not birth_date:
        raise ValueError("Invalid fraud check identity data")

    duplicate_user = find_duplicate_beneficiary(
        first_name,
        last_name,
        identity_content.get_married_name(),
        birth_date,
        fraud_check.userId,  # type: ignore [arg-type]
    )
    if not duplicate_user:
        return

    fraud_check.status = models.FraudCheckStatus.SUSPICIOUS
    if not fraud_check.reasonCodes:
        fraud_check.reasonCodes = []
    fraud_check.reasonCodes.append(models.FraudReasonCode.DUPLICATE_USER)  # type: ignore [arg-type]
    fraud_check.reason = f"Fraud check invalidé: duplicat de l'utilisateur {duplicate_user.id}"

    repository.save(fraud_check)
