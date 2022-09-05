import datetime

from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import constants as users_constants


REDIRECT_TO_STEPPER_LINK = "passculture://verification-identite"

RETRY_CALL_TO_ACTION = subscription_models.CallToActionMessage(
    title="Réessayer la vérification de mon identité",
    link=REDIRECT_TO_STEPPER_LINK,
    icon=subscription_models.CallToActionIcon.RETRY,
)


def get_educonnect_failure_subscription_message(
    reason_codes: list[fraud_models.FraudReasonCode], birth_date: datetime.date | None, user_id: int
) -> subscription_models.SubscriptionMessage:
    if (
        fraud_models.FraudReasonCode.AGE_NOT_VALID in reason_codes
        or fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes
    ) and birth_date:
        user_message = f"Ton dossier a été refusé. La date de naissance sur ton compte Éduconnect ({birth_date.strftime('%d/%m/%Y')}) indique que tu n'as pas entre {users_constants.ELIGIBILITY_UNDERAGE_RANGE[0]} et {users_constants.ELIGIBILITY_UNDERAGE_RANGE[-1]} ans."

    elif fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        user_message = "Ton dossier a été refusé : il y a déjà un compte à ton nom sur le pass Culture."

    elif fraud_models.FraudReasonCode.DUPLICATE_INE in reason_codes:
        user_message = "Ton dossier a été refusé : Ton identifiant national INE est déjà rattaché à un autre compte pass Culture. Vérifie que tu n'as pas déjà créé un compte avec une autre adresse e-mail."

    else:
        user_message = "La vérification de ton identité a échoué. Tu peux réessayer."

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=RETRY_CALL_TO_ACTION,
    )
