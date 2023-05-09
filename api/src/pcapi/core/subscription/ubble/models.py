import dataclasses

from pcapi.core.fraud import models as fraud_models
from pcapi.utils.string import u_nbsp


@dataclasses.dataclass
class UbbleError:
    detail_message: str = ""
    not_retryable_user_message: str = "Désolé, la vérification de ton identité n'a pas pu aboutir. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    retryable_action_hint: str = "Tu peux réessayer"
    retryable_message_summary: str = "La vérification de ton identité a échoué."
    retryable_user_message: str = "La vérification de ton identité a échoué. Tu peux réessayer."
    priority: int = 0


UBBLE_DEFAULT = UbbleError()

UBBLE_CODE_ERROR_MAPPING = {
    fraud_models.FraudReasonCode.AGE_TOO_OLD: UbbleError(
        detail_message="L'utilisateur a dépassé l'âge maximum ({age} ans)",
        not_retryable_user_message=f"Ton dossier a été refusé{u_nbsp}: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
        priority=50,
    ),
    fraud_models.FraudReasonCode.AGE_TOO_YOUNG: UbbleError(
        detail_message="L'utilisateur n'a pas encore l'âge requis ({age} ans)",
        not_retryable_user_message=f"Ton dossier a été refusé{u_nbsp}: tu n'as pas encore l'âge pour bénéficier du pass Culture. Reviens à tes 15 ans pour profiter de ton crédit.",
        priority=50,
    ),
    fraud_models.FraudReasonCode.BLURRY_VIDEO: UbbleError(
        detail_message="La vidéo est floue",
        not_retryable_user_message="Nous n'arrivons pas à lire ton document, les vidéos transmises sont floues. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie avec ta pièce d'identité en t'assurant qu'elle soit lisible",
        retryable_message_summary=f"Le document que tu as présenté est illisible{u_nbsp}: les vidéos sont floues.",
        retryable_user_message="Nous n'arrivons pas à lire ton document, les vidéos transmises sont floues. Réessaie la vérification d’identité en t’assurant de la netteté lors de l’envoi.",
        priority=30,
    ),
    fraud_models.FraudReasonCode.DOCUMENT_DAMAGED: UbbleError(
        detail_message="Le document est endommagé",
        not_retryable_user_message="Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie en t’assurant d’avoir un document original en bon état",
        retryable_message_summary="Le document que tu as présenté est endommagé.",
        retryable_user_message="Nous n'arrivons pas à lire ton document. Réessaie la vérification d’identité en t’assurant d’utiliser un document en bon état.",
        priority=30,
    ),
    fraud_models.FraudReasonCode.DUPLICATE_USER: UbbleError(
        not_retryable_user_message="",
        priority=60,
    ),
    fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER: UbbleError(
        not_retryable_user_message="",
        priority=60,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER: UbbleError(
        not_retryable_user_message="Ton dossier a été refusé. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        priority=10,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH: UbbleError(
        detail_message="Les informations de la pièce d'identité ne correspondent pas",
        not_retryable_user_message=f"Ton dossier a été refusé{u_nbsp}: le prénom et le nom que tu as renseignés ne correspondent pas à ta pièce d'identité. Tu peux contacter le support si tu penses qu’il s’agit d’une erreur.",
        priority=40,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED: UbbleError(
        detail_message="Le document d'identité est expiré",
        not_retryable_user_message="Ton document d'identité est expiré. Rends-toi sur le site demarches-simplifiees.fr avec un document en cours de validité pour renouveler ta demande.",
        retryable_action_hint="Réessaie avec un autre document d’identité valide",
        retryable_message_summary="Le document que tu as présenté est expiré.",
        retryable_user_message="Ton document d'identité est expiré. Réessaie avec un passeport ou une carte d'identité française en cours de validité.",
        priority=70,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC: UbbleError(
        detail_message="Le document d'identité n'est pas authentique",
        not_retryable_user_message="Ton dossier a été refusé car le document que tu as présenté n’est pas authentique. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie avec ta carte d’identité ou ton passeport",
        retryable_message_summary="Les copies ne sont pas acceptées.",
        retryable_user_message="Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaie avec un document original en cours de validité.",
        priority=90,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED: UbbleError(
        detail_message="Le document d'identité n'est pas supporté",
        not_retryable_user_message="Le document d'identité que tu as présenté n'est pas accepté. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie avec ta carte d’identité ou ton passeport",
        retryable_message_summary="Tu n’as pas déposé le bon type de document.",
        retryable_user_message="Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité.",
        priority=80,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE: UbbleError(
        detail_message="Ubble n'a pas réussi à lire le document",
        not_retryable_user_message="Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie avec ta pièce d'identité en t'assurant qu'elle soit lisible",
        retryable_message_summary="Le document que tu as présenté est illisible.",
        retryable_user_message="Nous n'arrivons pas à lire ton document. Réessaie avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé.",
        priority=100,
    ),
    fraud_models.FraudReasonCode.LACK_OF_LUMINOSITY: UbbleError(
        detail_message="Luminosité insuffisante",
        not_retryable_user_message="Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie en t’assurant d’avoir une bonne luminosité",
        retryable_message_summary=f"Le document que tu as présenté est illisible{u_nbsp}: la luminosité est trop faible.",
        retryable_user_message="Nous n'arrivons pas à lire ton document. Réessaie la vérification d’identité en t’assurant de filmer ton document avec une bonne luminosité.",
        priority=30,
    ),
    fraud_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE: UbbleError(
        detail_message="Problème de connexion réseau",
        not_retryable_user_message="Nous n’avons pas vu valider ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande.",
        retryable_action_hint="Réessaie en t’assurant d’avoir une bonne connexion Internet",
        retryable_message_summary="Ta connexion Internet ne nous a pas permis de valider ton document.",
        retryable_user_message="Nous n’avons pas vu valider ton document. Réessaie en t’assurant d’avoir une bonne connexion à Internet.",
        priority=30,
    ),
    fraud_models.FraudReasonCode.NOT_ELIGIBLE: UbbleError(
        not_retryable_user_message=f"Ton dossier a été refusé{u_nbsp}: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
        priority=50,
    ),
}
