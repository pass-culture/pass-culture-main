import enum


class UbbleRetryableUserMessage(enum.Enum):
    ID_CHECK_UNPROCESSABLE = "Nous n'arrivons pas à lire ton document. Réessaye avec un passeport ou une carte d'identité française en cours de validité dans un lieu bien éclairé."
    ID_CHECK_NOT_AUTHENTIC = "Le document que tu as présenté n’est pas accepté car il s’agit d’une photo ou d’une copie de l’original. Réessaye avec un document original en cours de validité."
    ID_CHECK_NOT_SUPPORTED = "Le document d'identité que tu as présenté n'est pas accepté. S’il s’agit d’une pièce d’identité étrangère ou d’un titre de séjour français, tu dois passer par le site demarches-simplifiees.fr. Si non, tu peux réessayer avec un passeport ou une carte d’identité française en cours de validité."
    ID_CHECK_EXPIRED = "Ton document d'identité est expiré. Réessaye avec un passeport ou une carte d'identité française en cours de validité."
    DEFAULT = "La vérification de ton identité a échoué. Tu peux réessayer."


class UbbleRetryableMessageSummary(enum.Enum):
    ID_CHECK_UNPROCESSABLE = "Le document que tu as présenté est illisible."
    ID_CHECK_NOT_AUTHENTIC = "Les copies ne sont pas acceptées."
    ID_CHECK_NOT_SUPPORTED = "Tu n’as pas déposé le bon type de document."
    ID_CHECK_EXPIRED = "Le document que tu as présenté est expiré."
    DEFAULT = "La vérification de ton identité a échoué."


class UbbleRetryableActionHint(enum.Enum):
    ID_CHECK_UNPROCESSABLE = "Réessaie avec ta pièce d'identité en t'assurant qu'elle soit lisible"
    ID_CHECK_NOT_AUTHENTIC = "Réessaie avec ta carte d’identité ou ton passeport"
    ID_CHECK_NOT_SUPPORTED = "Réessaie avec ta carte d’identité ou ton passeport"
    ID_CHECK_EXPIRED = "Réessaie avec un autre document d’identité valide"
    DEFAULT = "Tu peux réessayer."
