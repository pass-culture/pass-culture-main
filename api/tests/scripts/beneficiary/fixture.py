import datetime
import random
import string
from typing import Iterable
from typing import Optional

import babel.dates

from pcapi.connectors.dms import models as dms_models


DEFAULT_MESSAGES = [
    {
        "email": "contact@demarches-simplifiees.fr",
        "createdAt": "2021-09-14T16:02:33+02:00",
    }
]


def make_graphql_application(
    application_number: int,
    state: str,
    activity: str = "Étudiant",
    birth_date: Optional[datetime.datetime] = datetime.datetime(2004, 1, 1),
    civility: str = "Mme",
    city: Optional[str] = None,
    construction_datetime: str = "2020-05-13T09:09:46+02:00",
    last_modification_date: str = "2020-05-13T10:41:23+02:00",
    email: Optional[str] = "young.individual@example.com",
    first_name: str = "John",
    full_graphql_response: bool = False,
    has_next_page: bool = False,
    id_piece_number: Optional[str] = "123123123",
    last_name: str = "Doe",
    postal_code: int = 67200,
    processed_datetime: Optional[str] = "2020-05-13T10:41:21+02:00",
    messages: Optional[list] = None,
    application_techid: Optional[str] = None,
) -> dict:
    if messages is None:
        messages = DEFAULT_MESSAGES

    data = {
        "id": application_techid or "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)),
        "number": application_number,
        "archived": False,
        "state": state,
        "dateDepot": "2020-05-13T00:09:46+02:00",
        "dateDerniereModification": last_modification_date,
        "datePassageEnConstruction": construction_datetime,
        "datePassageEnInstruction": "2020-05-13T10:37:31+02:00",
        "dateTraitement": processed_datetime,
        "messages": messages,
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
                "id": "Q2hhbXAtNTgyMjIw",
                "label": "Quelle est votre date de naissance",
                "stringValue": babel.dates.format_date(birth_date, format="long", locale="fr"),
            },
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
                "label": "Quel est le numéro de la pièce que tu viens de saisir ?",
                "stringValue": id_piece_number,
            },
            {"id": "Q2hhbXAtNTgyMjE5", "label": "Quel est ton numéro de téléphone ?", "stringValue": "01 23 45 67 89"},
            {
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
                "stringValue": postal_code,
            },
            {
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est ton adresse de résidence",
                "stringValue": "3 La Bigotais 22800 Saint-Donan",
            },
            {"id": "Q2hhbXAtNzE4MDk0", "label": "Merci d'indiquer ton statut", "stringValue": activity},
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
        "usager": {"id": "WSJvY2VkdXJlLTQ0Nhju", "email": email},
        "demandeur": {
            "id": "ABCvY2VkdXJlLTQ0Nxyz",
            "civilite": civility,
            "nom": last_name,
            "prenom": first_name,
            "dateDeNaissance": None,
        },
    }
    if city is not None:
        data["champs"].append(
            {"id": "Q2hhbXAtNTgyMjIy", "label": "Quelle est ta ville de résidence ?", "stringValue": city}
        )
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
        "dateDepot": "2020-05-13T00:09:46+02:00",
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
                "stringValue": "19 décembre 2004",
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
            {"id": "Q2hhbXAtNzE4MDk0", "label": "Merci d'indiquer ton statut", "stringValue": "Employé"},
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
        "usager": {"id": "WSJvY2VkdXJlLTQ0Nhju", "email": "jean.valgean@example.com"},
        "demandeur": {
            "id": "ABCvY2VkdXJlLTQ0Nxyz",
            "civilite": "M",
            "nom": "VALGEAN",
            "prenom": "Jean",
            "dateDeNaissance": None,
        },
    }
    return response


def make_new_stranger_application():
    data = {
        "id": "RG9zc2llci01NzQyOTk0",
        "number": 5742994,
        "archived": False,
        "state": "en_construction",
        "dateDepot": "2020-05-13T00:09:46+02:00",
        "dateDerniereModification": "2021-09-15T15:19:21+02:00",
        "datePassageEnConstruction": "2021-09-15T15:19:20+02:00",
        "datePassageEnInstruction": None,
        "dateTraitement": None,
        "messages": [],
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
                "stringValue": "12 mai 2006",
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
                "label": "Quel est le numéro de la pièce que tu viens de saisir ?",
                "stringValue": "K682T8YLO",
            },
            {
                "id": "Q2hhbXAtNTgyMjE5",
                "label": "Quel est ton numéro de téléphone ?",
                "stringValue": "06 01 01 01 01",
            },
            {
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de ta commune de résidence ?",
                "stringValue": "92700",
            },
            {
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est ton adresse de résidence ?",
                "stringValue": "32 rue des sapins gris 21350 l'îsle à dent",
            },
            {"id": "Q2hhbXAtNzE4MDk0", "label": "Merci d'indiquer ton statut", "stringValue": "Employé"},
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
        "usager": {"id": "WSJvY2VkdXJlLTQ0Nhju", "email": "jean.valgean@example.com"},
        "demandeur": {
            "id": "ABCvY2VkdXJlLTQ0Nxyz",
            "civilite": "M",
            "nom": "VALGEAN",
            "prenom": "Jean",
            "dateDeNaissance": None,
        },
    }
    return data


def make_graphql_deleted_applications(procedure_id: int, application_numbers: Iterable[int]):
    return {
        "demarche": {
            "id": "PROCEDURE_ID_AT_DMS",
            "number": procedure_id,
            "deletedDossiers": {
                "pageInfo": {"endCursor": "MTAw", "hasNextPage": False},
                "nodes": [
                    {
                        "dateSupression": "2021-10-02T00:00:00+02:00",
                        "id": "".join(random.choice(string.ascii_letters) for _ in range(28)),
                        "number": application_number,
                        "reason": "user_request",
                        "state": "en_construction",
                    }
                    for application_number in application_numbers
                ],
            },
        }
    }


def make_single_application(*args, **kwargs):
    return {"dossier": make_graphql_application(*args, **kwargs)}


def make_parsed_graphql_application(*args, **kwargs):
    return dms_models.DmsApplicationResponse(**make_graphql_application(*args, **kwargs))
