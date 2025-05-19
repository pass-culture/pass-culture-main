import datetime
import enum
import logging
from dataclasses import dataclass

from pcapi import settings
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models
from pcapi.core.users import models as users_models
from pcapi.utils.string import u_nbsp


logger = logging.getLogger(__name__)

MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"


class NounGender(enum.Enum):
    MASCULINE = enum.auto()
    FEMININE = enum.auto()


@dataclass
class FieldErrorLabel:
    label: str
    gender: NounGender


FIELD_ERROR_LABELS = {
    fraud_models.DmsFieldErrorKeyEnum.birth_date: FieldErrorLabel(
        label="date de naissance", gender=NounGender.FEMININE
    ),
    fraud_models.DmsFieldErrorKeyEnum.first_name: FieldErrorLabel(label="prénom", gender=NounGender.MASCULINE),
    fraud_models.DmsFieldErrorKeyEnum.id_piece_number: FieldErrorLabel(
        label="numéro de pièce d'identité", gender=NounGender.MASCULINE
    ),
    fraud_models.DmsFieldErrorKeyEnum.last_name: FieldErrorLabel(label="nom de famille", gender=NounGender.MASCULINE),
    fraud_models.DmsFieldErrorKeyEnum.postal_code: FieldErrorLabel(label="code postal", gender=NounGender.MASCULINE),
}


def _generate_form_field_error(
    error_text_singular_masculine: str,
    error_text_singular_feminine: str,
    error_text_plural: str,
    error_fields: list[fraud_models.DmsFieldErrorDetails],
) -> str:
    error_field_details = [FIELD_ERROR_LABELS.get(error_field.key) for error_field in error_fields]

    if len(error_fields) == 1:
        field = error_field_details[0]
        if not field:
            logger.error("Unknown field error key: %s", error_fields[0].key)
            return "Ton dossier déposé sur le site demarches-simplifiees.fr contient des erreurs."
        user_message = (
            error_text_singular_masculine.format(formatted_error_fields=field.label)
            if (field.gender == NounGender.MASCULINE)
            else error_text_singular_feminine.format(formatted_error_fields=field.label)
        )
    else:
        error_field_labels = [field.label for field in error_field_details if field]
        user_message = error_text_plural.format(
            formatted_error_fields=", ".join(error_field_labels[:-1]) + " et " + error_field_labels[-1]
        )

    return user_message


def get_application_received_message(fraud_check: fraud_models.BeneficiaryFraudCheck) -> models.SubscriptionMessage:
    return models.SubscriptionMessage(
        user_message=f"Nous avons bien reçu ton dossier le {fraud_check.dateCreated.date():%d/%m/%Y}. Rends-toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel.",
        pop_over_icon=models.PopOverIcon.FILE,
        call_to_action=None,
        updated_at=fraud_check.updatedAt,
    )


def get_error_updatable_message(
    application_content: fraud_models.DMSContent | None,
    birth_date_error: fraud_models.DmsFieldErrorDetails | None,
    updated_at: datetime.datetime | None,
) -> models.SubscriptionMessage:
    if not application_content or not (application_content.field_errors or birth_date_error):
        user_message = "Ton dossier déposé sur le site demarches-simplifiees.fr contient des erreurs. Tu peux te rendre sur le site pour le rectifier."
    else:
        errors = application_content.field_errors or []
        errors.extend([birth_date_error] if birth_date_error else [])

        user_message = _generate_form_field_error(
            "Il semblerait que ton {formatted_error_fields} soit erroné. Tu peux te rendre sur le site demarches-simplifiees.fr pour le rectifier.",
            "Il semblerait que ta {formatted_error_fields} soit erronée. Tu peux te rendre sur le site demarches-simplifiees.fr pour la rectifier.",
            "Il semblerait que tes {formatted_error_fields} soient erronés. Tu peux te rendre sur le site demarches-simplifiees.fr pour les rectifier.",
            errors,
        )

    return models.SubscriptionMessage(
        user_message=user_message,
        pop_over_icon=None,
        call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
        updated_at=updated_at,
    )


def get_error_not_updatable_message(
    user: users_models.User,
    reason_codes: list[fraud_models.FraudReasonCode],
    application_content: fraud_models.DMSContent | None,
    birth_date_error: fraud_models.DmsFieldErrorDetails | None,
    updated_at: datetime.datetime | None,
) -> models.SubscriptionMessage:
    if not application_content or not (application_content.field_errors or birth_date_error):
        user_message = "Ton dossier déposé sur le site demarches-simplifiees.fr contient des erreurs."
    else:
        user_message = ""
        if application_content.field_errors:
            user_message += _generate_form_field_error(
                "Il semblerait que ton {formatted_error_fields} soit erroné. ",
                "Il semblerait que ta {formatted_error_fields} soit erronée. ",
                "Il semblerait que tes {formatted_error_fields} soient erronés. ",
                application_content.field_errors or [],
            )
        if fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes or birth_date_error:
            user_message += "Ta date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 15 et 18 ans. "

    user_message += "Tu peux contacter le support pour plus d’informations."

    return models.SubscriptionMessage(
        user_message=user_message,
        pop_over_icon=None,
        call_to_action=subscription_messages.compute_support_call_to_action(user.id),
        updated_at=updated_at,
    )


def get_error_processed_message(
    user: users_models.User,
    reason_codes: list[fraud_models.FraudReasonCode],
    application_content: fraud_models.DMSContent | None,
    birth_date_error: fraud_models.DmsFieldErrorDetails | None,
    updated_at: datetime.datetime | None,
) -> models.SubscriptionMessage:
    user_message = "Ton dossier déposé sur le site demarches-simplifiees.fr a été refusé"
    pop_over_icon: models.PopOverIcon | None = models.PopOverIcon.ERROR
    call_to_action: models.CallToActionMessage | None = subscription_messages.compute_support_call_to_action(user.id)

    if fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            user, fraud_models.FraudReasonCode.DUPLICATE_USER, application_content
        )
        pop_over_icon = None

    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            user, fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, application_content
        )
        pop_over_icon = None

    elif fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes or birth_date_error:
        user_message += (
            f"{u_nbsp}: la date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 15 et 18 ans."
        )
        call_to_action = None

    elif (
        fraud_models.FraudReasonCode.EMPTY_ID_PIECE_NUMBER in reason_codes
        or fraud_models.FraudReasonCode.INVALID_ID_PIECE_NUMBER in reason_codes
    ):
        user_message += f"{u_nbsp}: le format du numéro de pièce d'identité renseigné est invalide. Tu peux contacter le support pour plus d'informations."
        pop_over_icon = None

    elif fraud_models.FraudReasonCode.ERROR_IN_DATA in reason_codes or (
        application_content and application_content.field_errors
    ):
        errors = (application_content.field_errors or []) if application_content else []
        errors.extend([birth_date_error] if birth_date_error else [])
        if errors:
            user_message += f"{u_nbsp}:"
            user_message += _generate_form_field_error(
                " le format du {formatted_error_fields} renseigné est invalide.",
                " le format de la {formatted_error_fields} renseignée est invalide.",
                " le format des {formatted_error_fields} renseignés est invalide.",
                errors,
            )
        else:
            user_message += f"{u_nbsp}: il y a une erreur dans les données de ton dossier."
        user_message += " Tu peux contacter le support pour mettre à jour ton dossier."
        pop_over_icon = None
    elif fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR in reason_codes:
        user_message += ". Tu peux contacter le support pour plus d’informations."
    else:
        user_message += "."
        call_to_action = None

    return models.SubscriptionMessage(
        user_message=user_message,
        pop_over_icon=pop_over_icon,
        call_to_action=call_to_action,
        updated_at=updated_at,
    )
