RESPONSE_CLOSED_SIREN_PAGE1 = {
    "header": {
        "statut": 200,
        "message": "OK",
        "total": 5,
        "debut": 0,
        "nombre": 3,
        "curseur": "*",
        "curseurSuivant": "AoEpODg5Mjg4Mzc5",
    },
    "unitesLegales": [
        {
            "siren": "111111118",
            "dateDernierTraitementUniteLegale": "2025-01-26T12:34:56.789",
            "periodesUniteLegale": [
                {"dateFin": None, "dateDebut": "2025-01-25", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2025-01-24", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "A"},
            ],
        },
        {
            "siren": "222222226",
            "dateDernierTraitementUniteLegale": "2025-01-26T12:34:56.789",
            "periodesUniteLegale": [
                {"dateFin": None, "dateDebut": "2024-12-31", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2024-12-30", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "A"},
            ],
        },
        {
            "siren": "333333334",
            "dateDernierTraitementUniteLegale": "2025-01-26T12:34:56.789",
            "periodesUniteLegale": [
                {"dateFin": None, "dateDebut": "2032-12-31", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2032-12-30", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "A"},
            ],
        },
    ],
}

RESPONSE_CLOSED_SIREN_PAGE2 = {
    "header": {
        "statut": 200,
        "message": "OK",
        "total": 5,
        "debut": 3,
        "nombre": 2,
        "curseur": "AoEpODg5Mjg4Mzc5",
        "curseurSuivant": "AoEpODg5Mjg4Mzc5",
    },
    "unitesLegales": [
        {
            "siren": "444444442",
            "dateDernierTraitementUniteLegale": "2025-01-26T12:34:56.789",
            "periodesUniteLegale": [
                {"dateFin": None, "dateDebut": "2033-01-01", "etatAdministratifUniteLegale": "A"},
                {"dateFin": "2032-12-31", "dateDebut": "2025-02-17", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2025-02-16", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2024-12-30", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "A"},
            ],
        },
        {
            "siren": "555555556",
            "dateDernierTraitementUniteLegale": "2025-01-26T12:34:56.789",
            "periodesUniteLegale": [
                {"dateFin": None, "dateDebut": "2025-01-17", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2025-01-16", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "C"},
                {"dateFin": "2024-12-30", "dateDebut": "2024-01-01", "etatAdministratifUniteLegale": "A"},
            ],
        },
    ],
}
