import enum

from pcapi.utils.string import u_nbsp


class UbbleRetryableUserMessage(enum.Enum):
    ID_CHECK_UNPROCESSABLE = "Nous n'arrivons pas à lire ton document. Réessaie avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé."
    ID_CHECK_NOT_AUTHENTIC = "Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaie avec un document original en cours de validité."
    ID_CHECK_NOT_SUPPORTED = "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité."
    ID_CHECK_EXPIRED = "Ton document d'identité est expiré. Réessaie avec un passeport ou une carte d'identité française en cours de validité."
    BLURRY_VIDEO = "Nous n'arrivons pas à lire ton document, les vidéos transmises sont floues. Réessaie la vérification d’identité en t’assurant de la netteté lors de l’envoi."
    NETWORK_CONNECTION_ISSUE = (
        "Nous n’avons pas vu valider ton document. Réessaie en t’assurant d’avoir une bonne connexion à Internet."
    )
    LACK_OF_LUMINOSITY = "Nous n'arrivons pas à lire ton document. Réessaie la vérification d’identité en t’assurant de filmer ton document avec une bonne luminosité."
    DOCUMENT_DAMAGED = "Nous n'arrivons pas à lire ton document. Réessaie la vérification d’identité en t’assurant d’utiliser un document en bon état."
    DEFAULT = "La vérification de ton identité a échoué. Tu peux réessayer."


class UbbleNotRetryableUserMessage(enum.Enum):
    AGE_TOO_OLD = f"Ton dossier a été refusé{u_nbsp}: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans."
    AGE_TOO_YOUNG = f"Ton dossier a été refusé{u_nbsp}: tu n'as pas encore l'âge pour bénéficier du pass Culture. Reviens à tes 15 ans pour profiter de ton crédit."
    ID_CHECK_UNPROCESSABLE = "Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    ID_CHECK_NOT_AUTHENTIC = "Ton dossier a été refusé car le document que tu as présenté n’est pas authentique. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    ID_CHECK_NOT_SUPPORTED = "Le document d'identité que tu as présenté n'est pas accepté. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    ID_CHECK_EXPIRED = "Ton document d'identité est expiré. Rends-toi sur le site demarches-simplifiees.fr avec un document en cours de validité pour renouveler ta demande."
    ID_CHECK_DATA_MATCH = f"Ton dossier a été refusé{u_nbsp}: le prénom et le nom que tu as renseignés ne correspondent pas à ta pièce d'identité. Tu peux contacter le support si tu penses qu’il s’agit d’une erreur."
    ID_CHECK_BLOCKED_OTHER = (
        "Ton dossier a été refusé. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    )
    BLURRY_VIDEO = "Nous n'arrivons pas à lire ton document, les vidéos transmises sont floues. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    NETWORK_CONNECTION_ISSUE = "Nous n’avons pas vu valider ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    LACK_OF_LUMINOSITY = "Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    DOCUMENT_DAMAGED = "Nous n'arrivons pas à lire ton document. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."
    NOT_ELIGIBLE = f"Ton dossier a été refusé{u_nbsp}: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans."
    DEFAULT = "Désolé, la vérification de ton identité n'a pas pu aboutir. Rends-toi sur le site demarches-simplifiees.fr pour renouveler ta demande."


class UbbleRetryableMessageSummary(enum.Enum):
    ID_CHECK_UNPROCESSABLE = "Le document que tu as présenté est illisible."
    ID_CHECK_NOT_AUTHENTIC = "Les copies ne sont pas acceptées."
    ID_CHECK_NOT_SUPPORTED = "Tu n’as pas déposé le bon type de document."
    ID_CHECK_EXPIRED = "Le document que tu as présenté est expiré."
    BLURRY_VIDEO = f"Le document que tu as présenté est illisible{u_nbsp}: les vidéos sont floues."
    NETWORK_CONNECTION_ISSUE = "Ta connexion Internet ne nous a pas permis de valider ton document."
    LACK_OF_LUMINOSITY = f"Le document que tu as présenté est illisible{u_nbsp}: la luminosité est trop faible."
    DOCUMENT_DAMAGED = "Le document que tu as présenté est endommagé."
    DEFAULT = "La vérification de ton identité a échoué."


class UbbleRetryableActionHint(enum.Enum):
    ID_CHECK_UNPROCESSABLE = "Réessaie avec ta pièce d'identité en t'assurant qu'elle soit lisible"
    ID_CHECK_NOT_AUTHENTIC = "Réessaie avec ta carte d’identité ou ton passeport"
    ID_CHECK_NOT_SUPPORTED = "Réessaie avec ta carte d’identité ou ton passeport"
    ID_CHECK_EXPIRED = "Réessaie avec un autre document d’identité valide"
    BLURRY_VIDEO = "Réessaie avec ta pièce d'identité en t'assurant qu'elle soit lisible"
    NETWORK_CONNECTION_ISSUE = "Réessaie en t’assurant d’avoir une bonne connexion Internet"
    LACK_OF_LUMINOSITY = "Réessaie en t’assurant d’avoir une bonne luminosité"
    DOCUMENT_DAMAGED = "Réessaie en t’assurant d’avoir un document original en bon état"
    DEFAULT = "Tu peux réessayer"


class UbbleDetailMessage(enum.Enum):
    AGE_TOO_YOUNG = "L'utilisateur n'a pas encore l'âge requis ({age} ans)"
    AGE_TOO_OLD = "L'utilisateur a dépassé l'âge maximum ({age} ans)"
    ID_CHECK_DATA_MATCH = "Les informations de la pièce d'identité ne correspondent pas"
    ID_CHECK_NOT_SUPPORTED = "Le document d'identité n'est pas supporté"
    ID_CHECK_EXPIRED = "Le document d'identité est expiré"
    ID_CHECK_NOT_AUTHENTIC = "Le document d'identité n'est pas authentique"
    ID_CHECK_UNPROCESSABLE = "Ubble n'a pas réussi à lire le document"
    BLURRY_VIDEO = "La vidéo est floue"
    NETWORK_CONNECTION_ISSUE = "Problème de connexion réseau"
    LACK_OF_LUMINOSITY = "Luminosité insuffisante"
    DOCUMENT_DAMAGED = "Le document est endommagé"
