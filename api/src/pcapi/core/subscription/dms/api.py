import datetime
import enum
import hashlib
import logging

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
from dateutil.relativedelta import relativedelta

import pcapi.core.mails.transactional as transactional_mails
import pcapi.utils.email as email_utils
from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.connectors.dms.exceptions import DmsGraphQLApiException
from pcapi.connectors.dms.utils import lock_ds_application
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.mails.transactional.users import fraud_emails
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.dms import dms_internal_mailing
from pcapi.core.subscription.dms import fraud_check_api as fraud_dms_api
from pcapi.core.subscription.dms import messages
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.users import constants as users_constants
from pcapi.core.users import eligibility_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils import date as date_utils
from pcapi.utils import repository
from pcapi.utils.postal_code import PostalCode

from . import repository as dms_repository


logger = logging.getLogger(__name__)

FIELD_ERROR_LABELS = {
    dms_schemas.DmsFieldErrorKeyEnum.birth_date: "La date de naissance",
    dms_schemas.DmsFieldErrorKeyEnum.first_name: "Le prénom",
    dms_schemas.DmsFieldErrorKeyEnum.id_piece_number: "Le numéro de pièce d'identité",
    dms_schemas.DmsFieldErrorKeyEnum.last_name: "Le nom de famille",
    dms_schemas.DmsFieldErrorKeyEnum.postal_code: "Le code postal",
}

UPDATE_STATE_TIMEOUT = 30

PRE_GENERALISATION_DEPARTMENTS = ["08", "22", "25", "29", "34", "35", "56", "58", "67", "71", "84", "93", "94", "973"]

INACTIVITY_MESSAGE = """Aucune activité n’a eu lieu sur ton dossier depuis plus de {delay} jours.

Conformément à nos CGUs, en cas d’absence de réponse ou de justification insuffisante, nous nous réservons le droit de refuser ta création de compte. Aussi nous avons classé sans suite ton dossier n°{application_number}.

Sous réserve d’être encore éligible, tu peux si tu le souhaites refaire une demande d’inscription. Nous t'invitons à soumettre un nouveau dossier en suivant ce lien : https://demarche.numerique.gouv.fr/dossiers/new?procedure_id={procedure_id}

Tu trouveras toutes les informations dans notre FAQ pour t'accompagner dans cette démarche : https://aide.passculture.app/hc/fr/sections/4411991878545-Inscription-et-modification-d-information-sur-Démarches-Simplifiées
"""


class ApplicationLabel(enum.Enum):
    URGENT = "Urgent"


APPLICATION_LABEL_TO_SETTINGS_LABEL_ID: dict[int, dict[ApplicationLabel, str | None]] = {
    settings.DMS_ENROLLMENT_PROCEDURE_ID_FR: {
        ApplicationLabel.URGENT: settings.DMS_ENROLLMENT_FR_LABEL_ID_URGENT,
    },
    settings.DMS_ENROLLMENT_PROCEDURE_ID_ET: {
        ApplicationLabel.URGENT: settings.DMS_ENROLLMENT_ET_LABEL_ID_URGENT,
    },
}


def try_dms_orphan_adoption(user: users_models.User) -> None:
    dms_orphan = db.session.query(subscription_models.OrphanDmsApplication).filter_by(email=user.email).first()
    if not dms_orphan:
        return

    dms_application = dms_connector_api.DMSGraphQLClient().get_single_application_details(dms_orphan.application_id)
    fraud_check = handle_dms_application(dms_application)

    if fraud_check is not None:
        db.session.delete(dms_orphan)
        db.session.commit()


def _is_fraud_check_up_to_date(
    fraud_check: subscription_models.BeneficiaryFraudCheck, new_content: dms_schemas.DMSContent
) -> bool:
    if not fraud_check.resultContent:
        return False

    fraud_check_content = fraud_check.source_data()
    assert isinstance(fraud_check_content, dms_schemas.DMSContent)
    return compute_dms_checksum(new_content) == compute_dms_checksum(fraud_check_content)


def _update_fraud_check_with_new_content(
    fraud_check: subscription_models.BeneficiaryFraudCheck, new_content: dms_schemas.DMSContent
) -> None:
    fraud_check.reason = None
    fraud_check.reasonCodes = []
    fraud_check.resultContent = new_content.dict()
    new_eligibility = eligibility_api.decide_eligibility(
        fraud_check.user, new_content.get_birth_date(), new_content.get_registration_datetime()
    )
    if new_eligibility != fraud_check.eligibilityType:
        logger.warning("[DMS] User changed the eligibility in application %s", fraud_check.thirdPartyId)
        fraud_check.eligibilityType = new_eligibility


def _compute_birth_date_error_details(
    fraud_check: subscription_models.BeneficiaryFraudCheck, application_content: dms_schemas.DMSContent
) -> dms_schemas.DmsFieldErrorDetails | None:
    if fraud_check.eligibilityType is not None:
        return None

    birth_date = application_content.get_birth_date()

    return dms_schemas.DmsFieldErrorDetails(
        key=dms_schemas.DmsFieldErrorKeyEnum.birth_date,
        value=birth_date.isoformat() if birth_date else None,
    )


def _process_dms_application(
    application_content: dms_schemas.DMSContent,
    application_scalar_id: str,
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    state: dms_models.GraphQLApplicationStates,
    user: users_models.User,
) -> None:
    birth_date_error = _compute_birth_date_error_details(fraud_check, application_content)

    if state == dms_models.GraphQLApplicationStates.draft:
        _process_in_progress_application(
            fraud_check,
            application_content,
            subscription_models.FraudCheckStatus.STARTED,
            application_scalar_id,
            birth_date_error,
            is_application_updatable=True,
        )

    elif state == dms_models.GraphQLApplicationStates.on_going:
        _process_in_progress_application(
            fraud_check,
            application_content,
            subscription_models.FraudCheckStatus.PENDING,
            application_scalar_id,
            birth_date_error,
            is_application_updatable=False,
        )

    elif state == dms_models.GraphQLApplicationStates.accepted:
        _process_accepted_application(user, fraud_check, application_content.field_errors)

    elif state == dms_models.GraphQLApplicationStates.refused:
        fraud_check.status = subscription_models.FraudCheckStatus.KO
        fraud_check.reasonCodes = [subscription_models.FraudReasonCode.REFUSED_BY_OPERATOR]

    elif state == dms_models.GraphQLApplicationStates.without_continuation:
        fraud_check.status = subscription_models.FraudCheckStatus.CANCELED

    _update_application_annotations(application_scalar_id, application_content, birth_date_error, fraud_check)


def handle_dms_application(
    dms_application: dms_models.DmsApplicationResponse,
) -> subscription_models.BeneficiaryFraudCheck | None:
    application_number = dms_application.number
    user_email = email_utils.sanitize_email(dms_application.applicant.email or dms_application.profile.email)
    application_scalar_id = dms_application.id
    state = dms_application.state
    procedure_number = dms_application.procedure.number

    log_extra_data = {
        "application_number": application_number,
        "application_scalar_id": application_scalar_id,
        "procedure_number": procedure_number,
        "user_email": user_email,
        "dms_state": state,
    }

    application_content = dms_serializer.parse_beneficiary_information_graphql(dms_application)
    if not application_content.field_errors:
        logger.info(
            "Successfully parsed DMS application",
            extra=log_extra_data,
        )
    logger.info("[DMS] Application received with state %s", state, extra=log_extra_data)

    # Application may be refused after being instructed, even if there is no user account
    if state in (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going):
        _process_check_birth_date(
            application_content, dms_application.procedure.number, application_scalar_id, dms_application.labels
        )

        if _process_instructor_annotation(application_content, application_scalar_id):
            state = dms_models.GraphQLApplicationStates(application_content.state)

    user = find_user_by_email(user_email)
    if not user:
        logger.info("[DMS] User not found for application", extra=log_extra_data)
        _process_user_not_found_error(
            user_email,
            application_number,
            procedure_number,
            state,
            application_scalar_id,
            latest_modification_datetime=dms_application.latest_modification_datetime,
        )
        return None

    fraud_check = fraud_dms_api.get_fraud_check(user, application_number)
    if fraud_check is None:
        eligibility_type = (
            eligibility_api.decide_eligibility(
                user, application_content.get_birth_date(), application_content.get_registration_datetime()
            )
            if application_content
            else None
        )

        fraud_check = subscription_api.initialize_identity_fraud_check(
            eligibility_type=eligibility_type,
            fraud_check_type=subscription_models.FraudCheckType.DMS,
            identity_content=application_content,
            third_party_id=str(application_number),
            user=user,
        )
    else:
        if _is_fraud_check_up_to_date(fraud_check, application_content):
            logger.info("[DMS] FraudCheck already up to date", extra=log_extra_data)
            return fraud_check

        if fraud_check.status == subscription_models.FraudCheckStatus.OK:
            logger.warning("[DMS] Skipping because FraudCheck already has OK status", extra=log_extra_data)
            return fraud_check

        _update_fraud_check_with_new_content(fraud_check, application_content)

    _process_dms_application(application_content, application_scalar_id, fraud_check, state, user)

    return fraud_check


def _update_application_annotations(
    application_scalar_id: str,
    application_content: dms_schemas.DMSContent,
    birth_date_error: dms_schemas.DmsFieldErrorDetails | None,
    fraud_check: subscription_models.BeneficiaryFraudCheck,
) -> None:
    annotation = application_content.annotation
    if not annotation:
        logger.error("[DMS] No annotation defined for procedure %s", application_content.procedure_number)
        return
    new_annotation_value = _compute_new_annotation(application_content.field_errors, birth_date_error)
    if new_annotation_value == annotation.text:
        return

    logger.info("[DMS] Updating annotation for application %s", application_content.application_number)
    try:
        dms_connector_api.update_demarches_simplifiees_text_annotations(
            application_scalar_id, annotation.id, new_annotation_value
        )
    except Exception as exc:
        logger.exception(
            "[DMS] Error while updating annotation for application %s",
            application_content.application_number,
            extra={"error": str(exc), "application_scalar_id": application_scalar_id},
        )
        return
    new_annotation = dms_schemas.DmsAnnotation(id=annotation.id, label=annotation.label, text=new_annotation_value)
    fraud_check_content = fraud_check.source_data()
    assert isinstance(fraud_check_content, dms_schemas.DMSContent)
    fraud_check_content.annotation = new_annotation
    fraud_check.resultContent = fraud_check_content.dict()


def _compute_new_annotation(
    field_errors: list[dms_schemas.DmsFieldErrorDetails] | None,
    birth_date_error: dms_schemas.DmsFieldErrorDetails | None,
) -> str:
    annotation = ""
    if birth_date_error:
        annotation += f"{FIELD_ERROR_LABELS.get(birth_date_error.key)} ({birth_date_error.value}) indique que le demandeur n'est pas éligible au pass Culture (doit avoir entre 17 et 18 ans). "

    if field_errors:
        annotation += "Champs invalides: "
        annotation += ", ".join(
            f"{FIELD_ERROR_LABELS.get(field_error.key)} ({field_error.value})" for field_error in field_errors
        )

    if not annotation:
        annotation = "Aucune erreur détectée. Le dossier peut être passé en instruction."

    return annotation


def _send_field_error_dms_email(
    field_errors: list[dms_schemas.DmsFieldErrorDetails], application_scalar_id: str
) -> None:
    client = dms_connector_api.DMSGraphQLClient()
    client.send_user_message(
        application_scalar_id,
        settings.DMS_INSTRUCTOR_ID,
        dms_internal_mailing.build_field_errors_user_message(field_errors),
    )


def _send_eligibility_error_dms_email(
    formatted_birth_date: str | None,
    application_scalar_id: str,
    third_party_id: str,
) -> None:
    if not formatted_birth_date:
        logger.warning(
            "[DMS] No birth date found when trying to notify eligibility error",
            extra={"third_party_id": third_party_id},
        )
        return
    client = dms_connector_api.DMSGraphQLClient()
    client.send_user_message(
        application_scalar_id,
        settings.DMS_INSTRUCTOR_ID,
        dms_internal_mailing.build_dms_error_message_user_not_eligible(formatted_birth_date),
    )


def _process_in_progress_application(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    application_content: dms_schemas.DMSContent,
    fraud_check_status: subscription_models.FraudCheckStatus,
    application_scalar_id: str,
    birth_date_error: dms_schemas.DmsFieldErrorDetails | None,
    *,
    is_application_updatable: bool,
) -> None:
    if not application_content.field_errors and birth_date_error is None:
        fraud_check.status = fraud_check_status
        return

    errors = []
    reason_codes = []

    if birth_date_error is not None:
        if is_application_updatable:
            _send_eligibility_error_dms_email(birth_date_error.value, application_scalar_id, fraud_check.thirdPartyId)
        reason_codes.append(subscription_models.FraudReasonCode.AGE_NOT_VALID)
        errors.append(birth_date_error)

    if application_content.field_errors:
        if is_application_updatable:
            _send_field_error_dms_email(application_content.field_errors, application_scalar_id)
        reason_codes.append(subscription_models.FraudReasonCode.ERROR_IN_DATA)
        errors.extend(application_content.field_errors)

    logger.info(
        "[DMS] Errors found in DMS application",
        extra={
            "third_party_id": fraud_check.thirdPartyId,
            # `errors` is a list of `DmsFieldErrorDetails`.
            "errors": [{error.key.value: error.value} for error in errors],
            "status": fraud_check_status,
        },
    )

    _update_fraud_check_with_field_errors(
        fraud_check, errors, fraud_check_status=fraud_check_status, reason_codes=reason_codes
    )


def _update_fraud_check_with_field_errors(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    field_errors: list[dms_schemas.DmsFieldErrorDetails],
    fraud_check_status: subscription_models.FraudCheckStatus,
    reason_codes: list[subscription_models.FraudReasonCode],
) -> None:
    errors = ",".join([f"'{field_error.key.value}' ({field_error.value})" for field_error in field_errors])
    fraud_check.reason = f"Erreur dans les données soumises dans le dossier DMS : {errors}"
    fraud_check.reasonCodes = reason_codes
    fraud_check.status = fraud_check_status

    repository.save(fraud_check)


def _create_profile_completion_fraud_check_from_dms(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
    content: dms_schemas.DMSContent,
    application_id: str,
) -> None:
    """Creates a PROFILE_COMPLETION fraud check from a DMS content, provided that all necessary fields are filled."""
    if not all(
        [
            activity := content.get_activity(),
            address := content.get_address(),
            city := content.get_city(),
            first_name := content.get_first_name(),
            last_name := content.get_last_name(),
            postal_code := content.get_postal_code(),
        ]
    ):
        return

    fraud_api.create_profile_completion_fraud_check(
        user,
        eligibility,
        subscription_schemas.ProfileCompletionContent(
            activity=activity,
            address=address,
            city=city,
            first_name=first_name,
            last_name=last_name,
            origin=f"Completed in DMS application {application_id}",
            postal_code=postal_code,
            school_type=None,
        ),
    )


def _process_user_not_found_error(
    email: str,
    application_number: int,
    procedure_number: int,
    state: dms_models.GraphQLApplicationStates,
    application_scalar_id: str,
    *,
    latest_modification_datetime: datetime.datetime,
) -> None:
    orphan = dms_repository.get_orphan_dms_application_by_application_id(application_number)
    if orphan:
        if (
            not orphan.latest_modification_datetime
            or orphan.latest_modification_datetime < latest_modification_datetime
        ):
            orphan.latest_modification_datetime = latest_modification_datetime
            repository.save(orphan)
        else:
            # Application was already processed
            return
    else:
        # Create new orphan
        dms_repository.create_orphan_dms_application(
            application_number=application_number,
            procedure_number=procedure_number,
            latest_modification_datetime=latest_modification_datetime,
            email=email,
        )
        if state == dms_models.GraphQLApplicationStates.draft:
            dms_connector_api.DMSGraphQLClient().send_user_message(
                application_scalar_id,
                settings.DMS_INSTRUCTOR_ID,
                dms_internal_mailing.DMS_ERROR_MESSAGE_USER_NOT_FOUND,
            )
        elif state == dms_models.GraphQLApplicationStates.accepted:
            transactional_mails.send_create_account_after_dms_email(email)


def _process_accepted_application(
    user: users_models.User,
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    field_errors: list[dms_schemas.DmsFieldErrorDetails] | None,
) -> None:
    if field_errors:
        transactional_mails.send_pre_subscription_from_dms_error_email_to_beneficiary(
            user.email,
            field_errors,
        )
        _update_fraud_check_with_field_errors(
            fraud_check,
            field_errors,
            subscription_models.FraudCheckStatus.ERROR,
            [subscription_models.FraudReasonCode.ERROR_IN_DATA],
        )
        return

    dms_content = fraud_check.source_data()
    assert isinstance(dms_content, dms_schemas.DMSContent)

    try:
        fraud_api.on_dms_fraud_result(user, fraud_check)
    except Exception as exc:
        logger.exception("Error on dms fraud check result: %s", exc)
        return

    if fraud_check.status != subscription_models.FraudCheckStatus.OK:
        error_codes = fraud_check.reasonCodes or []
        _handle_validation_errors(user, error_codes, dms_content)

        return

    user.validatedBirthDate = dms_content.get_birth_date()

    fraud_api.create_honor_statement_fraud_check(
        user, "honor statement contained in DMS application", fraud_check.eligibilityType
    )
    _create_profile_completion_fraud_check_from_dms(
        user, fraud_check.eligibilityType, dms_content, application_id=fraud_check.thirdPartyId
    )

    if subscription_api.requires_manual_review_before_activation(user, fraud_check):
        fraud_emails.send_mail_for_fraud_review(user)

    try:
        has_completed_all_steps = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
    except Exception:
        logger.exception(
            "[DMS] Could not save application %s - Procedure %s",
            dms_content.application_number,
            dms_content.procedure_number,
        )
        return

    logger.info(
        "[DMS] Successfully imported accepted DMS application %s - Procedure %s",
        dms_content.application_number,
        dms_content.procedure_number,
    )

    if not has_completed_all_steps:
        transactional_mails.send_complete_subscription_after_dms_email(user.email)
        external_attributes_api.update_external_user(user)


def _handle_validation_errors(
    user: users_models.User,
    reason_codes: list[subscription_models.FraudReasonCode],
    dms_content: dms_schemas.DMSContent,
) -> None:
    if subscription_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        transactional_mails.send_duplicate_beneficiary_email(
            user, dms_content, subscription_models.FraudReasonCode.DUPLICATE_USER
        )
    elif subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        transactional_mails.send_duplicate_beneficiary_email(
            user, dms_content, subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER
        )

    reason = ", ".join([code.name for code in reason_codes])

    logger.warning(
        "[DMS] Rejected application %s because of '%s' - Procedure %s",
        dms_content.application_number,
        reason,
        dms_content.procedure_number,
        extra={"user_id": user.id},
    )


def get_dms_subscription_message(
    dms_fraud_check: subscription_models.BeneficiaryFraudCheck,
) -> subscription_schemas.SubscriptionMessage | None:
    application_content = None
    birth_date_error = None
    if dms_fraud_check.resultContent is not None:
        # old FraudChecks may not have resultContent filled
        application_content = dms_fraud_check.source_data()
        assert isinstance(application_content, dms_schemas.DMSContent)
        birth_date_error = _compute_birth_date_error_details(dms_fraud_check, application_content)

    assert application_content is None or isinstance(application_content, dms_schemas.DMSContent)

    if dms_fraud_check.status == subscription_models.FraudCheckStatus.STARTED:
        if dms_fraud_check.reasonCodes:
            return messages.get_error_updatable_message(
                application_content, birth_date_error, dms_fraud_check.updatedAt
            )
        return messages.get_application_received_message(dms_fraud_check)

    if dms_fraud_check.status == subscription_models.FraudCheckStatus.PENDING:
        if dms_fraud_check.reasonCodes:
            return messages.get_error_not_updatable_message(
                dms_fraud_check.user,
                dms_fraud_check.reasonCodes or [],
                application_content,
                birth_date_error,
                dms_fraud_check.updatedAt,
            )
        return messages.get_application_received_message(dms_fraud_check)

    if dms_fraud_check.status in (
        subscription_models.FraudCheckStatus.SUSPICIOUS,
        subscription_models.FraudCheckStatus.KO,
        subscription_models.FraudCheckStatus.ERROR,
    ):
        return messages.get_error_processed_message(
            dms_fraud_check.user,
            dms_fraud_check.reasonCodes or [],
            application_content,
            birth_date_error,
            dms_fraud_check.updatedAt,
        )

    # Status is OK or CANCELED. We don't want to display a subscription message
    return None


def compute_dms_checksum(content: dms_schemas.DMSContent) -> str:
    """
    Compute the checksum for a DMS fraud check.
    """
    fields = [
        content.activity,
        content.address,
        content.birth_date.isoformat() if content.birth_date else None,
        content.birth_place,
        content.city,
        content.civility.value if content.civility else None,
        content.department,
        content.email,
        content.first_name,
        content.id_piece_number,
        content.last_name,
        content.phone,
        content.postal_code,
        content.state,
    ]
    sorted_fields = sorted([field.encode("utf-8") for field in fields if field is not None])
    checksum = hashlib.sha256(b"".join(sorted_fields)).hexdigest()

    return checksum


def _process_check_birth_date(
    application_content: dms_schemas.DMSContent,
    procedure_number: int,
    application_scalar_id: str,
    labels: list[dms_models.DMSLabel],
) -> None:
    # Tag as "Urgent" when 7 days or less before end of eligibility
    if any(label.name == ApplicationLabel.URGENT.value for label in labels):
        return

    if birth_date := application_content.get_birth_date():
        days_before_end_of_eligibility = (
            birth_date + relativedelta(years=users_constants.ELIGIBILITY_END_AGE) - datetime.date.today()
        ).days
        if 0 < days_before_end_of_eligibility <= 7:
            _add_application_label(procedure_number, application_scalar_id, ApplicationLabel.URGENT)


def _add_application_label(procedure_number: int, application_scalar_id: str, label: ApplicationLabel) -> None:
    label_id = APPLICATION_LABEL_TO_SETTINGS_LABEL_ID.get(procedure_number, {}).get(label)
    if not label_id:
        raise ValueError("Configuration error: unknown label")

    try:
        client = dms_connector_api.DMSGraphQLClient()
        client.add_label_to_application(application_scalar_id, label_id)
    except DmsGraphQLApiException:
        pass  # label is a helper, do not fail; already logged


def _process_instructor_annotation(application_content: dms_schemas.DMSContent, application_scalar_id: str) -> bool:
    if not FeatureToggle.ENABLE_DS_APPLICATION_REFUSED_FROM_ANNOTATION.is_active():
        return False

    if not application_content.instructor_annotation:
        return False

    if (
        application_content.instructor_annotation.updated_datetime is not None
        and application_content.latest_user_fields_modification_datetime is not None
        and application_content.latest_user_fields_modification_datetime
        > application_content.instructor_annotation.updated_datetime
    ):
        # Application was still draft and has been updated by user, so instructor annotation may not be up-to-date
        # Ignore to avoid unconsistency between user fields and the reason to refuse.
        return False

    values = (
        application_content.instructor_annotation.value
        if isinstance(application_content.instructor_annotation.value, list)
        else [application_content.instructor_annotation.value]
    )

    if dms_schemas.DmsInstructorAnnotationEnum.NEL in values:
        motivation = dms_internal_mailing.DMS_MESSAGE_REFUSED_USER_NOT_ELIGIBLE
    elif dms_schemas.DmsInstructorAnnotationEnum.IDP in values:
        motivation = dms_internal_mailing.DMS_MESSAGE_REFUSED_ID_EXPIRED
    else:
        return False

    # Can be rejected automatically since an instructor has checked details before manually setting an annotation
    client = dms_connector_api.DMSGraphQLClient(timeout=UPDATE_STATE_TIMEOUT)
    client.make_refused(
        application_scalar_id,
        settings.DMS_ENROLLMENT_INSTRUCTOR,
        motivation,
        from_draft=(application_content.state == dms_models.GraphQLApplicationStates.draft.value),
    )
    application_content.state = dms_models.GraphQLApplicationStates.refused.value
    application_content.processed_datetime = date_utils.get_naive_utc_now()
    return True


def _import_all_dms_applications_initial_import(procedure_id: int) -> None:
    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_id)
    client = dms_connector_api.DMSGraphQLClient()
    processed_applications: list = []
    new_import_datetime = None
    for application_details in client.get_applications_with_details(procedure_id):
        if application_details.number in already_processed_applications_ids:
            continue
        try:
            handle_dms_application(application_details)
            processed_applications.append(application_details.number)
            if new_import_datetime is None or application_details.latest_modification_datetime > new_import_datetime:
                new_import_datetime = application_details.latest_modification_datetime
        except Exception:
            logger.exception("[DMS] Error in script while importing application %s", application_details.number)
    if new_import_datetime is None:
        # This is a normal situation outside prod, when we have few
        # applications to process (and often no applications at all).
        log = logger.error if settings.DS_LOGGER_ERROR else logger.info
        log("[DMS] No import for procedure %s", procedure_id)
        return
    new_import_record = dms_models.LatestDmsImport(
        procedureId=procedure_id,
        latestImportDatetime=new_import_datetime,
        isProcessing=False,
        processedApplications=processed_applications,
    )
    repository.save(new_import_record)
    logger.info(
        "[DMS] End import of all applications from Démarche Numérique for procedure %s - Processed %s applications",
        procedure_id,
        len(processed_applications),
    )


def import_all_updated_dms_applications(procedure_number: int, forced_since: datetime.datetime | None = None) -> None:
    logger.info("[DMS] Start import of all applications from Démarche Numérique for procedure %s", procedure_number)

    latest_dms_import_record: dms_models.LatestDmsImport | None = (
        db.session.query(dms_models.LatestDmsImport)
        .filter(dms_models.LatestDmsImport.procedureId == procedure_number)
        .order_by(dms_models.LatestDmsImport.latestImportDatetime.desc())
        .first()
    )
    if latest_dms_import_record is None:
        logger.info("[DMS] No previous import found for procedure %s. Running first import.", procedure_number)
        _import_all_dms_applications_initial_import(procedure_number)
        logger.info("[DMS] End import of all applications from Démarche Numérique for procedure %s", procedure_number)
        return

    new_import_datetime = None
    if latest_dms_import_record.isProcessing:
        logger.info("[DMS] Previous import is still processing for procedure %s", procedure_number)
        return

    latest_dms_import_record.isProcessing = True

    processed_applications: list = []
    try:
        client = dms_connector_api.DMSGraphQLClient()

        # It is OK to pass a UTC datetime as a param to DMS.
        # Their API understands it is a UTC datetime and interprets it correctly, even if they return time in the local timezone.
        for application_details in client.get_applications_with_details(
            procedure_number, since=forced_since if forced_since else latest_dms_import_record.latestImportDatetime
        ):
            try:
                latest_modification_datetime = application_details.latest_modification_datetime
                if new_import_datetime is None or latest_modification_datetime > new_import_datetime:
                    new_import_datetime = latest_modification_datetime

                with lock_ds_application(application_details.number):
                    handle_dms_application(application_details)
                processed_applications.append(application_details.number)
            except Exception:
                logger.exception("[DMS] Error in script while importing application %s", application_details.number)

    except Exception as e:
        logger.exception(
            "[DMS] Error in script while importing all applications for procedure %s", procedure_number, exc_info=e
        )
    latest_dms_import_record.isProcessing = False

    if new_import_datetime is None:
        new_import_datetime = latest_dms_import_record.latestImportDatetime

    new_import_record = dms_models.LatestDmsImport(
        procedureId=procedure_number,
        latestImportDatetime=new_import_datetime,
        isProcessing=False,
        processedApplications=processed_applications,
    )
    db.session.add(new_import_record)
    db.session.flush()

    logger.info(
        "[DMS] End import of all applications from Démarche Numérique for procedure %s - Processed %s applications",
        procedure_number,
        len(processed_applications),
    )


def archive_applications(procedure_number: int, dry_run: bool = True) -> None:
    total_applications = 0
    archived_applications = 0

    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_number)
    client = dms_connector_api.DMSGraphQLClient()

    for application_details in client.get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.accepted
    ):
        total_applications += 1

        application_techid = application_details.id
        application_number = application_details.number

        if application_number not in already_processed_applications_ids:
            continue

        if not dry_run:
            try:
                client.archive_application(application_techid, settings.DMS_ENROLLMENT_INSTRUCTOR)
            except Exception:
                logger.exception("error while archiving application %d", application_number)
        logger.info("Archiving application %d on procedure %d", application_number, procedure_number)
        archived_applications += 1

    logger.info(
        "script ran : total applications : %d to archive applications : %d", total_applications, archived_applications
    )


def _get_latest_deleted_application_datetime(procedure_number: int) -> datetime.datetime | None:
    fraud_check: subscription_models.BeneficiaryFraudCheck | None = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
            subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.CANCELED,
            subscription_models.BeneficiaryFraudCheck.resultContent.is_not(None),
            subscription_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(sa.Integer)
            == procedure_number,
            subscription_models.BeneficiaryFraudCheck.resultContent.has_key("deletion_datetime"),
        )
        .order_by(subscription_models.BeneficiaryFraudCheck.resultContent["deletion_datetime"].desc())
        .first()
    )
    if fraud_check:
        content = fraud_check.source_data()
        if isinstance(content, dms_schemas.DMSContent):
            return content.deletion_datetime

        raise ValueError(f"fraud_check.source_data() is not a DMSContent. Fraud check: {fraud_check.id}")
    return None


def handle_deleted_dms_applications(procedure_number: int) -> None:
    latest_deleted_application_datetime = _get_latest_deleted_application_datetime(procedure_number)

    logger.info(
        "Looking for deleted applications for procedure %d since %s",
        procedure_number,
        latest_deleted_application_datetime,
    )

    dms_graphql_client = dms_connector_api.DMSGraphQLClient()
    applications_to_mark_as_deleted = {}

    for deleted_application in dms_graphql_client.get_deleted_applications(
        procedure_number, deletedSince=latest_deleted_application_datetime
    ):
        applications_to_mark_as_deleted[str(deleted_application.number)] = deleted_application

    fraud_checks_to_mark_as_deleted = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .filter(
            subscription_models.BeneficiaryFraudCheck.thirdPartyId.in_(applications_to_mark_as_deleted),
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
            subscription_models.BeneficiaryFraudCheck.status != subscription_models.FraudCheckStatus.CANCELED,
            subscription_models.BeneficiaryFraudCheck.status != subscription_models.FraudCheckStatus.OK,
        )
        .yield_per(100)
    )
    updated_fraud_checks_count = 0

    for fraud_check in fraud_checks_to_mark_as_deleted:
        dms_information: dms_models.DmsDeletedApplication = applications_to_mark_as_deleted[fraud_check.thirdPartyId]
        try:
            fraud_check_data = fraud_check.source_data()
            assert isinstance(fraud_check_data, dms_schemas.DMSContent)

            fraud_check_data.deletion_datetime = dms_information.deletion_datetime
            fraud_check.resultContent = fraud_check_data.dict()
        except ValueError:
            logger.warning(
                "Could not write 'deletion_datetime' in fraud check resultContent: resultContent is empty",
                extra={"fraud_check": fraud_check.id, "deletion_datetime": dms_information.deletion_datetime},
            )

        fraud_check.status = subscription_models.FraudCheckStatus.CANCELED
        fraud_check.reason = f"Dossier supprimé sur démarches-simplifiées. Motif: {dms_information.reason}"

        db.session.add(fraud_check)
        updated_fraud_checks_count += 1
    db.session.commit()

    logger.info(
        "Marked %d fraud checks as deleted for procedure %d since %s",
        updated_fraud_checks_count,
        procedure_number,
        latest_deleted_application_datetime,
    )


def handle_inactive_dms_applications(procedure_number: int, with_never_eligible_applicant_rule: bool = False) -> None:
    logger.info("[DMS] Handling inactive application for procedure %d", procedure_number)
    marked_applications_count = 0
    draft_applications = dms_connector_api.DMSGraphQLClient().get_applications_with_details(
        procedure_number, dms_models.GraphQLApplicationStates.draft
    )

    for draft_application in draft_applications:
        with lock_ds_application(draft_application.number):
            try:
                if not _has_inactivity_delay_expired(draft_application):
                    continue
                if with_never_eligible_applicant_rule and _is_never_eligible_applicant(draft_application):
                    continue
                _mark_without_continuation_a_draft_application(draft_application)
                _mark_cancel_dms_fraud_check(
                    draft_application.number, draft_application.applicant.email or draft_application.profile.email
                )
                marked_applications_count += 1
            except (DmsGraphQLApiException, Exception):
                logger.exception(
                    "[DMS] Could not mark application %s without continuation",
                    draft_application.number,
                    extra={"procedure_number": procedure_number},
                )
                continue

    logger.info("[DMS] Marked %d inactive applications for procedure %d", marked_applications_count, procedure_number)


def _has_inactivity_delay_expired(dms_application: dms_models.DmsApplicationResponse) -> bool:
    date_with_delay = date_utils.get_naive_utc_now() - relativedelta(days=settings.DMS_INACTIVITY_TOLERANCE_DELAY)

    if dms_application.latest_modification_datetime >= date_with_delay:
        return False

    # Do not close application if no message has been sent by either an instructor or the automation
    if not dms_application.messages:
        return False

    most_recent_message = max(dms_application.messages, key=lambda message: message.created_at)

    return most_recent_message.created_at <= date_with_delay and not _is_message_from_applicant(
        dms_application, most_recent_message
    )


def _is_message_from_applicant(
    dms_application: dms_models.DmsApplicationResponse, message: dms_models.DMSMessage
) -> bool:
    return message.email == (dms_application.applicant.email or dms_application.profile.email)


def _mark_without_continuation_a_draft_application(dms_application: dms_models.DmsApplicationResponse) -> None:
    """Mark a draft application as without continuation.

    First make it on_going - disable notification to only notify the user of the without_continuation change
    Then mark it without_continuation
    """
    dms_connector_api.DMSGraphQLClient().mark_without_continuation(
        dms_application.id,
        settings.DMS_ENROLLMENT_INSTRUCTOR,
        motivation=INACTIVITY_MESSAGE.format(
            delay=settings.DMS_INACTIVITY_TOLERANCE_DELAY,
            procedure_id=dms_application.procedure.number,
            application_number=dms_application.number,
        ),
        from_draft=True,
    )

    logger.info("[DMS] Marked application %s without continuation", dms_application.number)


def _mark_cancel_dms_fraud_check(application_number: int, email: str) -> None:
    try:
        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter(
                subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
                subscription_models.BeneficiaryFraudCheck.thirdPartyId == str(application_number),
                subscription_models.BeneficiaryFraudCheck.resultContent.is_not(None),
                subscription_models.BeneficiaryFraudCheck.resultContent.contains({"email": email}),
            )
            .one_or_none()
        )
    except sa_exc.MultipleResultsFound:
        logger.exception("[DMS] Multiple fraud checks found for application %s", application_number)
        return

    if fraud_check:
        fraud_check.status = subscription_models.FraudCheckStatus.CANCELED
        fraud_check.reason = f"Automatiquement classé sans_suite car aucune activité n'a eu lieu depuis plus de {settings.DMS_INACTIVITY_TOLERANCE_DELAY} jours"
        repository.save(fraud_check)


def _is_never_eligible_applicant(dms_application: dms_models.DmsApplicationResponse) -> bool:
    application_content = dms_serializer.parse_beneficiary_information_graphql(dms_application)
    if application_content.field_errors:
        return True
    applicant_birth_date = application_content.get_birth_date()
    applicant_postal_code = application_content.get_postal_code()
    applicant_department = PostalCode(applicant_postal_code).get_departement_code() if applicant_postal_code else None
    if applicant_birth_date is None or applicant_department is None:
        return True

    age_at_generalisation = users_utils.get_age_at_date(applicant_birth_date, datetime.datetime(2021, 5, 21))

    return age_at_generalisation >= 19 and applicant_department not in PRE_GENERALISATION_DEPARTMENTS
