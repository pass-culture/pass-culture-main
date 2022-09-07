import datetime

from pcapi import settings
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models


MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"

FIELD_ERROR_LABELS = {
    fraud_models.DmsFieldErrorKeyEnum.birth_date: "date de naissance",
    fraud_models.DmsFieldErrorKeyEnum.first_name: "prénom",
    fraud_models.DmsFieldErrorKeyEnum.id_piece_number: "numéro de pièce d'identité",
    fraud_models.DmsFieldErrorKeyEnum.last_name: "nom de famille",
    fraud_models.DmsFieldErrorKeyEnum.postal_code: "code postal",
}


def _generate_form_field_error(
    error_text_singular: str, error_text_plural: str, error_fields: list[fraud_models.DmsFieldErrorDetails]
) -> str:
    field_text = ", ".join(FIELD_ERROR_LABELS.get(field.key, field.key.value) for field in error_fields)
    if len(error_fields) == 1:
        user_message = error_text_singular.format(formatted_error_fields=field_text)
    else:
        user_message = error_text_plural.format(formatted_error_fields=field_text)

    return user_message


def get_application_received_message(reception_datetime: datetime.datetime) -> models.SubscriptionMessage:
    return models.SubscriptionMessage(
        user_message=f"Nous avons bien reçu ton dossier le {reception_datetime.date():%d/%m/%Y}. Rends-toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel.",
        pop_over_icon=models.PopOverIcon.FILE,
        call_to_action=None,
    )


def get_error_updatable_message(
    application_content: fraud_models.DMSContent | None,
    birth_date_error: fraud_models.DmsFieldErrorDetails | None,
) -> models.SubscriptionMessage:
    if not application_content or not (application_content.field_errors or birth_date_error):
        user_message = "Ton dossier déposé sur le site Démarches-Simplifiées contient des erreurs. Tu peux te rendre sur le site pour le rectifier."
    else:
        errors = application_content.field_errors or []
        errors.extend([birth_date_error] if birth_date_error else [])

        user_message = _generate_form_field_error(
            "Il semblerait que le champ ‘{formatted_error_fields}’ soit invalide. Tu peux te rendre sur le site Démarches-simplifiées pour le rectifier.",
            "Il semblerait que les champs ‘{formatted_error_fields}’ soient invalides. Tu peux te rendre sur le site Démarches-simplifiées pour les rectifier.",
            errors,
        )

    return models.SubscriptionMessage(
        user_message=user_message,
        pop_over_icon=None,
        call_to_action=subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION,
    )


def get_error_not_updatable_message(
    user_id: int,
    reason_codes: list[fraud_models.FraudReasonCode],
    application_content: fraud_models.DMSContent | None,
    birth_date_error: fraud_models.DmsFieldErrorDetails | None,
) -> models.SubscriptionMessage:
    user_message = "Ton dossier déposé sur le site Démarches-Simplifiées a été refusé"
    pop_over_icon: models.PopOverIcon | None = models.PopOverIcon.ERROR
    call_to_action = None
    if (
        fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes
        or fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes
    ):
        user_message += " : il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations."
        call_to_action = subscription_messages.compute_support_call_to_action(user_id)
        pop_over_icon = None  # TODO: viconnex: ask frontend if we need to override with null value

    elif fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes or birth_date_error:
        user_message += " : la date de naissance indique que tu n'es pas éligible. Tu dois avoir entre 15 et 18 ans."

    elif fraud_models.FraudReasonCode.ERROR_IN_DATA in reason_codes or (
        application_content and application_content.field_errors
    ):
        errors = (application_content.field_errors or []) if application_content else []
        errors.extend([birth_date_error] if birth_date_error else [])
        if errors:
            user_message += _generate_form_field_error(
                " : le champ ‘{formatted_error_fields}’ est invalide.",
                " : les champs ‘{formatted_error_fields}’ sont invalides.",
                errors,
            )
        else:
            user_message += " : il y a une erreur dans les données de ton dossier."
    elif fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR in reason_codes:
        user_message += " : tu n'es malheureusement pas éligible au pass Culture."
    else:
        user_message += "."

    return models.SubscriptionMessage(
        user_message=user_message,
        pop_over_icon=pop_over_icon,
        call_to_action=call_to_action,
    )
