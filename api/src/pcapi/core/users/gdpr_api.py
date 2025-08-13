import datetime
import itertools
import logging
import random
import typing
import zipfile
from io import BytesIO
from pathlib import Path

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from flask import current_app as app
from flask import render_template
from sqlalchemy import func
from sqlalchemy import orm as sa_orm

import pcapi.core.bookings.models as bookings_models
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.permissions.models as permissions_models
import pcapi.core.users.ds as users_ds
import pcapi.core.users.utils as users_utils
from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors.beamer import BeamerException
from pcapi.connectors.beamer import delete_beamer_user
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.core import object_storage
from pcapi.core.chronicles import api as chronicles_api
from pcapi.core.chronicles import constants as chronicles_constants
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.finance import models as finance_models
from pcapi.core.fraud import models as fraud_models
from pcapi.core.geography.repository import get_iris_from_address
from pcapi.core.history.api import add_action
from pcapi.core.mails import get_raw_contact_data
from pcapi.core.object_storage import store_public_object
from pcapi.core.users import api
from pcapi.core.users import constants
from pcapi.core.users import exceptions
from pcapi.core.users import models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications import push as push_api
from pcapi.routes.serialization import users as users_serialization
from pcapi.utils import transaction_manager
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.pdf import generate_pdf_from_html
from pcapi.utils.requests import ExternalAPIException


logger = logging.getLogger(__name__)


def has_unprocessed_extract(user: models.User) -> bool:
    for extract in user.gdprUserDataExtracts:
        if not extract.is_expired and not extract.dateProcessed:
            return True
    return False


def is_suspended_for_less_than_five_years(user: models.User) -> bool:
    if user.suspension_reason in constants.FRAUD_SUSPENSION_REASONS:
        return user.suspension_date > datetime.datetime.utcnow() - relativedelta(years=5)
    return False


def anonymize_user(user: models.User, *, author: models.User | None = None) -> bool:
    if has_unprocessed_extract(user):
        return False

    iris = None
    if user.address:
        try:
            iris = get_iris_from_address(address=user.address, postcode=user.postalCode)
        except (api_adresse.AdresseApiException, api_adresse.InvalidFormatException):
            pass

    try:
        push_api.delete_user_attributes(user_id=user.id, can_be_asynchronously_retried=True)
    except ExternalAPIException as exc:
        # If is_retryable it is a real error. If this flag is False then it means the email is unknown for brevo.
        if exc.is_retryable:
            logger.error("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
            return False
    except Exception as exc:
        logger.error("Could not anonymize user", extra={"user_id": user.id, "exc": str(exc)})
        return False

    for beneficiary_fraud_check in user.beneficiaryFraudChecks:
        beneficiary_fraud_check.resultContent = None
        beneficiary_fraud_check.reason = "Anonymized"
        beneficiary_fraud_check.dateCreated = beneficiary_fraud_check.dateCreated.replace(day=1, month=1)

    for beneficiary_fraud_review in user.beneficiaryFraudReviews:
        beneficiary_fraud_review.reason = "Anonymized"
        beneficiary_fraud_review.dateReviewed = beneficiary_fraud_review.dateReviewed.replace(day=1, month=1)

    for deposit in user.deposits:
        deposit.source = "Anonymized"

    for extract in user.gdprUserDataExtracts:
        delete_gdpr_extract(extract.id)

    db.session.query(models.GdprUserAnonymization).filter(models.GdprUserAnonymization.userId == user.id).delete()
    db.session.query(chronicles_models.Chronicle).filter(chronicles_models.Chronicle.userId == user.id).update(
        {
            "userId": None,
            "email": chronicles_constants.ANONYMIZED_EMAIL,
        },
        synchronize_session=False,
    )

    for update_request in (
        db.session.query(models.UserAccountUpdateRequest)
        .filter(models.UserAccountUpdateRequest.userId == user.id)
        .all()
    ):
        # UserAccountUpdateRequest objects are deleted after being archived in DS
        try:
            users_ds.archive(update_request, motivation="Anonymisation du compte")
        except dms_exceptions.DmsGraphQLApiError as dms_api_error:
            # Ignore not found: the application is already deleted or on staging after dump/restore with fake id
            if not dms_api_error.is_not_found:
                raise

    user.password = b"Anonymized"  # ggignore
    user.firstName = None
    user.lastName = None
    user.married_name = None
    user.postalCode = None
    user.phoneNumber = None  # type: ignore[method-assign]
    user.dateOfBirth = user.dateOfBirth.replace(day=1, month=1) if user.dateOfBirth else None
    user.address = None
    user.city = None
    user.externalIds = []
    user.idPieceNumber = None
    user.user_email_history = []
    user.irisFrance = iris
    user.validatedBirthDate = user.validatedBirthDate.replace(day=1, month=1) if user.validatedBirthDate else None

    external_email_anonymized = api.remove_external_user(user)

    db.session.query(models.TrustedDevice).filter(models.TrustedDevice.userId == user.id).delete()
    db.session.query(models.LoginDeviceHistory).filter(models.LoginDeviceHistory.userId == user.id).delete()
    db.session.query(history_models.ActionHistory).filter(
        history_models.ActionHistory.userId == user.id,
        history_models.ActionHistory.offererId.is_(None),
    ).delete()
    db.session.query(
        permissions_models.BackOfficeUserProfile,
    ).filter(
        permissions_models.BackOfficeUserProfile.userId == user.id,
    ).delete()

    if external_email_anonymized:
        user.replace_roles_by_anonymized_role()
        user.email = f"anonymous_{user.id}@anonymized.passculture"
        db.session.add(
            history_models.ActionHistory(
                actionType=history_models.ActionType.USER_ANONYMIZED,
                authorUser=author,
                userId=user.id,
            )
        )
    return True


@transaction_manager.atomic()
def anonymize_non_pro_non_beneficiary_users() -> None:
    """
    Anonymize user accounts that have never been beneficiary (no deposits), are not pro (no pro
    role) and which have not connected for at least 3 years and if they have been suspended it was
    at least 5 years ago.
    """
    users = (
        db.session.query(models.User)
        .outerjoin(
            finance_models.Deposit,
            models.User.deposits,
        )
        .filter(
            sa.func.email_domain(models.User.email) != "passculture.app",  # people who work or worked in the company
            func.array_length(models.User.roles, 1).is_(None),  # no role, not already anonymized
            finance_models.Deposit.userId.is_(None),  # no deposit
            models.User.lastConnectionDate < datetime.datetime.utcnow() - relativedelta(years=3),
            sa.or_(
                models.User.suspension_reason.is_(None),  # type: ignore [attr-defined]
                ~models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                sa.and_(
                    models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                    models.User.suspension_date < datetime.datetime.utcnow() - relativedelta(years=5),  # type: ignore [operator]
                ),
            ),
        )
    )
    for user in users:
        with transaction_manager.atomic():
            if not anonymize_user(user):
                transaction_manager.mark_transaction_as_invalid()


def is_beneficiary_anonymizable(user: models.User) -> bool:
    if not is_only_beneficiary(user):
        return False

    # Check if the user never had credits.
    if len(user.deposits) == 0:
        return True

    # Check if the user is over 21.
    if (
        user.validatedBirthDate
        and users_utils.get_age_at_date(user.validatedBirthDate, datetime.datetime.utcnow()) >= 21
    ):
        return True
    return False


def is_only_beneficiary(user: models.User) -> bool:
    # Check if the user is admin, pro or anonymised
    beneficiary_roles = {models.UserRole.BENEFICIARY, models.UserRole.UNDERAGE_BENEFICIARY}
    return beneficiary_roles.issuperset(user.roles)


def pre_anonymize_user(user: models.User, author: models.User, is_backoffice_action: bool = False) -> None:
    if has_user_pending_anonymization(user.id):
        raise exceptions.UserAlreadyHasPendingAnonymization()

    api.suspend_account(
        user=user,
        reason=constants.SuspensionReason.WAITING_FOR_ANONYMIZATION,
        actor=author,
        comment="L'utilisateur sera anonymisé le jour de ses 21 ans",
        is_backoffice_action=is_backoffice_action,
    )
    db.session.add(models.GdprUserAnonymization(user=user))
    db.session.flush()


def has_user_pending_anonymization(user_id: int) -> bool:
    return db.session.query(
        db.session.query(models.GdprUserAnonymization).filter(models.GdprUserAnonymization.userId == user_id).exists()
    ).scalar()


@transaction_manager.atomic()
def anonymize_beneficiary_users() -> None:
    """
    Anonymize user accounts that have been beneficiaries which have not connected for at least 3
    years, and whose deposit has been expired for at least 5 years and if they have been suspended
    it was at least 5 years ago.
    """
    beneficiaries = (
        db.session.query(models.User)
        .outerjoin(
            finance_models.Deposit,
            models.User.deposits,
        )
        .filter(
            models.User.is_beneficiary,
            models.User.lastConnectionDate < datetime.datetime.utcnow() - relativedelta(years=3),
            finance_models.Deposit.expirationDate < datetime.datetime.utcnow() - relativedelta(years=5),
            sa.or_(
                models.User.suspension_reason.is_(None),  # type: ignore [attr-defined]
                ~models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                sa.and_(
                    models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                    models.User.suspension_date < datetime.datetime.utcnow() - relativedelta(years=5),  # type: ignore [operator]
                ),
            ),
        )
    )

    beneficiaries_tagged_to_anonymize = (
        db.session.query(models.User)
        .join(models.GdprUserAnonymization)
        .filter(
            models.User.validatedBirthDate < datetime.datetime.utcnow() - relativedelta(years=21),
            sa.or_(
                models.User.suspension_reason.is_(None),  # type: ignore [attr-defined]
                ~models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                sa.and_(
                    models.User.suspension_reason.in_(constants.FRAUD_SUSPENSION_REASONS),  # type: ignore [attr-defined]
                    models.User.suspension_date < datetime.datetime.utcnow() - relativedelta(years=5),  # type: ignore [operator]
                ),
            ),
        )
    )
    for user in itertools.chain(beneficiaries, beneficiaries_tagged_to_anonymize):
        with transaction_manager.atomic():
            if not anonymize_user(user):
                transaction_manager.mark_transaction_as_invalid()


def _get_anonymize_pro_query(time_clause: sa.sql.elements.BooleanClauseList) -> typing.Any:
    aliased_user_offerer = sa_orm.aliased(offerers_models.UserOfferer)
    aliased_offerer = sa_orm.aliased(offerers_models.Offerer)

    return (
        db.session.query(models.User)
        .outerjoin(models.User.UserOfferers)
        .outerjoin(offerers_models.UserOfferer.offerer)
        .outerjoin(models.User.beneficiaryFraudChecks)
        .filter(
            # only NON_ATTACHED_PRO, excluding other role in the same array (BENEFICIARY, etc.)
            models.User.roles == [models.UserRole.NON_ATTACHED_PRO],
            fraud_models.BeneficiaryFraudCheck.id.is_(None),
            # never connected or not connected within the last 3 years
            time_clause,
            # attachment or offerer is no longer active
            sa.or_(
                offerers_models.UserOfferer.id.is_(None),
                offerers_models.UserOfferer.validationStatus.in_([ValidationStatus.REJECTED, ValidationStatus.DELETED]),
                offerers_models.Offerer.validationStatus.in_([ValidationStatus.REJECTED, ValidationStatus.CLOSED]),
            ),
            # not attached to another waiting/active offerer
            sa.not_(
                sa.exists()
                .where(aliased_user_offerer.userId == models.User.id)
                .where(
                    aliased_user_offerer.validationStatus.in_(
                        [ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.VALIDATED]
                    )
                )
                .where(aliased_offerer.id == aliased_user_offerer.offererId)
                .where(
                    aliased_offerer.validationStatus.in_(
                        [ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.VALIDATED]
                    )
                )
            ),
        )
    )


@transaction_manager.atomic()
def notify_pro_users_before_anonymization() -> None:
    """
    Send an email one month before
    """
    almost_three_years_ago = datetime.date.today() - relativedelta(years=3, days=-30)

    users = _get_anonymize_pro_query(
        sa.or_(
            sa.cast(models.User.lastConnectionDate, sa.Date) == almost_three_years_ago,
            sa.and_(
                models.User.lastConnectionDate.is_(None),
                sa.cast(models.User.dateCreated, sa.Date) == almost_three_years_ago,
            ),
        ),
    ).all()

    for user in users:
        transactional_mails.send_pre_anonymization_email_to_pro(user)


@transaction_manager.atomic()
def anonymize_pro_users() -> None:
    """
    Anonymize pro accounts
    """
    three_years_ago = datetime.datetime.utcnow() - relativedelta(years=3)

    users = _get_anonymize_pro_query(
        sa.or_(
            models.User.lastConnectionDate < three_years_ago,
            sa.and_(models.User.lastConnectionDate.is_(None), models.User.dateCreated < three_years_ago),
        ),
    )

    for user in users:
        with transaction_manager.atomic():
            anonymized = anonymize_user(user)
            if not anonymized:
                transaction_manager.mark_transaction_as_invalid()

        if anonymized:
            try:
                delete_beamer_user(user.id)
            except BeamerException:
                pass


@transaction_manager.atomic()
def anonymize_internal_users() -> None:
    """Anonymize user who use to work for the company

    As old suspended internal users do not have a role, we discriminate on the email address
    """
    suspended_subquery = (
        db.session.query(
            history_models.ActionHistory.actionDate,
        )
        .filter(
            history_models.ActionHistory.userId == models.User.id,
            history_models.ActionHistory.actionType == history_models.ActionType.USER_SUSPENDED,
        )
        .correlate(
            models.User,
        )
        .order_by(history_models.ActionHistory.id.desc())
        .limit(1)
        .scalar_subquery()
    )

    users = db.session.query(
        models.User,
        suspended_subquery.label("last_suspended_date"),
    ).filter(
        models.User.email.ilike("%@passculture.app"),
        models.User.isActive.is_(False),
    )
    for user, last_suspended in users:
        # USER_SUSPENDED before 2022-02-21 may have an null actionDate
        if (not last_suspended) or (last_suspended < get_naive_utc_now() - relativedelta(years=1)):
            anonymize_user(user)


def anonymize_user_deposits() -> None:
    """
    Anonymize deposits that have been expired for at least 10 years.
    """
    deposits_query = db.session.query(finance_models.Deposit).filter(
        finance_models.Deposit.expirationDate < datetime.datetime.utcnow() - relativedelta(years=10),
        ~sa.and_(  # ignore already anonymized deposits
            sa.func.extract("month", finance_models.Deposit.expirationDate) == 1,
            sa.func.extract("day", finance_models.Deposit.expirationDate) == 1,
            sa.func.extract("month", finance_models.Deposit.dateCreated) == 1,
            sa.func.extract("day", finance_models.Deposit.dateCreated) == 1,
        ),
    )
    deposits_query.update(
        {
            "expirationDate": sa.func.date_trunc("year", finance_models.Deposit.expirationDate),
            "dateCreated": sa.func.date_trunc("year", finance_models.Deposit.dateCreated),
        },
        synchronize_session=False,
    )


def clean_gdpr_extracts() -> None:
    files = object_storage.list_files(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )
    files_ids = set()
    for file_path in files:
        try:
            extract_id = int(Path(file_path).stem)
            files_ids.add(extract_id)
        except ValueError:
            continue

    ids_in_db_query = (
        db.session.query(models.GdprUserDataExtract)
        .filter(models.GdprUserDataExtract.id.in_(files_ids))
        .with_entities(models.GdprUserDataExtract.id)
    )
    ids_in_db = {r.id for r in ids_in_db_query}

    # files in bucket and not in db
    for extract_id in files_ids - ids_in_db:
        delete_gdpr_extract(extract_id)

    extracts_to_delete = (
        db.session.query(models.GdprUserDataExtract)
        .filter(models.GdprUserDataExtract.expirationDate < datetime.datetime.utcnow())  # type: ignore [operator]
        .with_entities(models.GdprUserDataExtract.id)
    )
    for extract in extracts_to_delete:
        # expired extract
        delete_gdpr_extract(extract.id)


def delete_gdpr_extract(extract_id: int) -> None:
    object_storage.delete_public_object(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        object_id=f"{extract_id}.zip",
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )
    db.session.query(models.GdprUserDataExtract).filter(models.GdprUserDataExtract.id == extract_id).delete()


def _extract_gdpr_chronicles(user: models.User) -> list[users_serialization.GdprChronicleData]:
    chronicles_data = (
        db.session.query(chronicles_models.Chronicle)
        .filter(
            chronicles_models.Chronicle.userId == user.id,
        )
        .options(
            sa_orm.joinedload(chronicles_models.Chronicle.products).load_only(
                offers_models.Product.ean,
                offers_models.Product.name,
            )
        )
    )

    chronicles = []
    for chronicle in chronicles_data:
        product_name = None
        for product in chronicle.products:
            product_identifier = chronicles_api.get_product_identifier(chronicle, product)
            if chronicle.productIdentifier and product_identifier == chronicle.productIdentifier:
                product_name = product.name
                break
        chronicles.append(
            users_serialization.GdprChronicleData(
                age=chronicle.age,
                city=chronicle.city,
                content=chronicle.content,
                dateCreated=chronicle.dateCreated,
                ean=chronicle.productIdentifier
                if chronicle.productIdentifierType == chronicles_models.ChronicleProductIdentifierType.EAN
                else None,
                allocineId=chronicle.productIdentifier
                if chronicle.productIdentifierType == chronicles_models.ChronicleProductIdentifierType.ALLOCINE_ID
                else None,
                visa=chronicle.productIdentifier
                if chronicle.productIdentifierType == chronicles_models.ChronicleProductIdentifierType.VISA
                else None,
                productIdentifier=chronicle.productIdentifier,
                productIdentifierType=chronicle.productIdentifierType.value,
                email=chronicle.email,
                firstName=chronicle.firstName,
                isIdentityDiffusible=chronicle.isIdentityDiffusible,
                isSocialMediaDiffusible=chronicle.isSocialMediaDiffusible,
                productName=product_name,
            )
        )
    return chronicles


def _extract_gdpr_account_update_requests(user: models.User) -> list[users_serialization.GdprAccountUpdateRequests]:
    fr_update_types = {
        models.UserAccountUpdateType.FIRST_NAME: "Prénom",
        models.UserAccountUpdateType.LAST_NAME: "Nom",
        models.UserAccountUpdateType.EMAIL: "Email",
        models.UserAccountUpdateType.PHONE_NUMBER: "Numéro de téléphone",
    }
    update_requests_data = db.session.query(models.UserAccountUpdateRequest).filter(
        models.UserAccountUpdateRequest.userId == user.id,
    )
    update_requests = []
    for update_request in update_requests_data:
        update_requests.append(
            users_serialization.GdprAccountUpdateRequests(
                allConditionsChecked=update_request.allConditionsChecked,
                birthDate=update_request.birthDate,
                dateCreated=update_request.dateCreated,
                dateLastInstructorMessage=update_request.dateLastInstructorMessage,
                dateLastStatusUpdate=update_request.dateLastStatusUpdate,
                dateLastUserMessage=update_request.dateLastUserMessage,
                email=update_request.email,
                firstName=update_request.firstName,
                lastName=update_request.lastName,
                newEmail=update_request.newEmail,
                newFirstName=update_request.newFirstName,
                newLastName=update_request.newLastName,
                newPhoneNumber=update_request.newPhoneNumber,
                oldEmail=update_request.oldEmail,
                status=update_request.status,
                updateTypes=[fr_update_types.get(updateType, "") for updateType in update_request.updateTypes],
            )
        )
    return update_requests


def _extract_gdpr_marketing_data(user: models.User) -> users_serialization.GdprMarketing:
    notification_subscriptions = user.notificationSubscriptions or {}
    return users_serialization.GdprMarketing(
        marketingEmails=notification_subscriptions.get("marketing_email") or False,
        marketingNotifications=notification_subscriptions.get("marketing_push") or False,
    )


def _extract_gdpr_devices_history(
    user: models.User,
) -> list[users_serialization.GdprLoginDeviceHistorySerializer]:
    login_devices_data = (
        db.session.query(models.LoginDeviceHistory)
        .filter(models.LoginDeviceHistory.user == user)
        .order_by(models.LoginDeviceHistory.id)
        .all()
    )
    return [users_serialization.GdprLoginDeviceHistorySerializer.from_orm(data) for data in login_devices_data]


def _extract_gdpr_deposits(user: models.User) -> list[users_serialization.GdprDepositSerializer]:
    deposit_types = {
        finance_models.DepositType.GRANT_15_17.name: "Pass 15-17",
        finance_models.DepositType.GRANT_18.name: "Pass 18",
    }
    deposits_data = (
        db.session.query(finance_models.Deposit)
        .filter(finance_models.Deposit.user == user)
        .order_by(finance_models.Deposit.id)
        .all()
    )
    return [
        users_serialization.GdprDepositSerializer(
            dateCreated=deposit.dateCreated,
            dateUpdated=deposit.dateUpdated,
            expirationDate=deposit.expirationDate,
            amount=deposit.amount,
            source=deposit.source,
            type=deposit_types.get(deposit.type.name, deposit.type.name),
        )
        for deposit in deposits_data
    ]


def _extract_gdpr_email_history(user: models.User) -> list[users_serialization.GdprEmailHistory]:
    emails = (
        db.session.query(models.UserEmailHistory)
        .filter(
            models.UserEmailHistory.user == user,
            models.UserEmailHistory.eventType.in_(
                [
                    models.EmailHistoryEventTypeEnum.CONFIRMATION,
                    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
                ]
            ),
        )
        .order_by(models.UserEmailHistory.id)
        .all()
    )
    emails_history = []
    for history in emails:
        new_email = None
        if history.newUserEmail:
            new_email = f"{history.newUserEmail}@{history.newDomainEmail}"
        emails_history.append(
            users_serialization.GdprEmailHistory(
                oldEmail=f"{history.oldUserEmail}@{history.oldDomainEmail}",
                newEmail=new_email,
                dateCreated=history.creationDate,
            )
        )
    return emails_history


def _extract_gdpr_action_history(user: models.User) -> list[users_serialization.GdprActionHistorySerializer]:
    actions_history = (
        db.session.query(history_models.ActionHistory)
        .filter(
            history_models.ActionHistory.user == user,
            history_models.ActionHistory.actionType.in_(
                [
                    history_models.ActionType.USER_SUSPENDED,
                    history_models.ActionType.USER_UNSUSPENDED,
                    history_models.ActionType.USER_PHONE_VALIDATED,
                    history_models.ActionType.USER_EMAIL_VALIDATED,
                ],
            ),
        )
        .order_by(history_models.ActionHistory.id)
        .all()
    )
    return [users_serialization.GdprActionHistorySerializer.from_orm(a) for a in actions_history]


def _extract_gdpr_beneficiary_validation(
    user: models.User,
) -> list[users_serialization.GdprBeneficiaryValidation]:
    check_types = {
        fraud_models.FraudCheckType.DMS.name: "Démarches simplifiées",
        fraud_models.FraudCheckType.EDUCONNECT.name: "ÉduConnect",
        fraud_models.FraudCheckType.HONOR_STATEMENT.name: "Attestation sur l'honneur",
        fraud_models.FraudCheckType.INTERNAL_REVIEW.name: "Revue Interne",
        fraud_models.FraudCheckType.JOUVE.name: "Jouve",
        fraud_models.FraudCheckType.PHONE_VALIDATION.name: "Validation par téléphone",
        fraud_models.FraudCheckType.PROFILE_COMPLETION.name: "Complétion du profil",
        fraud_models.FraudCheckType.UBBLE.name: "Ubble",
        fraud_models.FraudCheckType.USER_PROFILING.name: "Profilage d'utilisateur",
    }
    check_status = {
        fraud_models.FraudCheckStatus.CANCELED.name: "Annulé",
        fraud_models.FraudCheckStatus.ERROR.name: "Erreur",
        fraud_models.FraudCheckStatus.KO.name: "Échec",
        fraud_models.FraudCheckStatus.OK.name: "Succès",
        fraud_models.FraudCheckStatus.PENDING.name: "En attente",
        fraud_models.FraudCheckStatus.STARTED.name: "Commencé",
        fraud_models.FraudCheckStatus.SUSPICIOUS.name: "Suspect",
    }
    eligibility_types = {
        models.EligibilityType.AGE18.name: "Pass 18",
        models.EligibilityType.UNDERAGE.name: "Pass 15-17",
    }
    beneficiary_fraud_checks = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(fraud_models.BeneficiaryFraudCheck.user == user)
        .order_by(fraud_models.BeneficiaryFraudCheck.id)
        .all()
    )
    return [
        users_serialization.GdprBeneficiaryValidation(
            dateCreated=fraud_check.dateCreated,
            eligibilityType=(
                eligibility_types.get(fraud_check.eligibilityType.name, fraud_check.eligibilityType.name)
                if fraud_check.eligibilityType
                else None
            ),
            status=check_status.get(fraud_check.status.name, fraud_check.status.name) if fraud_check.status else None,
            type=check_types.get(fraud_check.type.name, fraud_check.type.name),
            updatedAt=fraud_check.updatedAt,
        )
        for fraud_check in beneficiary_fraud_checks
    ]


def _extract_gdpr_booking_data(user: models.User) -> list[users_serialization.GdprBookingSerializer]:
    booking_status = {
        bookings_models.BookingStatus.CONFIRMED.name: "Réservé",
        bookings_models.BookingStatus.USED.name: "Utilisé",
        bookings_models.BookingStatus.CANCELLED.name: "Annulé",
        bookings_models.BookingStatus.REIMBURSED.name: "Utilisé",
    }
    bookings_data = (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.user == user,
        )
        .options(
            sa_orm.joinedload(bookings_models.Booking.stock).joinedload(offers_models.Stock.offer),
            sa_orm.joinedload(bookings_models.Booking.venue),
            sa_orm.joinedload(bookings_models.Booking.venue).joinedload(offerers_models.Venue.managingOfferer),
        )
        .order_by(bookings_models.Booking.id)
    )
    bookings = []
    for booking_data in bookings_data:
        offerer = booking_data.venue.managingOfferer
        bookings.append(
            users_serialization.GdprBookingSerializer(
                cancellationDate=booking_data.cancellationDate,
                dateCreated=booking_data.dateCreated,
                dateUsed=booking_data.dateUsed,
                quantity=booking_data.quantity,
                amount=booking_data.amount,
                status=booking_status.get(booking_data.status.name, booking_data.status.name),
                name=booking_data.stock.offer.name,
                venue=booking_data.venue.common_name,
                offerer=offerer.name,
            )
        )
    return bookings


def _extract_gdpr_brevo_data(user: models.User) -> dict:
    return get_raw_contact_data(user.email, user.has_any_pro_role)


def _dump_gdpr_data_container_as_json_bytes(
    container: users_serialization.GdprDataContainer,
) -> tuple[zipfile.ZipInfo, bytes]:
    json_bytes = container.json(indent=4).encode("utf-8")
    file_info = zipfile.ZipInfo(
        filename=f"{container.internal.user.email}.json",
        date_time=datetime.datetime.utcnow().timetuple()[:6],
    )
    return file_info, json_bytes


def _dump_gdpr_data_container_as_pdf_bytes(
    container: users_serialization.GdprDataContainer,
) -> tuple[zipfile.ZipInfo, bytes]:
    html_content = render_template("extracts/beneficiary_extract.html", container=container)
    pdf_bytes = generate_pdf_from_html(html_content=html_content)
    file_info = zipfile.ZipInfo(
        filename=f"{container.internal.user.email}.pdf",
        date_time=datetime.datetime.utcnow().timetuple()[:6],
    )
    return file_info, pdf_bytes


def _generate_archive_from_gdpr_data_container(container: users_serialization.GdprDataContainer) -> BytesIO:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", allowZip64=False) as zip_file:
        zip_file.writestr(*_dump_gdpr_data_container_as_json_bytes(container))
        zip_file.writestr(*_dump_gdpr_data_container_as_pdf_bytes(container))
    buffer.seek(0)
    return buffer


def _store_gdpr_archive(name: str, archive: bytes) -> None:
    store_public_object(
        folder=settings.GCP_GDPR_EXTRACT_FOLDER,
        object_id=name,
        blob=archive,
        content_type="application/zip",
        bucket=settings.GCP_GDPR_EXTRACT_BUCKET,
    )


def extract_beneficiary_data(extract: models.GdprUserDataExtract) -> None:
    extract.dateProcessed = datetime.datetime.utcnow()
    user = extract.user
    data = users_serialization.GdprDataContainer(
        generationDate=datetime.datetime.utcnow(),
        internal=users_serialization.GdprInternal(
            user=users_serialization.GdprUserSerializer.from_orm(user),
            marketing=_extract_gdpr_marketing_data(user),
            loginDevices=_extract_gdpr_devices_history(user),
            emailsHistory=_extract_gdpr_email_history(user),
            actionsHistory=_extract_gdpr_action_history(user),
            beneficiaryValidations=_extract_gdpr_beneficiary_validation(user),
            deposits=_extract_gdpr_deposits(user),
            bookings=_extract_gdpr_booking_data(user),
            chronicles=_extract_gdpr_chronicles(user),
            accountUpdateRequests=_extract_gdpr_account_update_requests(user),
        ),
        external=users_serialization.GdprExternal(
            brevo=_extract_gdpr_brevo_data(user),
        ),
    )
    archive = _generate_archive_from_gdpr_data_container(data)
    _store_gdpr_archive(
        name=f"{extract.id}.zip",
        archive=archive.getvalue(),
    )
    add_action(history_models.ActionType.USER_EXTRACT_DATA, author=extract.authorUser, user=extract.user)
    db.session.flush()


def _get_extract_beneficiary_data_lock() -> bool:
    result = app.redis_client.set(
        constants.GDPR_EXTRACT_DATA_LOCK,
        "locked",
        ex=settings.GDPR_LOCK_TIMEOUT,
        nx=True,
    )
    return bool(result)


def _release_extract_beneficiary_data_lock() -> None:
    app.redis_client.delete(constants.GDPR_EXTRACT_DATA_LOCK)


def extract_beneficiary_data_command() -> bool:
    counter = ExtractBeneficiaryDataCounter(
        key=constants.GDPR_EXTRACT_DATA_COUNTER, max_value=settings.GDPR_MAX_EXTRACT_PER_DAY
    )
    counter.reset()

    if not _get_extract_beneficiary_data_lock():
        return False

    if counter.is_full():
        _release_extract_beneficiary_data_lock()
        return False

    candidates = (
        db.session.query(models.GdprUserDataExtract)
        .filter(
            models.GdprUserDataExtract.dateProcessed.is_(None),
            models.GdprUserDataExtract.expirationDate > datetime.datetime.utcnow(),  # type: ignore [operator]
        )
        .options(
            sa_orm.joinedload(models.GdprUserDataExtract.user),
            sa_orm.joinedload(models.GdprUserDataExtract.authorUser),
        )
        .limit(10)
        .all()
    )
    if not candidates:
        _release_extract_beneficiary_data_lock()
        return False

    # choose one at random to avoid being stuck on a buggy extract
    extract = random.choice(candidates)
    try:
        extract_beneficiary_data(extract)
    finally:
        _release_extract_beneficiary_data_lock()
    counter += 1  # type: ignore [misc]
    return True


class ExtractBeneficiaryDataCounter:
    """
    Counter to coordinate the limitation of extraction performed every day.
    If reset is called it will reset the counter between 0:00 and 0:10
    """

    def __init__(self, key: str, max_value: int):
        self.key = key
        self.max_value = max_value

    def reset(self) -> None:
        now = datetime.datetime.utcnow()
        if now.hour == 0 and now.minute < 10:
            app.redis_client.delete(self.key)

    def get(self) -> int:
        raw_counter = app.redis_client.get(self.key)
        counter = int(raw_counter) if raw_counter else 0
        return counter

    def is_full(self) -> bool:
        return self.get() >= self.max_value

    def __iadd__(self, other: int) -> None:
        app.redis_client.incrby(self.key, other)
