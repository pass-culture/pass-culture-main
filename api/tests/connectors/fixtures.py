import datetime
import random
import string
from typing import Iterable

import babel.dates
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core.users.constants import ELIGIBILITY_AGE_18
from pcapi.utils import date as date_utils


DEFAULT_MESSAGES = [
    {
        "email": "contact.demarche.numerique@example.com",
        "createdAt": "2021-09-14T16:02:33+02:00",
    }
]


AGE18_ELIGIBLE_BIRTH_DATE = date_utils.get_naive_utc_now() - relativedelta(years=ELIGIBILITY_AGE_18)


def make_graphql_application(
    application_number: int,
    state: str,
    *,
    activity: str = "Étudiant",
    birth_date: datetime.datetime | None = AGE18_ELIGIBLE_BIRTH_DATE,
    birth_place: str = "Paris",
    civility: str = "Mme",
    city: str | None = None,
    construction_datetime: str = "2020-05-13T09:09:46+02:00",
    last_modification_date: str = "2020-05-13T10:41:23+02:00",
    last_user_fields_modification_date: str = "2020-05-13T00:09:46+02:00",
    email: str | None = "young.individual@example.com",
    applicant_email: str | None = None,
    first_name: str = "John",
    full_graphql_response: bool = False,
    has_next_page: bool = False,
    id_piece_number: str | None = "123123123",
    last_name: str = "Doe",
    postal_code: int = 67200,
    processed_datetime: str | None = "2020-05-13T10:41:21+02:00",
    messages: list | None = None,
    application_techid: str | None = None,
    procedure_number: int | None = 8888,
    labels: dict | None = None,
    annotations: list[dict] | None = None,
    application_labels: list | None = None,
) -> dict:
    if messages is None:
        messages = DEFAULT_MESSAGES
    if labels is None:
        labels = {}

    data = {
        "id": application_techid or "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20)),
        "number": application_number,
        "archived": False,
        "state": state,
        "dateDepot": "2020-05-13T00:09:46+02:00",
        "dateDerniereModification": last_modification_date,
        "dateDerniereModificationChamps": last_user_fields_modification_date,
        "datePassageEnConstruction": construction_datetime,
        "datePassageEnInstruction": "2020-05-13T10:37:31+02:00",
        "dateTraitement": processed_datetime,
        "demarche": {
            "id": "PROCEDURE_ID_AT_DMS",
            "number": procedure_number,
        },
        "instructeurs": [{"email": "instructor@example.com", "id": "SomeRandomId"}],
        "messages": messages,
        "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItMjYxMzg=", "number": 2613, "label": "défaut"},
        "champs": [
            {
                "id": "Q2hhbXAtNjA5NDQ3",
                "label": "Comment remplir ce formulaire de demande du crédit du pass Culture",
                "stringValue": "",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNTgyMjIw",
                "label": labels.get("birth_date") or "Quelle est ta date de naissance ?",
                "stringValue": babel.dates.format_date(birth_date, format="long", locale="fr"),
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNTQ1NzkzMQ==",
                "label": labels.get("birth_place") or "Quelle est ta ville de naissance ?",
                "stringValue": birth_place,
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtMTg3Mzc0Mw==",
                "label": labels.get("id_piece_number") or "Quel est le numéro de la pièce que tu viens de saisir ?",
                "stringValue": id_piece_number,
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNzE4MjIy",
                "label": "Pièces justificatives acceptées",
                "stringValue": "",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDU5ODE5",
                "label": "Pièce d'identité (page avec ta photo)",
                "stringValue": None,
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtMTg3Mzc5MA==",
                "label": "Ton selfie avec ta pièce d'identité",
                "stringValue": None,
                "updatedAt": last_user_fields_modification_date,
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjE5",
                "label": labels.get("phone_number") or "Quel est ton numéro de téléphone ?",
                "stringValue": "01 23 45 67 89",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjIx",
                "label": labels.get("postal_code")
                or "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
                "stringValue": postal_code,
                "updatedAt": last_user_fields_modification_date,
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjIz",
                "label": labels.get("address") or "Quelle est ton adresse de résidence",
                "stringValue": "3 La Bigotais 22800 Saint-Donan",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNzE4MDk0",
                "label": labels.get("status") or "Merci d'indiquer ton statut",
                "stringValue": activity,
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDUxMjg0",
                "label": "Déclaration de résidence",
                "stringValue": "",
            },
            {"id": "Q2hhbXAtNTgyMzI4", "label": "Certification sur l'honneur", "stringValue": ""},
            {
                "id": "Q2hhbXAtNzE4MjU0",
                "label": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDY2Njk1",
                "label": "Consentement à l'utilisation de mes données",
                "stringValue": "",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNzE4MjU0",
                "label": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDY2Njk1",
                "label": "Consentement à l'utilisation de mes données",
                "stringValue": "",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
                "updatedAt": last_user_fields_modification_date,
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
                "updatedAt": last_user_fields_modification_date,
            },
        ],
        "annotations": annotations if annotations else [],
        "usager": {"id": "WSJvY2VkdXJlLTQ0Nhju", "email": email},
        "demandeur": {
            "id": "ABCvY2VkdXJlLTQ0Nxyz",
            "civilite": civility,
            "nom": last_name,
            "prenom": first_name,
            "dateDeNaissance": None,
            "email": applicant_email,
        },
        "labels": [{"id": "TGFiZWwtR6E7NtAx", "name": "Test"}] if application_labels is None else application_labels,
    }
    if city is not None:
        data["champs"].append(
            {
                "id": "Q2hhbXAtNTgyMjIy",
                "label": labels.get("city") or "Quelle est ta ville de résidence ?",
                "stringValue": city,
            }
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
        "dateDerniereModificationChamps": "2020-05-13T00:09:46+02:00",
        "datePassageEnConstruction": "2021-09-14T16:02:32+02:00",
        "datePassageEnInstruction": None,
        "dateTraitement": None,
        "demarche": {"id": "UHJvY2VkdXJlLTQ3NDgw", "number": settings.DMS_ENROLLMENT_PROCEDURE_ID_FR},
        "instructeurs": [],
        "messages": [{"email": "contact.demarche.numerique@example.com", "createdAt": "2021-09-14T16:02:33+02:00"}],
        "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItNjE0NjU=", "number": 61465, "label": "défaut"},
        "champs": [
            {
                "id": "Q2hhbXAtNjA5NDQ3",
                "label": "Comment remplir ce formulaire de demande du crédit du pass Culture",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNTgyMjIw",
                "label": "Quelle est ta date de naissance ?",
                "stringValue": "19 décembre 2004",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNTUwMTIwNw==",
                "label": "Quelle est ta ville de naissance ?",
                "stringValue": "Paris",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMTg3Mzc0Mw==",
                "label": "Quel est le numéro de la pièce que tu viens de saisir ?",
                "stringValue": "F9GFAL123",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNzE4MjIy",
                "label": "Pièces justificatives acceptées",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDU5ODE5",
                "label": "Pièce d'identité (page avec ta photo)",
                "stringValue": None,
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMTg3Mzc5MA==",
                "label": "Ton selfie avec ta pièce d'identité",
                "stringValue": None,
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjE5",
                "label": "Quel est ton numéro de téléphone ?",
                "stringValue": "06 01 01 01 01",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
                "stringValue": "92700",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est ton adresse de résidence",
                "stringValue": "32 rue des sapins gris 21350 l'îsle à dent",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNzE4MDk0",
                "label": "Merci d'indiquer ton statut",
                "stringValue": "Employé",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDY2Njk1",
                "label": "Consentement à l'utilisation de mes données",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel. *",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
        ],
        "annotations": [
            {
                "id": "Q2hhbXAtNTA4ODM1NQ==",
                "label": "ID Ubble",
                "stringValue": "",
                "updatedAt": "2026-03-30T14:15:45+02:00",
            },
            {
                "id": "Q2hhbXAtNTAzMDM4MQ==",
                "label": "AN_002: Code de l'annotation instructeur",
                "stringValue": "",
                "updatedAt": "2026-03-30T14:15:45+02:00",
                "values": [],
            },
            {
                "id": "Q2hhbXAtMjI3NzY5OA==",
                "label": "Annotation libre",
                "stringValue": "",
                "updatedAt": "2026-03-30T14:15:45+02:00",
            },
            {
                "id": "Q2hhbXAtMjc1MzAxMg==",
                "label": "AN_001: Statut du dossier côté passCulture",
                "stringValue": "Aucune erreur détectée. Le dossier peut être passé en instruction.",
                "updatedAt": "2026-03-30T12:40:37+02:00",
            },
        ],
        "usager": {"id": "WSJvY2VkdXJlLTQ0Nhju", "email": "jean.valgean@example.com"},
        "demandeur": {
            "id": "ABCvY2VkdXJlLTQ0Nxyz",
            "civilite": "M",
            "nom": "VALGEAN",
            "prenom": "Jean",
            "dateDeNaissance": None,
            "email": None,
        },
        "labels": [],
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
        "dateDerniereModificationChamps": "2020-05-13T00:09:46+02:00",
        "datePassageEnConstruction": "2021-09-15T15:19:20+02:00",
        "datePassageEnInstruction": None,
        "dateTraitement": None,
        "demarche": {
            "id": "RG9zc2llci01NzQyOTk0",
            "number": settings.DMS_ENROLLMENT_PROCEDURE_ID_ET,
        },
        "instructeurs": [],
        "messages": [{"createdAt": "2021-09-14T16:02:33+02:00", "email": "contact.demarche.numerique@example.com"}],
        "groupeInstructeur": {"id": "R3JvdXBlSW5zdHJ1Y3RldXItNjEyNzE=", "number": 61271, "label": "défaut"},
        "champs": [
            {
                "id": "Q2hhbXAtNjA5NDQ3",
                "label": "Comment remplir ce formulaire de pré-inscription au pass Culture ?",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNTgyMjIw",
                "label": "Quelle est ta date de naissance ?",
                "stringValue": "12 mai 2006",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNTUwMTQ2NA==",
                "label": "Quelle est ta ville de naissance ?",
                "stringValue": "Berlin",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMjI3MTA3MQ==",
                "label": "Document d'identité",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMjAyMTk4Mw==",
                "label": "Quel est le numéro de la pièce que tu viens de saisir",
                "stringValue": "K682T8YLO",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDU5ODE5",
                "label": "Pièce d'identité (page avec photo)",
                "stringValue": None,
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMjAyMTk4MQ==",
                "label": "Ton selfie avec ta pièce d'identité originale en main",
                "stringValue": None,
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDUxMjg0",
                "label": "Déclaration de résidence",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMjAxMTQxNQ==",
                "label": "Justificatif de domicile - Documents",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
                "champs": [
                    {
                        "id": "Q2hhbXAtMjI3MzY2M3wwMUtNWkI1R1dOUVdCNzhUMlNLNzdERTIzSg==",
                        "label": "Justificatif de domicile de plus d'un an",
                        "stringValue": None,
                        "updatedAt": "2020-05-13T00:09:46+02:00",
                    },
                    {
                        "id": "Q2hhbXAtMjI3MzY2MXwwMUtNWkI1R1dOUVdCNzhUMlNLNzdERTIzSg==",
                        "label": "Attestation d'hébergement datée et signée manuellement",
                        "stringValue": None,
                        "updatedAt": "2020-05-13T00:09:46+02:00",
                    },
                    {
                        "id": "Q2hhbXAtMjI3MzY2MnwwMUtNWkI1R1dOUVdCNzhUMlNLNzdERTIzSg==",
                        "label": "Document d'identité de l'hébergeur ou responsable légal",
                        "stringValue": None,
                        "updatedAt": "2020-05-13T00:09:46+02:00",
                    },
                ],
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjE5",
                "label": "Quel est ton numéro de téléphone ?",
                "stringValue": "06 01 01 01 01",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjIx",
                "label": "Quel est le code postal de ta commune de résidence ?",
                "stringValue": "92700",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNTgyMjIz",
                "label": "Quelle est ton adresse de résidence ?",
                "stringValue": "32 rue des sapins gris 21350 l'îsle à dent",
            },
            {
                # Deprecated - Kept here to ensure compatibility with old applications
                "id": "Q2hhbXAtNzE4MDk0",
                "label": "Merci d'indiquer ton statut",
                "stringValue": "Employé",
            },
            {
                "id": "Q2hhbXAtNzE4MjU0",
                "label": "Je certifie sur l’honneur résider légalement et habituellement sur le territoire français depuis plus de un an.",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDY2Njk1",
                "label": "Consentement à l'utilisation de mes données",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDY2Njk0",
                "label": "J'accepte les conditions générales d'utilisation du pass Culture",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDU3MzAz",
                "label": "Je donne mon accord au traitement de mes données à caractère personnel.",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtMTE0NTg4Mg==",
                "label": "Je déclare sur l’honneur que l'ensemble des réponses et documents fournis sont corrects et authentiques.",
                "stringValue": "true",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
            {
                "id": "Q2hhbXAtNDU0Nzc1",
                "label": "Un grand merci et à très vite sur le pass Culture !",
                "stringValue": "",
                "updatedAt": "2020-05-13T00:09:46+02:00",
            },
        ],
        "annotations": [
            {
                "id": "Q2hhbXAtNTAzMzM5Mg==",
                "label": "ID Ubble",
                "stringValue": "",
                "updatedAt": "2026-03-30T14:23:16+02:00",
            },
            {
                "id": "Q2hhbXAtNTAzMjA0NA==",
                "label": "AN_002: Code de l'annotation instructeur",
                "stringValue": "",
                "updatedAt": "2026-03-30T14:23:16+02:00",
                "values": [],
            },
            {
                "id": "Q2hhbXAtMjQ0ODY0Mw==",
                "label": "Annotation libre",
                "stringValue": "",
                "updatedAt": "2026-03-30T14:23:16+02:00",
            },
            {
                "id": "Q2hhbXAtMjgwMzExOQ==",
                "label": "AN_001: Statut du dossier côté passCulture",
                "stringValue": "Aucune erreur détectée. Le dossier peut être passé en instruction.",
                "updatedAt": "2026-03-30T14:24:05+02:00",
            },
        ],
        "usager": {"id": "WSJvY2VkdXJlLTQ0Nhju", "email": "jean.valgean@example.com"},
        "demandeur": {
            "id": "ABCvY2VkdXJlLTQ0Nxyz",
            "civilite": "M",
            "nom": "VALGEAN",
            "prenom": "Jean",
            "dateDeNaissance": None,
            "email": None,
        },
        "labels": [],
    }
    return data


def make_graphql_deleted_applications(procedure_number: int, application_numbers: Iterable[int]):
    return {
        "demarche": {
            "id": "PROCEDURE_ID_AT_DMS",
            "number": procedure_number,
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


MOVIE_LIST = {
    "movieList": {
        "totalCount": 4,
        "pageInfo": {"hasNextPage": True, "endCursor": "YXJyYXljb25uZWN0aW9uOjQ5"},
        "edges": [
            {
                "node": {
                    "id": "TW92aWU6MTMxMTM2",
                    "internalId": 131136,
                    "backlink": {
                        "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=131136.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                    },
                    "data": {"eidr": None, "productionYear": 1915},
                    "title": "Ceux de chez nous",
                    "originalTitle": "Ceux de chez nous",
                    "type": "FEATURE_FILM",
                    "runtime": "PT0H21M0S",
                    "poster": {"url": "https://fr.web.img2.acsta.net/medias/nmedia/18/78/15/02/19447537.jpg"},
                    "synopsis": "Alors que la Premi\u00e8re Guerre Mondiale a \u00e9clat\u00e9, et en r\u00e9ponse aux propos des intellectuels allemands de l'\u00e9poque, Sacha Guitry filme les grands artistes de l'\u00e9poque qui contribuent au rayonnement culturel de la France.",
                    "releases": [
                        {
                            "name": "ReRelease",
                            "releaseDate": {"date": "2023-11-01"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411399]"},
                                "visa_number": "108245",
                            },
                            "certificate": None,
                        },
                        {
                            "name": "Released",
                            "releaseDate": {"date": "1915-11-22"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [411400]"},
                                "visa_number": "108245",
                            },
                            "certificate": None,
                        },
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {"firstName": "Sacha", "lastName": "Guitry"},
                                    "position": {"name": "DIRECTOR"},
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm-131136/casting/",
                            "label": "Casting complet du film sur AlloCin\u00e9",
                        },
                        "edges": [
                            {
                                "node": {
                                    "actor": {"firstName": "Sacha", "lastName": "Guitry"},
                                    "role": "(doublage)",
                                }
                            },
                            {"node": {"actor": {"firstName": "Sarah", "lastName": "Bernhardt"}, "role": None}},
                            {"node": {"actor": {"firstName": "Anatole", "lastName": "France"}, "role": None}},
                        ],
                    },
                    "countries": [{"name": "France", "alpha3": "FRA"}],
                    "genres": ["DOCUMENTARY"],
                    "companies": [
                        {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                        {"activity": "Distribution", "company": {"name": "Les Acacias"}},
                    ],
                }
            },
            {
                "node": {
                    "id": "TW92aWU6NDEzMjQ=",
                    "internalId": 41324,
                    "backlink": {
                        "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=41324.html",
                        "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                    },
                    "data": {"eidr": "10.5240/205D-17AD-BBB2-F62A-2481-7", "productionYear": 1931},
                    "title": "The Front page",
                    "originalTitle": "The Front page",
                    "type": "FEATURE_FILM",
                    "runtime": "PT1H41M0S",
                    "poster": {"url": "https://fr.web.img4.acsta.net/pictures/17/12/21/10/23/2878333.jpg"},
                    "synopsis": "Un journaliste s'appr\u00eate \u00e0 se marier, lorsqu'il est envoy\u00e9 de toute urgence sur un scoop: l'ex\u00e9cution d'un homme accus\u00e9 d'avoir tu\u00e9 un policier. Mais ce dernier s'\u00e9vade.",
                    "releases": [
                        {
                            "name": "ReRelease",
                            "releaseDate": {"date": "2024-10-16"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [408737]"}
                            },
                            "certificate": None,
                        },
                        {
                            "name": "Released",
                            "releaseDate": {"date": "1931-09-25"},
                            "data": {
                                "tech": {"auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [278514]"}
                            },
                            "certificate": None,
                        },
                    ],
                    "credits": {
                        "edges": [
                            {
                                "node": {
                                    "person": {"firstName": "Lewis", "lastName": "Milestone"},
                                    "position": {"name": "DIRECTOR"},
                                }
                            }
                        ]
                    },
                    "cast": {
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm-41324/casting/",
                            "label": "Casting complet du film sur AlloCin\u00e9",
                        },
                        "edges": [
                            {
                                "node": {
                                    "actor": {"firstName": "Adolphe", "lastName": "Menjou"},
                                    "role": "Walter Burns",
                                }
                            },
                            {
                                "node": {
                                    "actor": {"firstName": "Pat", "lastName": "O'Brien"},
                                    "role": "Hildy Johnson",
                                }
                            },
                            {
                                "node": {
                                    "actor": {"firstName": "Mary", "lastName": "Brian"},
                                    "role": "Peggy Grant",
                                }
                            },
                        ],
                    },
                    "countries": [{"name": "USA", "alpha3": "USA"}],
                    "genres": ["COMEDY"],
                    "companies": [
                        {"activity": "InternationalDistributionExports", "company": {"name": "United Artists"}},
                        {"activity": "Distribution", "company": {"name": "Swashbuckler Films"}},
                        {"activity": "Distribution", "company": {"name": "Swashbuckler Films"}},
                        {"activity": "Production", "company": {"name": "The Caddo company"}},
                    ],
                }
            },
        ],
    }
}

MOVIE_SHOWTIME_LIST = {
    "movieShowtimeList": {
        "totalCount": 29,
        "edges": [
            {
                "node": {
                    "movie": {
                        "id": "TW92aWU6Mjg4NDAx",
                        "internalId": 288401,
                        "backlink": {
                            "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=288401.html",
                            "label": "Tous les d\u00e9tails du film sur AlloCin\u00e9",
                        },
                        "data": {"eidr": None, "productionYear": 2023},
                        "title": "Les Trois Mousquetaires: Milady",
                        "originalTitle": "Les Trois Mousquetaires: Milady",
                        "type": "FEATURE_FILM",
                        "runtime": "PT1H55M0S",
                        "poster": {"url": "https://fr.web.img4.acsta.net/pictures/23/10/06/12/03/1531578.jpg"},
                        "synopsis": "Du Louvre au Palais de Buckingham, des bas-fonds de Paris au si\u00e8ge de La Rochelle\u2026 dans un Royaume divis\u00e9 par les guerres de religion et menac\u00e9 d\u2019invasion par l\u2019Angleterre, une poign\u00e9e d\u2019hommes et de femmes vont croiser leurs \u00e9p\u00e9es et lier leur destin \u00e0 celui de la France.",
                        "releases": [
                            {
                                "name": "Released",
                                "releaseDate": {"date": "2023-12-13"},
                                "data": {
                                    "tech": {
                                        "auto_update_info": "Imported from AC_INT.dbo.EntityRelease from id [361246]"
                                    },
                                    "visa_number": "155097",
                                },
                                "certificate": None,
                            }
                        ],
                        "credits": {
                            "edges": [
                                {
                                    "node": {
                                        "person": {"firstName": "Martin", "lastName": "Bourboulon"},
                                        "position": {"name": "DIRECTOR"},
                                    }
                                }
                            ]
                        },
                        "cast": {
                            "backlink": {
                                "url": "https://www.allocine.fr/film/fichefilm-288401/casting/",
                                "label": "Casting complet du film sur AlloCin\u00e9",
                            },
                            "edges": [
                                {
                                    "node": {
                                        "actor": {"firstName": "Fran\u00e7ois", "lastName": "Civil"},
                                        "role": "D'Artagnan",
                                    }
                                },
                                {
                                    "node": {
                                        "actor": {"firstName": "Vincent", "lastName": "Cassel"},
                                        "role": "Athos",
                                    }
                                },
                                {
                                    "node": {
                                        "actor": {"firstName": "Romain", "lastName": "Duris"},
                                        "role": "Aramis",
                                    }
                                },
                            ],
                        },
                        "countries": [{"name": "France", "alpha3": "FRA"}],
                        "genres": ["ADVENTURE", "HISTORICAL"],
                        "companies": [
                            {"activity": "Distribution", "company": {"name": "Path\u00e9"}},
                            {"activity": "InternationalDistributionExports", "company": {"name": "Path\u00e9"}},
                            {"activity": "Production", "company": {"name": "Path\u00e9"}},
                            {"activity": "CoProduction", "company": {"name": "M6 Films"}},
                            {"activity": "CoProduction", "company": {"name": "Radar Films"}},
                            {"activity": "CoProduction", "company": {"name": "DeaPlaneta"}},
                            {"activity": "CoProduction", "company": {"name": "Constantin Film Verleih"}},
                        ],
                    },
                    "showtimes": [
                        {
                            "startsAt": "2023-12-18T14:00:00",
                            "diffusionVersion": "LOCAL",
                            "projection": ["DIGITAL"],
                            "experience": None,
                            "languages": ["FRENCH"],
                        }
                    ],
                }
            }
        ],
    }
}
