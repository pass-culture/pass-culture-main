DS_RESPONSE_GET_INSTRUCTORS = {
    "demarche": {
        "groupeInstructeurs": [
            {
                "instructeurs": [
                    {"id": "SW5wdHK1Y3RleRItFDU4MaEs", "email": "one@example.com"},
                    {"id": "SW5wdHK1Y3RleRItMTAvMEI=", "email": "two@example.com"},
                    {"id": "SW5wdHK1Y3RleRItTbAeMpc6", "email": "other_one@example.com"},
                ]
            },
            {
                "instructeurs": [
                    {"id": "SW5wdHK1Y3RleRItMRAkOCgz", "email": "three@example.com"},
                ]
            },
        ]
    }
}

DS_RESPONSE_EMAIL_CHANGED = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQwODozMTozNS4yNzgyMDMwMDBaOzIxMTYzNTU5",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21163559,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-11-26T09:31:35+01:00",
                    "dateDepot": "2024-11-26T09:31:35+01:00",
                    "datePassageEnConstruction": "2024-11-26T09:31:35+01:00",
                    "datePassageEnInstruction": None,
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T09:31:35+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T09:31:31+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T09:24:22+01:00",
                    "usager": {"email": "usager@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "B\u00e9n\u00e9ficiaire",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [],
                    "champs": [
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjAwOA==",
                            # "label": "Comment remplir ce formulaire de modification d'informations sur mon pass Culture ?",
                            "value": None,
                        },
                        {
                            # "__typename": "DateChamp",
                            "id": "Q2hhbXAtMzM0NjAwOQ==",
                            # "label": "Quelle est ta date de naissance ?",
                            "date": "2006-02-01",
                        },
                        {
                            # "__typename": "MultipleDropDownListChamp",
                            "id": "Q2hhbXAtMzM0NjEyMA==",
                            # "label": "S\u00e9lectionne la modification souhait\u00e9e",
                            "values": ["changement d'adresse de mail"],
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM0NjEzOA==",
                            # "label": "Carte nationale d'identit\u00e9 ou passeport ou titre de s\u00e9jour",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM0NjE0Mw==",
                            # "label": "Prends toi en photo avec ta carte nationale d'identit\u00e9 (recto) ou passeport ou acte de naissance dans la main",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjE0NA==",
                            # "label": "Quelle est ton ancienne adresse mail ?",
                            "value": "beneficiaire@example.com",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjE2MA==",
                            # "label": "Quelle est la nouvelle adresse mail que tu veux utiliser ?",
                            "value": "Nouvelle.Adresse@example.com",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjIzNQ==",
                            # "label": "Consentement \u00e0 l'utilisation de mes donn\u00e9es",
                            "value": None,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjIzOA==",
                            # "label": "J'accepte les conditions g\u00e9n\u00e9rales d'utilisation du pass Culture",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI0MQ==",
                            # "label": "Je donne mon accord au traitement de mes donn\u00e9es \u00e0 caract\u00e8re personnel.",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI1Mw==",
                            # "label": "Je d\u00e9clare sur l\u2019honneur que l'ensemble des r\u00e9ponses et documents fournis sont corrects et authentiques.",
                            "checked": True,
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjI1NA==",
                            # "label": "Un grand merci et \u00e0 tr\u00e8s vite sur le pass Culture !",
                            "value": None,
                        },
                    ],
                    "messages": [
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxMzMzOTA=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": "<p>[Votre dossier n\u00ba 21163559 a bien \u00e9t\u00e9 d\u00e9pos\u00e9 (TEST - Modification d'informations sur mo...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21163559 <strong>a bien \u00e9t\u00e9 d\u00e9pos\u00e9</strong>.\u00a0<br>Si besoin est, vous pouvez encore y apporter des modifications.\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br><br><br>\n</div>",
                            "createdAt": "2024-11-26T09:31:35+01:00",
                            "correction": None,
                        }
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_PHONE_NUMBER_CHANGED = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQxMDowMjo0Ni4yMDgwMTkwMDBaOzIxMTY2NTQ2",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21166546,
                    "archived": False,
                    "state": "en_instruction",
                    "dateDerniereModification": "2024-11-26T11:04:05+01:00",
                    "dateDepot": "2024-11-26T11:02:46+01:00",
                    "datePassageEnConstruction": "2024-11-26T11:02:46+01:00",
                    "datePassageEnInstruction": "2024-11-26T11:03:14+01:00",
                    "dateTraitement": None,
                    "dateExpiration": None,
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T11:02:44+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T11:01:52+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "B\u00e9n\u00e9ficiaire",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjAwOA==",
                            # "label": "Comment remplir ce formulaire de modification d'informations sur mon pass Culture ?",
                            "value": None,
                        },
                        {
                            # "__typename": "DateChamp",
                            "id": "Q2hhbXAtMzM0NjAwOQ==",
                            # "label": "Quelle est ta date de naissance ?",
                            "date": "2006-03-02",
                        },
                        {
                            # "__typename": "MultipleDropDownListChamp",
                            "id": "Q2hhbXAtMzM0NjEyMA==",
                            # "label": "S\u00e9lectionne la modification souhait\u00e9e",
                            "values": ["changement de n\u00b0 de t\u00e9l\u00e9phone"],
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM0NjEzOA==",
                            # "label": "Carte nationale d'identit\u00e9 ou passeport ou titre de s\u00e9jour",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM0NjE0Mw==",
                            # "label": "Prends toi en photo avec ta carte nationale d'identit\u00e9 (recto) ou passeport ou acte de naissance dans la main",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM2MDE5OQ==",
                            # "label": "Quel est ton num\u00e9ro de t\u00e9l\u00e9phone ?",
                            "value": "06.10.20.30.40",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjIzNQ==",
                            # "label": "Consentement \u00e0 l'utilisation de mes donn\u00e9es",
                            "value": None,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjIzOA==",
                            # "label": "J'accepte les conditions g\u00e9n\u00e9rales d'utilisation du pass Culture",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI0MQ==",
                            # "label": "Je donne mon accord au traitement de mes donn\u00e9es \u00e0 caract\u00e8re personnel.",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI1Mw==",
                            # "label": "Je d\u00e9clare sur l\u2019honneur que l'ensemble des r\u00e9ponses et documents fournis sont corrects et authentiques.",
                            "checked": True,
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjI1NA==",
                            # "label": "Un grand merci et \u00e0 tr\u00e8s vite sur le pass Culture !",
                            "value": None,
                        },
                    ],
                    "messages": [
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDA5MzM=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": "<p>[Votre dossier n\u00ba 21166546 a bien \u00e9t\u00e9 d\u00e9pos\u00e9 (TEST - Modification d'informations sur mo...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21166546 <strong>a bien \u00e9t\u00e9 d\u00e9pos\u00e9</strong>.\u00a0<br>Si besoin est, vous pouvez encore y apporter des modifications.\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br><br><br>\n</div>",
                            "createdAt": "2024-11-26T11:02:46+01:00",
                            "correction": None,
                        },
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDA5ODk=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": "<p>[Votre dossier n\u00ba 21166546 va \u00eatre examin\u00e9 (TEST - Modification d'informations sur mon ...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21166546 a bien \u00e9t\u00e9 re\u00e7u et<strong>pris en charge</strong>. Il va maintenant \u00eatre examin\u00e9 par le service.\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br><br><br>\n</div>",
                            "createdAt": "2024-11-26T11:03:14+01:00",
                            "correction": None,
                        },
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDEwNjc=",
                            "email": "instructeur@passculture.app",
                            # "body": "Message de l'instructeur",
                            "createdAt": "2024-11-26T11:04:05+01:00",
                            "correction": None,
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_TWO_APPLICATIONS_FIRST_NAME_LAST_NAME_CHANGED = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQxMDoyMDo1MC44MDEzNzEwMDBaOzIxMTY3MTQ4",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21167090,
                    "archived": False,
                    "state": "accepte",
                    "dateDerniereModification": "2024-11-26T11:21:45+01:00",
                    "dateDepot": "2024-11-26T11:19:35+01:00",
                    "datePassageEnConstruction": "2024-11-26T11:19:35+01:00",
                    "datePassageEnInstruction": "2024-11-26T11:21:24+01:00",
                    "dateTraitement": "2024-11-26T11:21:45+01:00",
                    "dateExpiration": "2025-11-26T11:21:45+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T11:19:24+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T11:18:14+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "B\u00e9n\u00e9ficiaire",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjAwOA==",
                            # "label": "Comment remplir ce formulaire de modification d'informations sur mon pass Culture ?",
                            "value": None,
                        },
                        {
                            # "__typename": "DateChamp",
                            "id": "Q2hhbXAtMzM0NjAwOQ==",
                            # "label": "Quelle est ta date de naissance ?",
                            "date": "2006-04-03",
                        },
                        {
                            # "__typename": "MultipleDropDownListChamp",
                            "id": "Q2hhbXAtMzM0NjEyMA==",
                            # "label": "S\u00e9lectionne la modification souhait\u00e9e",
                            "values": ["changement de pr\u00e9nom"],
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM0NjEzOA==",
                            # "label": "Carte nationale d'identit\u00e9 ou passeport ou titre de s\u00e9jour",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM2MDIwNA==",
                            # "label": "Quel est ton nouveau pr\u00e9nom ?",
                            "value": "Vieux",
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM2MDIwNQ==",
                            # "label": "un document officiel qui atteste du changement de ton pr\u00e9nom ou de nom",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjIzNQ==",
                            # "label": "Consentement \u00e0 l'utilisation de mes donn\u00e9es",
                            "value": None,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjIzOA==",
                            # "label": "J'accepte les conditions g\u00e9n\u00e9rales d'utilisation du pass Culture",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI0MQ==",
                            # "label": "Je donne mon accord au traitement de mes donn\u00e9es \u00e0 caract\u00e8re personnel.",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI1Mw==",
                            # "label": "Je d\u00e9clare sur l\u2019honneur que l'ensemble des r\u00e9ponses et documents fournis sont corrects et authentiques.",
                            "checked": True,
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjI1NA==",
                            # "label": "Un grand merci et \u00e0 tr\u00e8s vite sur le pass Culture !",
                            "value": None,
                        },
                    ],
                    "messages": [
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDI1NDg=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": "<p>[Votre dossier n\u00ba 21167090 a bien \u00e9t\u00e9 d\u00e9pos\u00e9 (TEST - Modification d'informations sur mo...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21167090 <strong>a bien \u00e9t\u00e9 d\u00e9pos\u00e9</strong>.\u00a0<br>Si besoin est, vous pouvez encore y apporter des modifications.\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br><br><br>\n</div>",
                            "createdAt": "2024-11-26T11:19:35+01:00",
                            "correction": None,
                        },
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDI3NDA=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": "<p>[Votre dossier n\u00ba 21167090 va \u00eatre examin\u00e9 (TEST - Modification d'informations sur mon ...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21167090 a bien \u00e9t\u00e9 re\u00e7u et<strong>pris en charge</strong>. Il va maintenant \u00eatre examin\u00e9 par le service.\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br><br><br>\n</div>",
                            "createdAt": "2024-11-26T11:21:24+01:00",
                            "correction": None,
                        },
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDI3OTU=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": '<p>[Votre dossier n\u00ba 21167090 a \u00e9t\u00e9 accept\u00e9 (TEST - Modification d\'informations sur mon co...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21167090 <strong>a \u00e9t\u00e9 accept\u00e9</strong> le 26/11/2024.\u00a0<br><br>\n</div><div>\u00c0 tout moment, vous pouvez consulter votre dossier et les \u00e9ventuels messages de l\'administration \u00e0 cette adresse : <a target="_blank" rel="noopener" href="https://www.demarches-simplifiees.fr/dossiers/21167090">https://www.demarches-simplifiees.fr/dossiers/21167090</a>\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br>\u00a0\u00a0<br><br>\n</div>',
                            "createdAt": "2024-11-26T11:21:45+01:00",
                            "correction": None,
                        },
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDI5MDM=",
                            "email": "beneficiaire@example.com",
                            # "body": "Merci !",
                            "createdAt": "2024-11-26T11:22:51+01:00",
                            "correction": None,
                        },
                    ],
                },
                {
                    "id": "UHJvY4VkdXKlLTI5NTgx",
                    "number": 21167148,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-11-26T11:22:16+01:00",
                    "dateDepot": "2024-11-26T11:20:50+01:00",
                    "datePassageEnConstruction": "2024-11-26T11:20:50+01:00",
                    "datePassageEnInstruction": None,
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T11:20:50+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": "2024-11-26T11:22:16+01:00",
                    "dateDerniereModificationChamps": "2024-11-26T11:20:45+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T11:19:44+01:00",
                    "usager": {"email": "usager@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "Inconnu",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjAwOA==",
                            # "label": "Comment remplir ce formulaire de modification d'informations sur mon pass Culture ?",
                            "value": None,
                        },
                        {
                            # "__typename": "DateChamp",
                            "id": "Q2hhbXAtMzM0NjAwOQ==",
                            # "label": "Quelle est ta date de naissance ?",
                            "date": "2006-05-04",
                        },
                        {
                            # "__typename": "MultipleDropDownListChamp",
                            "id": "Q2hhbXAtMzM0NjEyMA==",
                            # "label": "S\u00e9lectionne la modification souhait\u00e9e",
                            "values": ["changement de nom"],
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM0NjEzOA==",
                            # "label": "Carte nationale d'identit\u00e9 ou passeport ou titre de s\u00e9jour",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtNDU2NzkwOQ==",
                            # "label": "Quel est ton nouveau nom ?",
                            "value": "B\u00e9n\u00e9ficiaire",
                        },
                        {
                            # "__typename": "TitreIdentiteChamp",
                            "id": "Q2hhbXAtMzM2MDIwNQ==",
                            # "label": "un document officiel qui atteste du changement de ton pr\u00e9nom ou de nom",
                            "grantType": "piece_justificative",
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjIzNQ==",
                            # "label": "Consentement \u00e0 l'utilisation de mes donn\u00e9es",
                            "value": None,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjIzOA==",
                            # "label": "J'accepte les conditions g\u00e9n\u00e9rales d'utilisation du pass Culture",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI0MQ==",
                            # "label": "Je donne mon accord au traitement de mes donn\u00e9es \u00e0 caract\u00e8re personnel.",
                            "checked": True,
                        },
                        {
                            # "__typename": "CheckboxChamp",
                            "id": "Q2hhbXAtMzM0NjI1Mw==",
                            # "label": "Je d\u00e9clare sur l\u2019honneur que l'ensemble des r\u00e9ponses et documents fournis sont corrects et authentiques.",
                            "checked": True,
                        },
                        {
                            # "__typename": "TextChamp",
                            "id": "Q2hhbXAtMzM0NjI1NA==",
                            # "label": "Un grand merci et \u00e0 tr\u00e8s vite sur le pass Culture !",
                            "value": None,
                        },
                    ],
                    "messages": [
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDI2ODc=",
                            "email": "contact@demarches-simplifiees.fr",
                            # "body": "<p>[Votre dossier n\u00ba 21167148 a bien \u00e9t\u00e9 d\u00e9pos\u00e9 (TEST - Modification d'informations sur mo...]</p><div>Bonjour,<br><br>\n</div><div>Votre dossier n\u00ba 21167148 <strong>a bien \u00e9t\u00e9 d\u00e9pos\u00e9</strong>.\u00a0<br>Si besoin est, vous pouvez encore y apporter des modifications.\u00a0<br><br>\n</div><div>Bonne journ\u00e9e,<br><br><br>\n</div>",
                            "createdAt": "2024-11-26T11:20:50+01:00",
                            "correction": None,
                        },
                        {
                            # "id": "Q29tbWVudGFpcmUtNTAxNDI4NDM=",
                            "email": "instructeur@passculture.app",
                            # "body": "Correction demand\u00e9e",
                            "createdAt": "2024-11-26T11:21:16+01:00",
                            "correction": {"dateResolution": None},
                        },
                        {
                            "email": "oldinstructeur@passculture.app",
                            # "body": "Bonjour, je suis un vieil instructeur",
                            "createdAt": "2024-11-26T11:22:16+01:00",
                        },
                    ],
                },
            ],
        },
    }
}

DS_RESPONSE_ACCOUNT_HAS_SAME = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQxNToxNDoxNC4yNTgyMjEwMDBaOzIxMTc2MTkz",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21176193,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-11-26T16:14:14+01:00",
                    "dateDepot": "2024-11-26T16:14:14+01:00",
                    "datePassageEnConstruction": "2024-11-26T16:14:14+01:00",
                    "datePassageEnInstruction": None,
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T16:14:14+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T16:14:02+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T16:13:30+01:00",
                    "usager": {"email": "jeune@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {"nom": "En d\u00e9tresse", "prenom": "Jeune", "email": None},
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-07-06"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["compte a les m\u00eames informations"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T16:14:14+01:00",
                            "correction": None,
                        }
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_APPLIED_BY_PROXY = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {"hasNextPage": False, "endCursor": "MjAyNC0xMS0yNlQxNTo1NToxNC44MTgyNTAwMDBaOzIxMTc2OTk3"},
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21176997,
                    "archived": False,
                    "state": "en_instruction",
                    "dateDerniereModification": "2024-11-26T16:55:14+01:00",
                    "dateDepot": "2024-11-26T16:43:28+01:00",
                    "datePassageEnConstruction": "2024-11-26T16:43:28+01:00",
                    "datePassageEnInstruction": "2024-11-26T16:54:29+01:00",
                    "dateTraitement": None,
                    "dateExpiration": None,
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T16:42:12+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T16:39:21+01:00",
                    "usager": {"email": "papamaman@example.com"},
                    "prenomMandataire": "Papa",
                    "nomMandataire": "Maman",
                    "deposeParUnTiers": True,
                    "demandeur": {"nom": "Enfant", "prenom": "Jeune", "email": "jeune@example.com"},
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"email": "instructeur@passculture.app"}],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-08-07"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["changement de n\u00b0 de t\u00e9l\u00e9phone"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM2MDE5OQ==", "value": "07-33-44-55-66"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T16:43:28+01:00",
                            "correction": None,
                        },
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T16:54:29+01:00",
                            "correction": None,
                        },
                        {
                            "email": "instructeur@passculture.app",
                            "createdAt": "2024-11-26T16:55:14+01:00",
                            "correction": None,
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_CORRECTION_RESOLVED = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {"hasNextPage": False, "endCursor": "MjAyNC0xMS0yNlQxNjowNTozMi40NzMwNjEwMDBaOzIxMTc3NzQ0"},
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21177744,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-11-26T17:05:32+01:00",
                    "dateDepot": "2024-11-26T17:04:27+01:00",
                    "datePassageEnConstruction": "2024-11-26T17:04:27+01:00",
                    "datePassageEnInstruction": None,
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T17:04:27+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T17:05:32+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T17:03:43+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {"nom": "B\u00e9n\u00e9ficiaire", "prenom": "Jeune", "email": None},
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"email": "instructeur@passculture.app"}],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-09-08"},
                        {
                            "id": "Q2hhbXAtMzM0NjEyMA==",
                            "values": ["changement d'adresse de mail", "changement de n\u00b0 de t\u00e9l\u00e9phone"],
                        },
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0NA==", "value": "ancienne.adresse@example.com"},
                        {"id": "Q2hhbXAtMzM0NjE2MA==", "value": "Nouvelle.Adresse@example.com"},
                        {"id": "Q2hhbXAtMzM2MDE5OQ==", "value": "0733445566"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T17:04:27+01:00",
                            "correction": None,
                        },
                        {
                            "email": "instructeur@passculture.app",
                            "createdAt": "2024-11-26T17:05:04+01:00",
                            "correction": {"dateResolution": "2024-11-26T17:05:32+01:00"},
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_MISSING_VALUE = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {"hasNextPage": False, "endCursor": "MjAyNC0xMS0yNlQxNzoxOTo0Mi41NzE3NDIwMDBaOzIxMTc5MjI0"},
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21179224,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-11-26T18:19:42+01:00",
                    "dateDepot": "2024-11-26T18:19:42+01:00",
                    "datePassageEnConstruction": "2024-11-26T18:19:42+01:00",
                    "datePassageEnInstruction": None,
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T18:19:42+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T18:19:41+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T18:18:37+01:00",
                    "usager": {"email": "Nouvelle.Adresse@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {"nom": "B\u00e9n\u00e9ficiaire", "prenom": "Jeune", "email": None},
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": None},  # birth date missing
                        {
                            "id": "Q2hhbXAtMzM0NjEyMA==",
                            "values": ["changement d'adresse de mail", "changement de n\u00b0 de t\u00e9l\u00e9phone"],
                        },
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0NA==", "value": None},  # old email missing
                        {"id": "Q2hhbXAtMzM0NjE2MA==", "value": "Nouvelle.Adresse@example.com"},
                        {"id": "Q2hhbXAtMzM2MDE5OQ==", "value": None},  # new phone number missing
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T18:19:42+01:00",
                            "correction": None,
                        }
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_INVALID_VALUE = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {"hasNextPage": False, "endCursor": "MjAyNC0xMS0yN1QxNDoyNTowMy40NDU4NjAwMDBaOzIxMTkzNjM3"},
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21193637,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-11-27T15:25:03+01:00",
                    "dateDepot": "2024-11-27T15:25:03+01:00",
                    "datePassageEnConstruction": "2024-11-27T15:25:03+01:00",
                    "datePassageEnInstruction": None,
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-27T15:25:03+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-27T15:25:01+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-27T15:24:04+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {"nom": "B\u00e9n\u00e9ficiaire", "prenom": "Jeune", "email": None},
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-11-10"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["changement de n\u00b0 de t\u00e9l\u00e9phone"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM2MDE5OQ==", "value": "0700000000"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-27T15:25:03+01:00",
                            "correction": None,
                        }
                    ],
                }
            ],
        },
    }
}


DS_RESPONSE_EMAIL_CHANGED_WITH_SET_WITHOUT_CONTINUATION = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQwODozMTozNS4yNzgyMDMwMDBaOzIxMTYzNTU5",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21163559,
                    "archived": False,
                    "state": "en_instruction",
                    "dateDerniereModification": "2024-12-10T17:12:00+01:00",
                    "dateDepot": "2025-01-16T09:31:35+01:00",
                    "datePassageEnConstruction": "2025-01-16T09:31:35+01:00",
                    "datePassageEnInstruction": "2025-01-16T10:31:35+01:00",
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T09:31:35+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-12-10T17:12:00+01:00",
                    "dateDerniereModificationAnnotations": "2025-01-16T09:24:22+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "B\u00e9n\u00e9ficiaire",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-06-05"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["changement d'adresse de mail"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0NA==", "value": "other@example.com"},
                        {"id": "Q2hhbXAtMzM0NjE2MA==", "value": "Nouvelle.Adresse@example.com"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2025-01-16T09:31:35+01:00",
                            "correction": None,
                        },
                        {
                            "email": "instructeur@passculture.app",
                            "createdAt": "2024-12-12T12:12:00+01:00",
                            "correction": None,
                        },
                        {
                            "email": "beneficiaire@example.com",
                            "createdAt": "2024-12-07T12:12:00+01:00",
                            "correction": None,
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_FIRSTNAME_CHANGED_WITH_SET_WITHOUT_CONTINUATION = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQwODozMTozNS4yNzgyMDMwMDBaOzIxMTYzNTU5",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21163559,
                    "archived": False,
                    "state": "en_instruction",
                    "dateDerniereModification": "2024-12-10T17:12:00+01:00",
                    "dateDepot": "2025-01-16T09:31:35+01:00",
                    "datePassageEnConstruction": "2025-01-16T09:31:35+01:00",
                    "datePassageEnInstruction": "2025-01-16T10:31:35+01:00",
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T09:31:35+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-12-10T17:12:00+01:00",
                    "dateDerniereModificationAnnotations": "2025-01-16T09:24:22+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "B\u00e9n\u00e9ficiaire",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-06-05"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["changement de pr\u00e9nom"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM2MDIwNA==", "value": "Nouveau"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2025-01-16T09:31:35+01:00",
                            "correction": None,
                        },
                        {
                            "email": "instructeur@passculture.app",
                            "createdAt": "2024-12-12T12:12:00+01:00",
                            "correction": None,
                        },
                        {
                            "email": "beneficiaire@example.com",
                            "createdAt": "2024-12-07T12:12:00+01:00",
                            "correction": None,
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_EMAIL_CHANGED_FROM_DRAFT_WITH_SET_WITHOUT_CONTINUATION = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQwODozMTozNS4yNzgyMDMwMDBaOzIxMTYzNTU5",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21163559,
                    "archived": False,
                    "state": "en_construction",
                    "dateDerniereModification": "2024-12-10T17:12:00+01:00",
                    "dateDepot": "2025-01-16T09:31:35+01:00",
                    "datePassageEnConstruction": "2025-01-16T09:31:35+01:00",
                    "datePassageEnInstruction": "2025-01-16T10:31:35+01:00",
                    "dateTraitement": None,
                    "dateExpiration": "2025-11-26T09:31:35+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-12-10T17:12:00+01:00",
                    "dateDerniereModificationAnnotations": "2025-01-16T09:24:22+01:00",
                    "usager": {"email": "beneficiaire@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "B\u00e9n\u00e9ficiaire",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-06-05"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["changement d'adresse de mail"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0NA==", "value": "beneficiaire@example.com"},
                        {"id": "Q2hhbXAtMzM0NjE2MA==", "value": "Nouvelle.Adresse@example.com"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2025-01-16T09:31:35+01:00",
                            "correction": None,
                        },
                        {
                            "email": "instructeur@passculture.app",
                            "createdAt": "2024-12-12T12:12:00+01:00",
                            "correction": None,
                        },
                        {
                            "email": "beneficiaire@example.com",
                            "createdAt": "2024-12-07T12:12:00+01:00",
                            "correction": None,
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_ARCHIVED = {
    "demarche": {
        "number": 104118,
        "dossiers": {
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "MjAyNC0xMS0yNlQxMDo1Mjo0NC40NzEyMTcwMDBaOzIxMTY4Mjc2",
            },
            "nodes": [
                {
                    "id": "UHJvY4VkdXKlLTI5NTgw",
                    "number": 21168276,
                    "archived": True,
                    "state": "sans_suite",
                    "dateDerniereModification": "2024-11-26T11:54:41+01:00",
                    "dateDepot": "2024-11-26T11:52:44+01:00",
                    "datePassageEnConstruction": "2024-11-26T11:52:44+01:00",
                    "datePassageEnInstruction": "2024-11-26T11:54:16+01:00",
                    "dateTraitement": "2024-11-26T11:54:32+01:00",
                    "dateExpiration": "2025-11-26T11:54:32+01:00",
                    "dateSuppressionParUsager": None,
                    "dateDerniereCorrectionEnAttente": None,
                    "dateDerniereModificationChamps": "2024-11-26T11:52:41+01:00",
                    "dateDerniereModificationAnnotations": "2024-11-26T11:51:46+01:00",
                    "usager": {"email": "usager@example.com"},
                    "prenomMandataire": None,
                    "nomMandataire": None,
                    "deposeParUnTiers": False,
                    "demandeur": {
                        "nom": "Usager",
                        "prenom": "Jeune",
                        "email": None,
                    },
                    "demarche": {"revision": {"id": "UHJvY2VkdXJlUmV2aXNpb24tMTYyOTUz"}},
                    "instructeurs": [{"id": "SW5zdHJ1Y3RldXItMTAyOTgz", "email": "instructeur@passculture.app"}],
                    "champs": [
                        {"id": "Q2hhbXAtMzM0NjAwOA==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjAwOQ==", "date": "2006-06-05"},
                        {"id": "Q2hhbXAtMzM0NjEyMA==", "values": ["changement d'adresse de mail"]},
                        {"id": "Q2hhbXAtMzM0NjEzOA==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0Mw==", "grantType": "piece_justificative"},
                        {"id": "Q2hhbXAtMzM0NjE0NA==", "value": "ancienne.adresse@example.com"},
                        {"id": "Q2hhbXAtMzM0NjE2MA==", "value": "Nouvelle.Adresse@example.com"},
                        {"id": "Q2hhbXAtMzM0NjIzNQ==", "value": None},
                        {"id": "Q2hhbXAtMzM0NjIzOA==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI0MQ==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1Mw==", "checked": True},
                        {"id": "Q2hhbXAtMzM0NjI1NA==", "value": None},
                    ],
                    "messages": [
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T11:52:44+01:00",
                            "correction": None,
                        },
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T11:54:16+01:00",
                            "correction": None,
                        },
                        {
                            "email": "contact@demarches-simplifiees.fr",
                            "createdAt": "2024-11-26T11:54:32+01:00",
                            "correction": None,
                        },
                    ],
                }
            ],
        },
    }
}

DS_RESPONSE_DELETED_APPLICATIONS = {
    "demarche": {
        "id": "UHJvY2VkdXJlLTEwNDExOA==",
        "number": 104118,
        "deletedDossiers": {
            "pageInfo": {
                "endCursor": "MjAyVC0wNy2wMlQw4To1NDo0MC4CNzgyFjAwMDyaOzMzOTA4ODc",
                "hasNextPage": False,
            },
            "nodes": [
                {
                    "dateSupression": "2025-01-01T07:23:31+02:00",
                    "id": "RGVsZX5lZ8Rvc6NpZX5RtMGV4MT54NA==",
                    "number": 10000001,
                    "reason": "user_request",
                    "state": "en_construction",
                },
                {
                    "dateSupression": "2025-01-02T07:34:53+02:00",
                    "id": "RGVsfZRlZERrKsBpZXetMTA5MTQzOQ==",
                    "number": 10000003,
                    "reason": "expired",
                    "state": "accepte",
                },
                {
                    "dateSupression": "2025-01-03T02:04:58+02:00",
                    "id": "RGVsZXRlREoGS3N4ZXI4MTIrNjQ0NQ==",
                    "number": 10000004,
                    "reason": "expired",
                    "state": "refuse",
                },
            ],
        },
    }
}

DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING = {
    "dossierPasserEnInstruction": {
        "dossier": {
            "id": "UHJvY4VkdXKlLTI5NTgw",
            "number": 21163559,
            "state": "en_instruction",
            "dateDerniereModification": "2024-12-02T18:20:53+01:00",
            "dateDepot": "2024-12-02T18:16:50+01:00",
            "datePassageEnConstruction": "2024-12-02T18:19:39+01:00",
            "datePassageEnInstruction": "2024-12-02T18:20:53+01:00",
            "dateTraitement": None,
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2024-12-02T18:16:49+01:00",
        },
        "errors": None,
    }
}

DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_ON_GOING = {
    "dossierPasserEnInstruction": {"dossier": None, "errors": [{"message": "Le dossier est déjà en instruction"}]}
}

DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_ACCEPTED = {
    "dossierAccepter": {
        "dossier": {
            "id": "UHJvY4VkdXKlLTI5NTgw",
            "number": 21268381,
            "state": "accepte",
            "dateDerniereModification": "2024-12-05T12:17:10+01:00",
            "dateDepot": "2024-12-02T15:37:29+01:00",
            "datePassageEnConstruction": "2024-12-05T12:15:55+01:00",
            "datePassageEnInstruction": "2024-12-05T12:16:03+01:00",
            "dateTraitement": "2024-12-05T12:17:10+01:00",
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2024-12-02T15:37:28+01:00",
        },
        "errors": None,
    }
}

DS_RESPONSE_UPDATE_STATE_ACCEPTED_TO_ACCEPTED = {
    "dossierAccepter": {"dossier": None, "errors": [{"message": "Le dossier est d\u00e9j\u00e0 accept\u00e9"}]}
}


DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION = {
    "dossierClasserSansSuite": {
        "dossier": {
            "id": "UHJvY4VkdXKlLTI5NTgw",
            "number": 21163559,
            "state": "sans_suite",
            "dateDerniereModification": "2025-01-15T17:54:59+01:00",
            "dateDepot": "2025-01-15T16:28:45+01:00",
            "datePassageEnConstruction": "2025-01-15T17:20:09+01:00",
            "datePassageEnInstruction": "2025-01-15T17:52:58+01:00",
            "dateTraitement": "2025-01-15T17:54:59+01:00",
            "dateDerniereCorrectionEnAttente": None,
            "dateDerniereModificationChamps": "2025-01-15T17:20:53+01:00",
        },
        "errors": None,
    }
}

DS_RESPONSE_UPDATE_STATE_ACCEPTED_TO_WITHOUT_CONTINUATION = {
    "dossierClasserSansSuite": {"dossier": None, "errors": [{"message": "Le dossier est déjà accepté"}]}
}

DS_RESPONSE_UPDATE_STATE_REFUSED_TO_WITHOUT_CONTINUATION = {
    "dossierClasserSansSuite": {"dossier": None, "errors": [{"message": "Le dossier est déjà refusé"}]}
}

DS_RESPONSE_UPDATE_STATE_DRAFT_TO_WITHOUT_CONTINUATION = {
    "dossierClasserSansSuite": {
        "dossier": None,
        "errors": [{"message": "Le dossier est déjà en\xa0construction"}],
    }
}

DS_RESPONSE_UPDATE_STATE_WITHOUT_CONTINUATION_TO_WITHOUT_CONTINUATION = {
    "dossierClasserSansSuite": {
        "dossier": None,
        "errors": [{"message": "Le dossier est déjà classé sans suite"}],
    }
}


DS_RESPONSE_ARCHIVE = {
    "dossierArchiver": {
        "dossier": {
            "id": "RG9zc2llci0yMTgzNTc0OQ==",
        },
        "errors": None,
    }
}

DS_RESPONSE_ARCHIVE_ERROR_NOT_INSTRUCTED = {
    "dossierArchiver": {
        "dossier": None,
        "errors": [
            {"message": "Un dossier ne peut être déplacé dans « à archiver » qu’une fois le traitement terminé"}
        ],
    }
}
