import datetime
import typing

from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.common import models as common_fraud_models
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models


PENDING_UBBLE_SUBSCRIPTION_MESSAGE = subscription_models.SubscriptionMessage(
    user_message="Ton document d'identité est en cours de vérification.",
    call_to_action=None,
    pop_over_icon=subscription_models.PopOverIcon.CLOCK,
)

REDIRECT_TO_IDENTIFICATION = subscription_models.CallToActionMessage(
    title="Réessayer la vérification de mon identité",
    link="passculture://verification-identite/identification",
    icon=subscription_models.CallToActionIcon.RETRY,
)


def get_application_pending_message(updated_at: datetime.datetime | None) -> subscription_models.SubscriptionMessage:
    return subscription_models.SubscriptionMessage(
        user_message="Ton document d'identité est en cours de vérification.",
        call_to_action=None,
        pop_over_icon=subscription_models.PopOverIcon.CLOCK,
        updated_at=updated_at,
    )


def get_ubble_retryable_message(
    reason_codes: list[fraud_models.FraudReasonCode], updated_at: datetime.datetime | None
) -> subscription_models.SubscriptionMessage:
    call_to_action = REDIRECT_TO_IDENTIFICATION

    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        user_message = "Nous n'arrivons pas à lire ton document. Réessaye avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé."
    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        user_message = "Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaye avec un document original en cours de validité."
    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        user_message = "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité."
        call_to_action = subscription_messages.REDIRECT_TO_IDENTIFICATION_CHOICE
    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        user_message = "Ton document d'identité est expiré. Réessaye avec un passeport ou une carte d'identité française en cours de validité."
    else:
        user_message = "La vérification de ton identité a échoué. Tu peux réessayer."

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=call_to_action,
        pop_over_icon=None,
        updated_at=updated_at,
    )


def get_ubble_not_retryable_message(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> subscription_models.SubscriptionMessage:
    reason_codes = fraud_check.reasonCodes or []
    if fraud_check.resultContent:
        identity_content = typing.cast(common_fraud_models.IdentityCheckContent, fraud_check.source_data())
    else:
        identity_content = None

    call_to_action = None
    pop_over_icon = None
    if fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE in reason_codes:
        user_message = "Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC in reason_codes:
        user_message = "Ton dossier a été refusé car le document que tu as présenté n’est pas authentique. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED in reason_codes:
        user_message = "Le document d'identité que tu as présenté n'est pas accepté. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.ID_CHECK_EXPIRED in reason_codes:
        user_message = "Ton document d'identité est expiré. Rends-toi sur le site demarches-simplifiees.fr avec un document en cours de validité pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    elif fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            fraud_check.user, fraud_models.FraudReasonCode.DUPLICATE_USER, identity_content
        )
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        user_message = subscription_messages.build_duplicate_error_message(
            fraud_check.user, fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER, identity_content
        )
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

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
        user_message = "Ton dossier a été refusé : le prénom et le nom que tu as renseignés ne correspondent pas à ta pièce d'identité. Tu peux contacter le support si tu penses qu’il s’agit d’une erreur."
        call_to_action = subscription_messages.compute_support_call_to_action(fraud_check.user.id)

    elif fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER in reason_codes:
        user_message = (
            "Ton dossier a été refusé. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
        )
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    else:
        user_message = "Désolé, la vérification de ton identité n'a pas pu aboutir. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
        call_to_action = subscription_messages.REDIRECT_TO_DMS_CALL_TO_ACTION

    return subscription_models.SubscriptionMessage(
        user_message=user_message,
        call_to_action=call_to_action,
        pop_over_icon=pop_over_icon,
        updated_at=fraud_check.updatedAt,
    )
