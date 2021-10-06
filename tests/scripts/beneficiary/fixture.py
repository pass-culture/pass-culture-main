import copy
import random
import string
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
    email: Optional[str] = None,
) -> dict:
    application = copy.deepcopy(APPLICATION_DETAIL_STANDARD_RESPONSE)
    application["dossier"]["id"] = application_id
    application["dossier"]["state"] = state
    application["dossier"]["individual"]["civilite"] = civility
    if email:
        application["dossier"]["email"] = email
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


def make_graphql_application(
    application_id: int,
    state: str,
    postal_code: int = 67200,
    department_code: str = "67 - Bas-Rhin",
    civility: str = "Mme",
    activity: str = "Étudiant",
    id_piece_number: Optional[str] = "123123123",
    email: Optional[str] = "young.individual@example.com",
    full_graphql_response: bool = False,
    has_next_page: bool = False,
) -> dict:
    data = {
        "id": "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)),
        "number": application_id,
        "archived": False,
        "state": state,
        "dateDerniereModification": "2020-05-13T10:41:23+02:00",
        "datePassageEnConstruction": "2020-05-13T09:09:46+02:00",
        "datePassageEnInstruction": "2020-05-13T10:37:31+02:00",
        "dateTraitement": "2020-05-13T10:41:21+02:00",
        "motivation": "",
        "motivationAttachment": None,
        "attestation": None,
        "instructeurs": [{"email": "instructor@example.com", "id": "SomeRandomId"}],
        "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItMjYxMzg=", "number": 2613, "label": "défaut"},
        "champs": [
            {
                "id": "Q2hhbXAtNjA5NDQ3",
                "label": "Comment remplir ce formulaire de pré-inscription au pass Culture",
                "stringValue": "",
            },
            {
                "id": "Q2hhbXAtNTk2NDUz",
                "label": "Veuillez indiquer votre département de résidence",
                "stringValue": department_code,
            },
            {"id": "Q2hhbXAtNTgyMjIw", "label": "Quelle est votre date de naissance", "stringValue": "12 mai 2002"},
            {"id": "Q2hhbXAtNzE4MjIy", "label": "Pièces justificatives acceptées", "stringValue": ""},
            {
                "id": "Q2hhbXAtNDU5ODE5",
                "label": "Pièce d'identité (photocopie de la page avec votre photo)",
                "stringValue": "",
                "file": {
                    "filename": "Carte Identité THOMAS MERLE.PDF",
                    "url": "https://some.url.example.com",
                },
            },
            {
                "id": "Q2hhbXAtMTg3Mzc0Mw==",
                "label": "Quel est le numéro de la pièce que vous venez de saisir ?",
                "stringValue": id_piece_number,
            },
            {"id": "Q2hhbXAtNTgyMjE5", "label": "Quel est votre numéro de téléphone", "stringValue": "07 83 44 23 76"},
            {
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de votre commune de résidence ?",
                "stringValue": postal_code,
            },
            {
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est votre adresse de résidence",
                "stringValue": "3 La Bigotais 22800 Saint-Donan",
            },
            {"id": "Q2hhbXAtNzE4MDk0", "label": "Veuillez indiquer votre statut", "stringValue": activity},
            {"id": "Q2hhbXAtNDUxMjg0", "label": "Déclaration de résidence", "stringValue": ""},
            {"id": "Q2hhbXAtNTgyMzI4", "label": "Certification sur l'honneur", "stringValue": ""},
            {
                "id": "Q2hhbXAtNzE4MTA2",
                "label": "Je certifie sur l’honneur résider dans l'un des départements ouverts à l'expérimentation du pass Culture.",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNzE4MjU0",
                "label": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                "stringValue": "true",
            },
            {"id": "Q2hhbXAtNDY2Njk1", "label": "Consentement à l'utilisation de mes données", "stringValue": ""},
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
            },
        ],
        "annotations": [],
        "usager": {"email": email},
        "demandeur": {"civilite": civility, "nom": "Doe", "prenom": "John", "dateDeNaissance": None},
    }
    if full_graphql_response:
        enveloppe = {
            "demarche": {
                "dossiers": {"nodes": [], "pageInfo": {"endCursor": "MTc", "hasNextPage": has_next_page}},
                "id": "UHJvY2VkdXJlLTQ0Njgy",
                "number": 44682,
            }
        }
        enveloppe["demarche"]["dossiers"]["nodes"] = [data]
        return enveloppe
    return data


def make_new_application():

    response = {
        "id": "RG9zc2llci01NzE4MzAz",
        "number": 5718303,
        "archived": False,
        "state": "en_construction",
        "dateDerniereModification": "2021-09-14T16:02:33+02:00",
        "datePassageEnConstruction": "2021-09-14T16:02:32+02:00",
        "datePassageEnInstruction": None,
        "dateTraitement": None,
        "motivation": None,
        "motivationAttachment": None,
        "attestation": None,
        "pdf": {
            "url": "https://example.com/some/path/to/application.pdf",
        },
        "instructeurs": [],
        "demarche": {"id": "UHJvY2VkdXJlLTQ3NDgw", "number": 47480},
        "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItNjE0NjU=", "number": 61465, "label": "défaut"},
        "revision": {
            "id": "UHJvY2VkdXJlUmV2aXNpb24tNTc4MTU=",
            "champDescriptors": [
                {
                    "id": "Q2hhbXAtNjA5NDQ3",
                    "type": "explication",
                    "label": "Comment remplir ce formulaire de demande des 300€ du pass Culture",
                    "description": "Une aide pour remplir votre dossier est disponible ici : https://aide.passculture.app/fr/articles/5519444-jeunes-comment-remplir-le-formulaire-d-inscription-sur-demarches-simplifiees",
                    "required": False,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNTgyMjIw",
                    "type": "date",
                    "label": "Quelle est votre date de naissance",
                    "description": "Le pass Culture n'est éligible qu'aux personnes ayant 18 ans au moment du dépôt ou de la validation de leur dossier.",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNzE4MjIy",
                    "type": "explication",
                    "label": "Pièces justificatives acceptées",
                    "description": "Pour valider votre inscription, vous devez obligatoirement fournir l'un des documents suivants :\n- carte nationale d'identité française\n- passeport français ",
                    "required": False,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNDU5ODE5",
                    "type": "piece_justificative",
                    "label": "Pièce d'identité (page avec votre photo)",
                    "description": "L'ensemble de votre pièce doit être identifiable : attention à bien prendre la pièce intégralement en photo, en faisant apparaître vos nom, prénom et date de naissance. Ces éléments doivent être clairement identifiables. \nN'envoyez PAS le verso de votre carte d'identité ni la couverture de votre passeport.",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtMTg3Mzc5MA==",
                    "type": "piece_justificative",
                    "label": "Votre propre photo avec votre pièce d'identité",
                    "description": "Merci de vous prendre en photo avec votre pièce d'identité. \nNous devons pouvoir être en mesure de \n- lire clairement votre pièce, c'est-à-dire d'identifier vos nom, prénom et date de naissance\n- de voir distinctement votre visage.",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtMTg3Mzc0Mw==",
                    "type": "text",
                    "label": "Quel est le numéro de la pièce que tu viens de saisir ?",
                    "description": "Indiquez ici le numéro de la pièce que vous avez envoyé (généralement située en haut à droite du recto). \nLe format ressemble à cela : \n- Ancienne carte d'identité : 880692310285\n- Nouvelle carte d'identité : F9GFAL123\n- Passeport : 21GT764978",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNTgyMjE5",
                    "type": "phone",
                    "label": "Quel est ton numéro de téléphone ?",
                    "description": "",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNTgyMjIx",
                    "type": "integer_number",
                    "label": "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
                    "description": "Renseigner le code postal à 5 chiffres\nExemple: 92110",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNTgyMjIz",
                    "type": "address",
                    "label": "Quelle est ton adresse de résidence",
                    "description": None,
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNzE4MDk0",
                    "type": "drop_down_list",
                    "label": "Merci d'indiquer ton statut",
                    "description": "",
                    "required": True,
                    "options": [
                        "Lycéen",
                        "Étudiant",
                        "Employé",
                        "Apprenti, Alternant, Volontaire en service civique rémunéré",
                        "En recherche d'emploi ou chômeur",
                        "Inactif (ni en emploi ni au chômage), En incapacité de travailler",
                    ],
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNDY2Njk1",
                    "type": "header_section",
                    "label": "Consentement à l'utilisation de mes données",
                    "description": "",
                    "required": False,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNDY2Njk0",
                    "type": "engagement",
                    "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                    "description": "Elles sont consultables via le lien suivant : https://pass.culture.fr/cgu/",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNDU3MzAz",
                    "type": "engagement",
                    "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                    "description": "Ces données sont utilisées afin de nous assurer de votre éligibilité au pass Culture et d'assurer le bon fonctionnement du service pass Culture, conformément à notre Charte des données personnelles : https://pass.culture.fr/donnees-personnelles/\n\nPour en savoir plus sur l'exercice de vos droits, merci de nous écrire à support@passculture.app.",
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtMTE0NTg4Mg==",
                    "type": "engagement",
                    "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                    "description": None,
                    "required": True,
                    "options": None,
                    "champDescriptors": None,
                },
                {
                    "id": "Q2hhbXAtNDU0Nzc1",
                    "type": "header_section",
                    "label": "Un grand merci et à très vite sur le pass Culture !",
                    "description": "",
                    "required": False,
                    "options": None,
                    "champDescriptors": None,
                },
            ],
            "annotationDescriptors": [],
        },
        "champs": [
            {
                "id": "Q2hhbXAtNjA5NDQ3",
                "label": "Comment remplir ce formulaire de demande des 300€ du pass Culture",
                "stringValue": "",
            },
            {
                "id": "Q2hhbXAtNTgyMjIw",
                "label": "Quelle est votre date de naissance",
                "stringValue": "19 décembre 1984",
            },
            {"id": "Q2hhbXAtNzE4MjIy", "label": "Pièces justificatives acceptées", "stringValue": ""},
            {
                "id": "Q2hhbXAtNDU5ODE5",
                "label": "Pièce d'identité (page avec votre photo)",
                "stringValue": "",
                "file": {
                    "filename": "cat.jpg",
                    "contentType": "image/jpeg",
                    "checksum": "cEE15Txt8qglBb2Buv0XEA==",
                    "byteSize": 4576,
                    "url": "https://some.url.example.com",
                },
            },
            {
                "id": "Q2hhbXAtMTg3Mzc5MA==",
                "label": "Votre propre photo avec votre pièce d'identité",
                "stringValue": "",
                "file": {
                    "filename": "cat.jpg",
                    "contentType": "image/jpeg",
                    "checksum": "cEE15Txt8qglBb2Buv0XEA==",
                    "byteSize": 4576,
                    "url": "https://some.url.example.com",
                },
            },
            {
                "id": "Q2hhbXAtMTg3Mzc0Mw==",
                "label": "Quel est le numéro de la pièce que tu viens de saisir ?",
                "stringValue": "F9GFAL123",
            },
            {"id": "Q2hhbXAtNTgyMjE5", "label": "Quel est ton numéro de téléphone ?", "stringValue": "06 01 01 01 01"},
            {
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
                "stringValue": "92700",
            },
            {
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est ton adresse de résidence",
                "stringValue": "32 rue des sapins gris 21350 l'îsle à dent",
            },
            {"id": "Q2hhbXAtNzE4MDk0", "label": "Veuillez indiquer votre statut", "stringValue": "Employé"},
            {"id": "Q2hhbXAtNDY2Njk1", "label": "Consentement à l'utilisation de mes données", "stringValue": ""},
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
            },
        ],
        "annotations": [],
        "avis": [],
        "messages": [
            {
                "id": "Q29tbWVudGFpcmUtMTM2NjYzNDQ=",
                "email": "contact@demarches-simplifiees.fr",
                "body": '[Votre demande de crédit pour le pass Culture a bien été reçue]<br><br><div>&nbsp;Bonjour Jean,<br><br></div><div>L\'équipe du pass Culture vous confirme la bonne réception de votre dossier nº 5718303.&nbsp;<br><br></div><div><strong>Votre dossier sera examiné le plus rapidement possible, et vous recevrez un réponse au plus tard dans les semaines à venir. <br><br>Cela ne sert à rien de nous relancer : nos services sont extrêmement sollicités, et nous faisons vraiment de notre mieux pour vous répondre au plus vite !<br><br>Si vous avez&nbsp; prochainement 19 ans, ne vous inquiétez pas : si vous avez déposé votre dossier alors que vous aviez encore 18 ans, il sera bien validé !<br></strong><br>Un mail de confirmation vous sera envoyé lors de la mise en place des 300€ sur votre pass Culture.&nbsp;<br><br>À tout moment, vous pouvez consulter l\'avancée de votre dossier : <a target="_blank" rel="noopener" href="https://www.demarches-simplifiees.fr/dossiers/5718303">https://www.demarches-simplifiees.fr/dossiers/5718303</a></div><div><br>Vous avez des questions ?Nous vous invitons à consulter notre FAQ, vous y trouverez toutes les informations relatives au pass Culture : <a href="https://docs.passculture.app/experimentateurs/pre-inscription-au-pass-culture">https://aide.passculture.app</a></div><div><br>Bonne journée,</div><div><br>L\'équipe du pass Culture</div>',
                "createdAt": "2021-09-14T16:02:33+02:00",
                "attachment": None,
            }
        ],
        "usager": {"email": "jean.valgean@example.com"},
        "demandeur": {"civilite": "M", "nom": "VALGEAN", "prenom": "Jean", "dateDeNaissance": None},
    }
    return response


def make_new_stranger_application():
    data = {
        "id": "RG9zc2llci01NzQyOTk0",
        "number": 5742994,
        "archived": False,
        "state": "en_construction",
        "dateDerniereModification": "2021-09-15T15:19:21+02:00",
        "datePassageEnConstruction": "2021-09-15T15:19:20+02:00",
        "datePassageEnInstruction": None,
        "dateTraitement": None,
        "motivation": None,
        "motivationAttachment": None,
        "attestation": None,
        "pdf": {
            "url": "https://example.com/some/path/to/application.pdf",
        },
        "instructeurs": [],
        "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItNjEyNzE=", "number": 61271, "label": "défaut"},
        "champs": [
            {
                "id": "Q2hhbXAtNjA5NDQ3",
                "label": "Comment remplir ce formulaire de pré-inscription au pass Culture",
                "stringValue": "",
            },
            {
                "id": "Q2hhbXAtNTgyMjIw",
                "label": "Quelle est votre date de naissance",
                "stringValue": "18 décembre 2000",
            },
            {"id": "Q2hhbXAtNzE4MjIy", "label": "Pièces justificatives acceptées", "stringValue": ""},
            {"id": "Q2hhbXAtNDU5ODE5", "label": "Pièce d'identité (page avec votre photo)", "stringValue": ""},
            {
                "id": "Q2hhbXAtMjAyMTk4MQ==",
                "label": "Votre propre photo avec votre pièce d'identité",
                "stringValue": "",
            },
            {
                "id": "Q2hhbXAtMjAyMTk4Mw==",
                "label": "Quel est le numéro de la pièce que vous venez de saisir ?",
                "stringValue": "K682T8YLO",
            },
            {
                "id": "Q2hhbXAtNTgyMjE5",
                "label": "Quel est votre numéro de téléphone",
                "stringValue": "06 01 01 01 01",
            },
            {
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de votre commune de résidence ?",
                "stringValue": "92700",
            },
            {
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est votre adresse de résidence",
                "stringValue": "32 rue des sapins gris 21350 l'îsle à dent",
            },
            {"id": "Q2hhbXAtNzE4MDk0", "label": "Veuillez indiquer votre statut", "stringValue": "Employé"},
            {"id": "Q2hhbXAtNDUxMjg0", "label": "Déclaration de résidence", "stringValue": ""},
            {"id": "Q2hhbXAtMjAxMTQxNQ==", "label": "Justificatif de domicile", "stringValue": ""},
            {
                "id": "Q2hhbXAtNzE4MjU0",
                "label": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                "stringValue": "true",
            },
            {"id": "Q2hhbXAtNDY2Njk1", "label": "Consentement à l'utilisation de mes données", "stringValue": ""},
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
            },
        ],
        "annotations": [],
        "usager": {"email": "jean.valgean@example.com"},
        "demandeur": {"civilite": "M", "nom": "VALGEAN", "prenom": "Jean", "dateDeNaissance": None},
    }
    return data
