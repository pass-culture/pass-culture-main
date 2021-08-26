import copy
from typing import Optional


APPLICATION_DETAIL_STANDARD_RESPONSE = {
    "dossier": {
        "id": 123,
        "created_at": "2020-04-17T07:18:22.534Z",
        "updated_at": "2020-04-17T07:20:33.051Z",
        "archived": False,
        "email": "john.doe@test.com",
        "state": "closed",
        "simplified_state": "Accepté",
        "initiated_at": "2020-04-17T07:20:31.996Z",
        "received_at": None,
        "processed_at": None,
        "motivation": None,
        "instructeurs": [],
        "individual": {"civilite": "M.", "nom": "Doe", "prenom": "John"},
        "entreprise": None,
        "etablissement": None,
        "cerfa": [],
        "commentaires": [
            {
                "email": "contact@demarches-simplifiees.fr",
                "body": '[Votre préinscription pour le pass Culture a bien été reçue]\u003cbr\u003e\u003cbr\u003e\u003cp\u003e\r\nBonjour Adrien,\u003c/p\u003e\r\n\u003cp\u003e\r\nL\'équipe du pass Culture vous confirme la bonne réception de votre dossier nº 1613447. \u003c/p\u003e\u003cp\u003eVotre dossier sera examiné \u003cb\u003edans les semaines à venir\u003c/b\u003e. Un mail de confirmation vous sera envoyé à l’ouverture de votre pass Culture. À tout moment, vous pouvez consulter l\'avancée de votre dossier : \u003ca target="_blank" rel="noopener" href="https://www.demarches-simplifiees.fr/dossiers/1613447"\u003ehttps://www.demarches-simplifiees.fr/dossiers/1613447\u003c/a\u003e\u003c/p\u003e\u003cp\u003eNous vous invitons à consulter notre FAQ, vous y trouverez toutes les informations relatives au pass Culture : \u003ca target="_blank" rel="nofollow" href="https://docs.passculture.app/experimentateurs/pre-inscription-au-pass-culture"\u003ehttps://aide.passculture.app/fr/article/18-ans-ma-pre-inscription-au-pass-culture-fj3mqc/\u003c/a\u003e\u003c/p\u003e\u003cp\u003eVous avez des questions ? Vous pouvez échanger directement avec nous à cette adresse : \u003cb\u003esupport@passculture.app\u003c/b\u003e\u003cbr\u003e\u003c/p\u003e\u003cp\u003eBonne journée,\u003cbr\u003e\u003c/p\u003e\u003cp\u003eL\'équipe du pass Culture\u003c/p\u003e',
                "created_at": "2020-04-17T07:20:33.049Z",
                "offerer_attachment_validationhment": None,
            }
        ],
        "champs_private": [],
        "pieces_justificatives": [],
        "types_de_piece_justificative": [],
        "avis": [],
        "champs": [
            {
                "value": None,
                "type_de_champ": {
                    "id": 609447,
                    "libelle": "Comment remplir ce formulaire de pré-inscription au pass Culture",
                    "type_champ": "explication",
                    "order_place": 0,
                    "description": "Une aide pour remplir votre dossier est disponible ici : https://aide.passculture.app/fr/article/18-ans-ma-pre-inscription-au-pass-culture-fj3mqc/​",
                },
            },
            {
                "value": "93 - Seine-Saint-Denis",
                "type_de_champ": {
                    "id": 596453,
                    "libelle": "Veuillez indiquer votre département de résidence",
                    "type_champ": "drop_down_list",
                    "order_place": 1,
                    "description": "Attention, si votre département ne se trouve pas dans cette liste, c'est que vous n'êtes malheureusement pas encore éligible au pass Culture.",
                },
            },
            {
                "value": "2000-05-01",
                "type_de_champ": {
                    "id": 582220,
                    "libelle": "Quelle est votre date de naissance",
                    "type_champ": "date",
                    "order_place": 2,
                    "description": "Le pass Culture n'est éligible qu'aux personnes ayant 18 ans.",
                },
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 718222,
                    "libelle": "Pièces justificatives acceptées",
                    "type_champ": "explication",
                    "order_place": 3,
                    "description": "Pour valider votre inscription, vous devez obligatoirement fournir l'un des documents suivants :\n - carte nationale d'identité ou passeport français ;\n - carte nationale d'identité ou passeport de l'un des Etats membres de l'Union européenne ou de l'un des Etats parties à l'accord sur l'Espace économique européen ou de la Confédération suisse ;\n - titre de séjour français.",
                },
            },
            {
                "value": "http://fake.url",
                "type_de_champ": {
                    "id": 459819,
                    "libelle": "Pièce d'identité (photocopie de la page avec votre photo)",
                    "type_champ": "piece_justificative",
                    "order_place": 4,
                    "description": "Vos nom, prénom et date de naissance doivent être clairement identifiables. \nN'envoyez PAS le verso de votre carte d'identité ni la couverture de votre passeport.",
                },
            },
            {
                "value": "0123456789",
                "type_de_champ": {
                    "id": 582219,
                    "libelle": "Quel est votre numéro de téléphone",
                    "type_champ": "phone",
                    "order_place": 5,
                    "description": "",
                },
            },
            {
                "value": 93130,
                "type_de_champ": {
                    "id": 582221,
                    "libelle": "Quel est le code postal de votre commune de résidence ?",
                    "type_champ": "integer_number",
                    "order_place": 6,
                    "description": None,
                },
            },
            {
                "value": "35 Rue Saint Denis 93130 Noisy-le-Sec",
                "type_de_champ": {
                    "id": 582223,
                    "libelle": "Quelle est votre adresse de résidence",
                    "type_champ": "address",
                    "order_place": 7,
                    "description": None,
                },
            },
            {
                "value": "Employé",
                "type_de_champ": {
                    "id": 718094,
                    "libelle": "Veuillez indiquer votre statut",
                    "type_champ": "drop_down_list",
                    "order_place": 8,
                    "description": "",
                },
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451284,
                    "libelle": "Déclaration de résidence",
                    "type_champ": "header_section",
                    "order_place": 9,
                    "description": "",
                },
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 582328,
                    "libelle": "Certification sur l'honneur",
                    "type_champ": "explication",
                    "order_place": 10,
                    "description": "Le pass Culture est actuellement en phase d'expérimentation, et n'est disponible que dans certains départements pilotes. Il s'étendra progressivement à l'ensemble du territoire français.\n\nLa liste des départements ouverts à l'expérimentation du pass Culture est disponible ici : https://aide.passculture.app/fr/article/18-ans-puis-je-beneficier-du-pass-culture-16uinm8/",
                },
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 718106,
                    "libelle": "Je certifie sur l’honneur résider dans l'un des départements ouverts à l'expérimentation du pass Culture.",
                    "type_champ": "engagement",
                    "order_place": 11,
                    "description": "Des contrôles aléatoires seront effectués et vous devrez alors fournir un justificatif de domicile. En cas de fraude, vous vous exposez à des poursuites judiciaires.",
                },
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 718254,
                    "libelle": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                    "type_champ": "engagement",
                    "order_place": 12,
                    "description": "Cette condition est obligatoire si vous n'êtes pas un ressortissant de l'un des Etats membres de l'Union européenne ou de l'un des Etats parties à l'accord sur l'Espace économique européen ou de la Confédération suisse.",
                },
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 466695,
                    "libelle": "Consentement à l'utilisation de mes données",
                    "type_champ": "header_section",
                    "order_place": 13,
                    "description": "",
                },
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 466635,
                    "libelle": "Que faisons-nous de ces données ?",
                    "type_champ": "explication",
                    "order_place": 14,
                    "description": "Ces données sont utilisées à la seule fin de nous assurer de votre éligibilité à l'expérimentation du pass Culture. Vos données seront contrôlées par l'équipe du pass Culture, puis conservées pendant un an à des fins de contrôle a posteriori.",
                },
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 466694,
                    "libelle": "Je donne mon accord au traitement de mes données à caractère personnel dans les conditions explicitées ci-dessus",
                    "type_champ": "engagement",
                    "order_place": 15,
                    "description": "",
                },
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 457303,
                    "libelle": "Je déclare sur l’honneur que ces documents sont authentiques. ",
                    "type_champ": "engagement",
                    "order_place": 16,
                    "description": "",
                },
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 454775,
                    "libelle": "Un grand merci et à très vite sur le pass Culture !",
                    "type_champ": "header_section",
                    "order_place": 17,
                    "description": "",
                },
            },
        ],
    }
}


def make_new_beneficiary_application_details(
    application_id: int,
    state: str,
    postal_code: int = 67200,
    department_code: str = "67 - Bas-Rhin",
    civility: str = "Mme",
    activity: str = "Étudiant",
    id_piece_number: Optional[str] = None,
) -> dict:
    application = copy.deepcopy(APPLICATION_DETAIL_STANDARD_RESPONSE)
    application["dossier"]["id"] = application_id
    application["dossier"]["state"] = state
    application["dossier"]["individual"]["civilite"] = civility
    for field in application["dossier"]["champs"]:
        if field["type_de_champ"]["libelle"] == "Veuillez indiquer votre département de résidence":
            field["value"] = department_code
        if field["type_de_champ"]["libelle"] == "Quel est le code postal de votre commune de résidence ?":
            field["value"] = postal_code
        if field["type_de_champ"]["libelle"] == "Veuillez indiquer votre statut":
            field["value"] = activity

    if id_piece_number:
        application["dossier"]["champs"].append(
            {
                "value": id_piece_number,
                "type_de_champ": {
                    "id": 123123,
                    "libelle": "Quel est le numéro de la pièce que vous venez de saisir ?",
                    "type_champ": "unknown",
                    "order_place": 123,
                    "description": "WIP",
                },
            }
        )
    return application
