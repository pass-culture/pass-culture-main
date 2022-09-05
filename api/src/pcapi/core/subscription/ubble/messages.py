from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models


PENDING_UBBLE_SUBSCRIPTION_MESSAGE = subscription_models.SubscriptionMessage(
    user_message="Ton document d'identité est en cours de vérification.",
    call_to_action=None,
    pop_over_icon=subscription_models.PopOverIcon.CLOCK,
)

REDIRECT_TO_IDENTIFICATION_LINK = "passculture://verification-identite/identification"


def get_ubble_retryable_message(
    reason_codes: list[fraud_models.FraudReasonCode],
) -> subscription_models.SubscriptionMessage:
    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        user_message = "Nous n'arrivons pas à lire ton document. Réessaye avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé."
    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        user_message = "Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaye avec un document original en cours de validité."
    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        user_message = "Ton document d'identité ne te permet pas de bénéficier du pass Culture. Réessaye avec un passeport ou une carte d'identité française en cours de validité."
    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        user_message = "Ton document d'identité est expiré. Réessaye avec un passeport ou une carte d'identité française en cours de validité."
    else:
        user_message = "La vérification de ton identité a échoué. Tu peux réessayer."

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=subscription_models.CallToActionMessage(
            title="Réessayer la vérification de mon identité",
            link=REDIRECT_TO_IDENTIFICATION_LINK,
            icon=subscription_models.CallToActionIcon.RETRY,
        ),
        pop_over_icon=None,
    )


def get_ubble_not_retryable_message(
    reason_codes: list[fraud_models.FraudReasonCode], user_id: int
) -> subscription_models.SubscriptionMessage:
    call_to_action = None
    pop_over_icon = None
    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        user_message = "Nous n'arrivons pas à lire ton document. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        user_message = "Ton dossier a été refusé car le document que tu as présenté n’est pas authentique. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        user_message = "Ton document d'identité ne te permet pas de bénéficier du pass Culture. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        user_message = "Ton document d'identité est expiré. Rends-toi sur le site Démarches-Simplifiées avec un document en cours de validité pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif (
        fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes
        or fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes
    ):
        user_message = "Ton dossier a été refusé : il y a déjà un compte à ton nom sur le pass Culture. Tu peux contacter le support pour plus d'informations."
        call_to_action = subscription_messages.compute_support_call_to_action(user_id)

    elif fraud_models.FraudReasonCode.AGE_TOO_YOUNG in reason_codes:
        user_message = "Ton dossier a été refusé : tu n'as pas encore l'âge pour bénéficier du pass Culture. Reviens à tes 15 ans pour profiter de ton crédit."
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif fraud_models.FraudReasonCode.AGE_TOO_OLD in reason_codes:
        user_message = "Ton dossier a été refusé : tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans."
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes:
        user_message = "Ton dossier a été refusé : tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans."
        pop_over_icon = subscription_models.PopOverIcon.ERROR

    elif fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH in reason_codes:
        user_message = "Ton dossier a été refusé : le prénom et le nom que tu as renseignés ne correspondent pas à ta pièce d'identité. Tu peux contacter le support pour plus d'informations."
        call_to_action = subscription_messages.compute_support_call_to_action(user_id)

    elif fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER in reason_codes:
        user_message = (
            "Ton dossier a été refusé. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande."
        )
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    else:
        user_message = (
            "Ton dossier a été refusé. Rends-toi sur le site Démarches-Simplifiées pour renouveler ta demande."
        )
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=call_to_action,
        pop_over_icon=pop_over_icon,
    )
