import logging

from pcapi import settings
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


SUBSCRIPTION_SUPPORT_FORM_URL = "https://aide.passculture.app/hc/fr/requests/new?ticket_form_id=20669662761500"

MAINTENANCE_PAGE_MESSAGE = subscription_schemas.SubscriptionMessage(
    user_message="La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
    call_to_action=None,
    pop_over_icon=subscription_schemas.PopOverIcon.CLOCK,
)

REDIRECT_TO_DMS_CALL_TO_ACTION = subscription_schemas.CallToActionMessage(
    title="Accéder au site Démarche Numérique",
    link=f"{settings.WEBAPP_V2_URL}/verification-identite/demarches-simplifiees",
    icon=subscription_schemas.CallToActionIcon.EXTERNAL,
)

REDIRECT_TO_IDENTIFICATION_CHOICE = subscription_schemas.CallToActionMessage(
    title="Réessayer la vérification de mon identité",
    link=f"{settings.WEBAPP_V2_URL}/verification-identite",
    icon=subscription_schemas.CallToActionIcon.RETRY,
)


def compute_support_call_to_action(user_id: int) -> subscription_schemas.CallToActionMessage:
    return subscription_schemas.CallToActionMessage(
        title="Contacter le support",
        link=SUBSCRIPTION_SUPPORT_FORM_URL,
        icon=subscription_schemas.CallToActionIcon.EXTERNAL,
    )


def get_generic_ko_message(user_id: int) -> subscription_schemas.SubscriptionMessage:
    return subscription_schemas.SubscriptionMessage(
        user_message="Ton inscription n'a pas pu aboutir. Contacte le support pour plus d'informations",
        call_to_action=compute_support_call_to_action(user_id),
        pop_over_icon=None,
    )


def build_duplicate_error_message(
    user: users_models.User,
    reason_code: subscription_models.FraudReasonCode,
    application_content: subscription_schemas.IdentityCheckContent | None,
) -> str:
    match reason_code:
        case subscription_models.FraudReasonCode.DUPLICATE_INE:
            message_start = "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé aux identifiants ÉduConnect que tu as fournis."
        case subscription_models.FraudReasonCode.DUPLICATE_USER:
            message_start = "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom."
        case subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER:
            message_start = "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé à ce numéro de pièce d’identité."
        case _:
            logger.error("Duplicate error with no matching body message %s", reason_code)
            message_start = "Ton dossier a été refusé car tu as déjà un compte bénéficiaire"

    contact_support_message = "Contacte le support si tu penses qu’il s’agit d’une erreur."
    message_end = "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."

    default_message = f"{message_start} {contact_support_message} {message_end}"

    if not application_content:
        return default_message

    anonymized_email = fraud_api.get_duplicate_beneficiary_anonymized_email(user, application_content, reason_code)
    if anonymized_email is None:
        return default_message

    return f"{message_start} Connecte-toi avec l’adresse mail {anonymized_email} ou {contact_support_message.lower()} {message_end}"
