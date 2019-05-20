import copy
from typing import List, Tuple

LIST_APPLICATIONS_STANDARD_RESPONSE = {
    "dossiers": [],
    "pagination":
        {
            "page": 1,
            "resultats_par_page": 100,
            "nombre_de_page": 1
        }
}

APPLICATION_DETAIL_STANDARD_RESPONSE = {
    "dossier": {
        "id": 123,
        "created_at": "2019-05-04T17:57:28.726Z",
        "updated_at": "2019-05-07T15:15:39.849Z",
        "archived": False,
        "email": "jane.doe@test.com",
        "state": "closed",
        "simplified_state": "Accepté",
        "initiated_at": "2019-05-04T18:01:23.694Z",
        "received_at": "2019-05-07T15:15:22.340Z",
        "processed_at": "2019-05-07T15:15:39.393Z",
        "motivation": "",
        "instructeurs": ["admin.pc@example.com"],
        "individual": {"civilite": "Mme", "nom": "Doe", "prenom": "Jane"},
        "entreprise": None,
        "etablissement": None, "cerfa": [], "commentaires": [
            {
                "email": "contact@demarches-simplifiees.fr",
                "body": "[Votre préinscription pour le pass Culture a bien été reçue]\u003cbr\u003e\u003cbr\u003e\u003cp\u003e\r\nBonjour Jane,\u003c/p\u003e\r\n\u003cp\u003e\r\nL'équipe du pass Culture vous confirme la bonne réception de votre dossier nº 470917. \u003c/p\u003e\u003cp\u003eVotre dossier sera examiné dans les plus bref délais. Si votre dossier est validé, vous bénéficierez dès l'ouverture de l'expérimentation sur votre département d'un crédit de 500€ pour réserver l'ensemble des propositions culturelles figurant sur l'application pass Culture. Un mail de confirmation vous sera envoyé à l'ouverture de votre crédit.\u003c/p\u003e\r\n\u003cp\u003e\r\nÀ tout moment, vous pouvez consulter l'avancée de votre dossier et échanger directement avec nous à cette adresse : \u003ca target=\"_blank\" rel=\"noopener\" href=\"https://www.demarches-simplifiees.fr/dossiers/470917\"\u003ehttps://www.demarches-simplifiees.fr/dossiers/470917\u003c/a\u003e\r\n\u003c/p\u003e\r\n\u003cp\u003e\r\nBonne journée,\r\n\u003c/p\u003e\r\n\u003cp\u003e\r\nL'équipe du pass Culture\u003c/p\u003e\u003cp\u003e\u003cimg alt=\"\" src=\"https://s1g.s3.amazonaws.com/42376e1f41d9842343a53bcdd87e5fc4.jpeg\"\u003e\u003cbr\u003e\u003c/p\u003e",
                "created_at": "2019-05-04T18:01:24.428Z",
                "attachment": None
            },
            {
                "email": "contact@demarches-simplifiees.fr",
                "body": "[L'équipe du pass Culture s'occupe de votre dossier]\u003cbr\u003e\u003cbr\u003e\u003cp\u003eBonjour Jane,\u003c/p\u003e\u003cp\u003eBonne nouvelle ! Votre dossier nº 470917 est en cours d'examen par l'équipe du pass Culture.\u003c/p\u003e\u003cp\u003eÀ tout moment, vous pouvez consulter l'avancée de votre dossier et échanger directement avec nous à cette adresse : \u003ca target=\"_blank\" rel=\"noopener\" href=\"https://www.demarches-simplifiees.fr/dossiers/470917\"\u003ehttps://www.demarches-simplifiees.fr/dossiers/470917\u003c/a\u003e\u003cbr\u003e\u003c/p\u003e\u003cp\u003eBonne journée,\u003c/p\u003e\u003cp\u003eL'équipe du pass Culture\u003c/p\u003e\u003cp\u003e\u003cimg alt=\"\" src=\"https://s1g.s3.amazonaws.com/42376e1f41d9842343a53bcdd87e5fc4.jpeg\"\u003e\u003cbr\u003e\u003c/p\u003e",
                "created_at": "2019-05-07T15:15:22.504Z",
                "attachment": None
            },
            {
                "email": "contact@demarches-simplifiees.fr",
                "body": "[Votre demande d'activation du pass Culture a été acceptée]\u003cbr\u003e\u003cbr\u003e\u003cp\u003eBonjour Jane,\u003cbr\u003e\u003c/p\u003e\u003cp\u003eL'équipe du pass Culture vous informe que votre dossier nº 470917 a été accepté le 07/05/2019.\u003c/p\u003e\u003cp\u003eDès l'ouverture de l'expérimentation sur votre département, vous recevrez votre mail de bienvenue pour accéder à l’application.\u003c/p\u003e\u003cp\u003eBonne journée,\u003cbr\u003e\u003c/p\u003e\u003cp\u003eL'équipe du pass Culture\u003c/p\u003e\u003cp\u003e\u003cimg alt=\"\" src=\"https://s1g.s3.amazonaws.com/42376e1f41d9842343a53bcdd87e5fc4.jpeg\"\u003e\u003cbr\u003e\u003c/p\u003e",
                "created_at": "2019-05-07T15:15:39.845Z",
                "attachment": None
            }
        ],
        "champs_private": [],
        "pieces_justificatives": [],
        "types_de_piece_justificative": [],
        "justificatif_motivation": None,
        "champs": [
            {
                "value": "67 - Bas-Rhin",
                "type_de_champ": {
                    "id": 596453, "libelle": "Veuillez indiquer votre département",
                    "type_champ": "departements", "order_place": 0, "description": None
                }
            },
            {
                "value": "0612345678",
                "type_de_champ": {
                    "id": 582219, "libelle": "Numéro de téléphone", "type_champ": "phone",
                    "order_place": 2, "description": None
                }
            },
            {
                "value": "2000-05-01",
                "type_de_champ": {
                    "id": 582220,
                    "libelle": "Date de naissance",
                    "type_champ": "date",
                    "order_place": 3,
                    "description": None
                }
            },
            {
                "value": "41 avenue de la Résistance 67200 Strasbourg",
                "type_de_champ": {
                    "id": 582223, "libelle": "Adresse de résidence", "type_champ": "address",
                    "order_place": 4, "description": None
                }
            },
            {
                "value": "67200",
                "type_de_champ": {
                    "id": 582221,
                    "libelle": "Code postal",
                    "type_champ": "text",
                    "order_place": 5,
                    "description": None
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 582328, "libelle": "Pièces justificatives",
                    "type_champ": "explication", "order_place": 6,
                    "description": "Afin de valider votre inscription, vous devez fournir obligatoirement un justificatif de date de naissance (pièce d'identité), ainsi qu'un justificatif d'une adresse de résidence sur le département concerné (justificatif de domicile)"
                }
            },
            {
                "value": "https://url.to.scan/passeport",
                "type_de_champ": {
                    "id": 459819,
                    "libelle": "Pièce d'identité (photocopie recto de votre carte d'identité ou passeport)",
                    "type_champ": "piece_justificative", "order_place": 7,
                    "description": "Cette pièce justificative est obligatoire pour valider votre inscription"
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451284,
                    "libelle": "Vous avez un justificatif de domicile à votre nom ?",
                    "type_champ": "header_section", "order_place": 8,
                    "description": ""
                }
            }, {
                "value": None,
                "type_de_champ": {
                    "id": 422858,
                    "libelle": "Justificatif de domicile à votre nom (facture de moins de 6 mois d'eau, d'électricité, de gaz ou de téléphone) ",
                    "type_champ": "piece_justificative",
                    "order_place": 9,
                    "description": ""
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 460834,
                    "libelle": "Vous habitez chez un proche (parent, ami, etc.) ?",
                    "type_champ": "header_section", "order_place": 10,
                    "description": ""
                }
            }, {
                "value": "https://url.to.scan/hebergement",
                "type_de_champ": {
                    "id": 451287,
                    "libelle": "Attestation sur l'honneur d'hébergement, datée et signée par la personne qui vous héberge et par vous-même",
                    "type_champ": "piece_justificative", "order_place": 11,
                    "description": ""
                }
            }, {
                "value": "https://url.to.scan/domicile",
                "type_de_champ": {
                    "id": 460835,
                    "libelle": "Justificatif de domicile de la personne qui vous héberge (facture de moins de 6 mois d'eau, d'électricité, de gaz ou de téléphone) ",
                    "type_champ": "piece_justificative", "order_place": 12,
                    "description": ""
                }
            }, {
                "value": "https://url.to.scan/cni_hebergeur",
                "type_de_champ": {
                    "id": 451288,
                    "libelle": "Pièce d'identité de la personne qui vous héberge",
                    "type_champ": "piece_justificative", "order_place": 13,
                    "description": ""
                }
            }, {
                "value": None,
                "type_de_champ": {
                    "id": 460836,
                    "libelle": "Vous n'êtes pas de nationalité française ?",
                    "type_champ": "header_section",
                    "order_place": 14,
                    "description": ""
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451286,
                    "libelle": "Justificatif de présence sur le territoire français depuis plus d'un an",
                    "type_champ": "piece_justificative", "order_place": 15,
                    "description": "Si vous n'êtes pas de la nationalité française, merci de télécharger un document permettant de justifier de votre présence légale sur le territoire depuis plus d'un an."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 466695, "libelle": "Consentement à l'utilisation de mes données",
                    "type_champ": "header_section", "order_place": 16, "description": ""
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 466635, "libelle": "Que faisons-nous de ces données ?",
                    "type_champ": "explication", "order_place": 17,
                    "description": "Ces données ne sont utilisées qu'à la seule fin de nous assurer de votre éligibilité à l'avant-première du pass Culture. Vos données seront contrôlées par l'équipe du pass Culture, puis conservées pendant un an à des fins de contrôle à posteriori."
                }
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 466694,
                    "libelle": "Je donne mon accord au traitement de mes données à caractère personnel dans les conditions explicitées ci-dessus",
                    "type_champ": "engagement", "order_place": 18,
                    "description": ""
                }
            }, {
                "value": "on",
                "type_de_champ": {
                    "id": 457303,
                    "libelle": "Je déclare sur l’honneur que ces documents sont authentiques. ",
                    "type_champ": "engagement",
                    "order_place": 19,
                    "description": "Des contrôles aléatoires seront effectués. En cas de fraude, vous vous exposez à des poursuites judiciaires."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 454775,
                    "libelle": "Un grand merci et à très vite sur le pass Culture !",
                    "type_champ": "header_section", "order_place": 20,
                    "description": ""
                }
            }
        ]
    }
}


def make_applications_list(applications_params: List[Tuple[int, str, str]]) -> dict:
    applications = copy.deepcopy(LIST_APPLICATIONS_STANDARD_RESPONSE)
    for params in applications_params:
        applications['dossiers'].append(
            {
                "id": params[0],
                "state": params[1],
                "updated_at": params[2]
            }
        )
    return applications


def make_application_detail(id: int, state: str) -> dict:
    application = dict(APPLICATION_DETAIL_STANDARD_RESPONSE)
    application['id'] = id
    application['state'] = state
    return application
