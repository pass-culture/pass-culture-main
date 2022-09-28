from pcapi import settings
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.common import models as common_fraud_models
from pcapi.core.subscription import models
from pcapi.core.users import models as users_models


MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"

MAINTENANCE_PAGE_MESSAGE = models.SubscriptionMessage(
    user_message="La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
    call_to_action=None,
    pop_over_icon=models.PopOverIcon.CLOCK,
)

REDIRECT_TO_DMS_CALL_TO_ACTION = models.CallToActionMessage(
    title="Accéder au site Démarches-Simplifiées",
    link="passculture://verification-identite/demarches-simplifiees",
    icon=models.CallToActionIcon.EXTERNAL,
)

REDIRECT_TO_IDENTIFICATION_CHOICE = models.CallToActionMessage(
    title="Réessayer la vérification de mon identité",
    link="passculture://verification-identite",
    icon=models.CallToActionIcon.RETRY,
)


def compute_support_call_to_action(user_id: int) -> models.CallToActionMessage:
    return models.CallToActionMessage(
        title="Contacter le support",
        link=MAILTO_SUPPORT + MAILTO_SUPPORT_PARAMS.format(id=user_id),
        icon=models.CallToActionIcon.EMAIL,
    )


def get_generic_ko_message(user_id: int) -> models.SubscriptionMessage:
    return models.SubscriptionMessage(
        user_message="Ton inscription n'a pas pu aboutir. Contacte le support pour plus d'informations",
        call_to_action=compute_support_call_to_action(user_id),
        pop_over_icon=None,
    )


def build_duplicate_error_message(
    user: users_models.User,
    reason_code: fraud_models.FraudReasonCode,
    application_content: common_fraud_models.IdentityCheckContent | None,
) -> str:
    if not application_content:
        return "Contacte le support si tu penses qu'il s'agit d'une erreur."

    anonymized_email = fraud_api.get_duplicate_beneficiary_anonymized_email(user, application_content, reason_code)

    if anonymized_email is None:
        return "Contacte le support si tu penses qu'il s'agit d'une erreur."

    return (
        f"Connecte-toi avec l'adresse {anonymized_email} ou contacte le support si tu penses qu'il s'agit d'une erreur."
    )
