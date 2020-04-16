import copy

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
                "body": "...",
                "created_at": "2019-05-04T18:01:24.428Z",
                "attachment": None
            },
            {
                "email": "contact@demarches-simplifiees.fr",
                "body": "...",
                "created_at": "2019-05-07T15:15:22.504Z",
                "attachment": None
            },
            {
                "email": "contact@demarches-simplifiees.fr",
                "body": "...",
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
                "value": None,
                "type_de_champ": {
                    "id": 609447,
                    "libelle": "Comment remplir ce formulaire de pré-inscription au pass Culture",
                    "type_champ": "explication", "order_place": 0,
                    "description": "Une aide pour remplir votre dossier est disponible ici : https://docs.passculture.app/experimentateurs/pre-inscription"}
            },
            {
                "value": "94 - Val-de-Marne",
                "type_de_champ": {
                    "id": 596453, "libelle": "Veuillez indiquer votre département",
                    "type_champ": "departements", "order_place": 1,
                    "description": "Département de résidence (vous devrez fournir un justificatif de domicile)."
                }
            },
            {
                "value": "0123456789",
                "type_de_champ": {
                    "id": 582219, "libelle": "Numéro de téléphone",
                    "type_champ": "phone", "order_place": 2, "description": ""
                }
            },
            {
                "value": "2000-05-01",
                "type_de_champ": {
                    "id": 582220, "libelle": "Date de naissance", "type_champ": "date",
                    "order_place": 3,
                    "description": "Assurez-vous de bien sélectionner votre année de naissance."
                }
            },
            {
                "value": "94200",
                "type_de_champ": {
                    "id": 639254, "libelle": "Code postal de votre lieu de naissance",
                    "type_champ": "text", "order_place": 4, "description": None
                }
            },
            {
                "value": "Étudiant",
                "type_de_champ":
                    {
                        "id":718094,
                        "libelle":"Veuillez indiquer votre statut",
                        "type_champ":"drop_down_list",
                        "order_place":7,
                        "description":""
                    }
            },
            {
                "value": "6 rue de la République",
                "type_de_champ": {
                    "id": 582223, "libelle": "Adresse de résidence",
                    "type_champ": "address", "order_place": 5, "description": None
                }
            },
            {
                "value": "67200",
                "type_de_champ": {
                    "id": 582221,
                    "libelle": "Code postal de votre adresse de résidence",
                    "type_champ": "text", "order_place": 6,
                    "description": None
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 582328,
                    "libelle": "Pièces justificatives",
                    "type_champ": "explication",
                    "order_place": 7,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 609392, "libelle": "1. Pièce d'identité",
                    "type_champ": "header_section", "order_place": 8,
                    "description": None
                }
            },
            {
                "value": "http://fake.url",
                "type_de_champ": {
                    "id": 459819,
                    "libelle": "Pièce d'identité (numérisation RECTO seul de votre carte d'identité ou passeport)",
                    "type_champ": "piece_justificative", "order_place": 9,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451284,
                    "libelle": "2.1 Si vous avez un justificatif de domicile à votre nom :",
                    "type_champ": "header_section", "order_place": 10,
                    "description": ""
                }
            },
            {
                "value": "http://fake.url",
                "type_de_champ": {
                    "id": 422858,
                    "libelle": "Justificatif de domicile à votre nom et prénom",
                    "type_champ": "piece_justificative", "order_place": 11,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 460834,
                    "libelle": "2.2 Sinon, si vous habitez chez un proche (parent, ami, etc.) :",
                    "type_champ": "header_section", "order_place": 12,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 460835,
                    "libelle": "Justificatif de domicile de la personne qui vous héberge",
                    "type_champ": "piece_justificative",
                    "order_place": 13,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451287,
                    "libelle": "Attestation sur l'honneur d'hébergement, datée et signée par la personne qui vous héberge et par vous-même",
                    "type_champ": "piece_justificative",
                    "order_place": 14,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451288,
                    "libelle": "Pièce d'identité de la personne qui vous héberge",
                    "type_champ": "piece_justificative",
                    "order_place": 15,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 460836,
                    "libelle": "Vous n'êtes pas de nationalité française ?",
                    "type_champ": "header_section", "order_place": 16,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 451286,
                    "libelle": "Justificatif de présence sur le territoire français depuis plus d'un an",
                    "type_champ": "piece_justificative",
                    "order_place": 17,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 466695,
                    "libelle": "Consentement à l'utilisation de mes données",
                    "type_champ": "header_section", "order_place": 18,
                    "description": "..."
                }
            },
            {
                "value": None,

                "type_de_champ": {
                    "id": 466635,
                    "libelle": "Que faisons-nous de ces données ?",
                    "type_champ": "explication",
                    "order_place": 19,
                    "description": "..."
                }
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 466694,
                    "libelle": "Je donne mon accord au traitement de mes données à caractère personnel dans les conditions explicitées ci-dessus",
                    "type_champ": "engagement", "order_place": 20,
                    "description": "..."
                }
            },
            {
                "value": "on",
                "type_de_champ": {
                    "id": 457303,
                    "libelle": "Je déclare sur l’honneur que ces documents sont authentiques. ",
                    "type_champ": "engagement",
                    "order_place": 21,
                    "description": "..."
                }
            },
            {
                "value": None,
                "type_de_champ": {
                    "id": 454775,
                    "libelle": "Un grand merci et à très vite sur le pass Culture !",
                    "type_champ": "header_section", "order_place": 22,
                    "description": "..."
                }
            }
        ]
    }
}


def make_old_application_detail(id: int, state: str, postal_code='67200', department_code='67 - Bas-Rhin',
                            civility='Mme', activity='Étudiant') -> dict:
    application = copy.deepcopy(APPLICATION_DETAIL_STANDARD_RESPONSE)
    application['dossier']['id'] = id
    application['dossier']['state'] = state
    application['dossier']['individual']['civilite'] = civility
    for field in application['dossier']['champs']:
        if field['type_de_champ']['libelle'] == 'Veuillez indiquer votre département':
            field['value'] = department_code
        if field['type_de_champ']['libelle'] == 'Code postal de votre adresse de résidence':
            field['value'] = postal_code
        if field['type_de_champ']['libelle'] == 'Veuillez indiquer votre statut':
            field['value'] = activity
    return application
