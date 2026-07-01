from datetime import date

from pcapi.connectors import api_particulier
from pcapi.core.subscription.bonus.constants import QUOTIENT_FAMILIAL_THRESHOLD
from pcapi.core.users import models as users_models


QUOTIENT_FAMILIAL_FIXTURE = {
    "data": {
        "allocataires": [
            {
                "nom_naissance": "LEFEBVRE",
                "nom_usage": None,
                "prenoms": "ALEXIS GÉRÔME JEAN-PHILIPPE",
                "date_naissance": "1982-12-27",
                "sexe": "M",
            }
        ],
        "enfants": [
            {
                "nom_naissance": "LEFEBVRE",
                "nom_usage": None,
                "prenoms": "LEO",
                "date_naissance": "1990-04-20",
                "sexe": "M",
            }
        ],
        "adresse": {
            "destinataire": "Monsieur LEFEBVRE ALEXIS GÉRÔME JEAN-PHILIPPE",
            "complement_information": None,
            "complement_information_geographique": None,
            "numero_libelle_voie": "1 RUE MONTORGUEIL",
            "lieu_dit": None,
            "code_postal_ville": "75002 PARIS",
            "pays": "FRANCE",
        },
        "quotient_familial": {
            "fournisseur": "CNAF",
            "valeur": QUOTIENT_FAMILIAL_THRESHOLD,
            "annee": 2023,
            "mois": 6,
            "annee_calcul": 2024,
            "mois_calcul": 12,
        },
    },
    "links": {},
    "meta": {},
}

QF_DESERIALIZED_RESPONSE = api_particulier.QuotientFamilialResponse(
    data=api_particulier.QuotientFamilialData(
        allocataires=[
            api_particulier.ApiParticulierPerson(
                nom_naissance="LEFEBVRE",
                prenoms="ALEXIS GÉRÔME JEAN-PHILIPPE",
                date_naissance=date(1982, 12, 27),
                sexe=users_models.GenderEnum.M,
            )
        ],
        enfants=[
            api_particulier.ApiParticulierPerson(
                nom_naissance="LEFEBVRE",
                prenoms="LEO",
                date_naissance=date(1990, 4, 20),
                sexe=users_models.GenderEnum.M,
            )
        ],
        quotient_familial=api_particulier.QuotientFamilial(
            fournisseur="CNAF",
            valeur=2550,
            annee=2023,
            mois=6,
            annee_calcul=2024,
            mois_calcul=12,
        ),
    )
)

# 404 response
APPLICATION_NOT_FOUND_FIXTURE = {
    "errors": [
        {
            "code": "37003",
            "detail": "Le dossier allocataire n'a pas été trouvé auprès de la CNAV.",
            "meta": {"provider": "CNAV"},
            "source": None,
            "title": "Dossier allocataire absent CNAV",
        }
    ]
}

# 422 response
PERSON_NOT_FOUND_FIXTURE = {
    "errors": [
        {
            "code": "00355",
            "title": "Impossible d'identifier l'allocataire",
            "detail": "Les paramètres fournis ne permettent pas d'identifier un allocataire.",
            "meta": {},
        }
    ]
}

# 502 response
DATA_PROVIDER_ERROR = {
    "errors": [
        {
            "code": "36000",
            "title": "Erreur interne du fournisseur de données",
            "detail": "La réponse retournée par le fournisseur de données est invalide et a été identifié comme étant une erreur interne. Si le problème persiste, consultez la page de status ou contactez nous sur le support.",
            "meta": {"provider": "Sécurité sociale"},
        }
    ]
}


AAH_BENEFICIARY_RESPONSE = {
    "data": {"est_beneficiaire": True, "date_debut_droit": "2022-11-29"},
    "links": {},
    "meta": {},
}

AAH_NOT_BENEFICIARY_RESPONSE = {
    "data": {"est_beneficiaire": False, "date_debut_droit": None},
    "links": {},
    "meta": {},
}


AEEH_BENEFICIARY_RESPONSE = {
    "data": {"status": "allocataire", "date_debut_droit": "2023-06-15"},
    "links": {},
    "meta": {},
}

AEEH_NOT_BENEFICIARY_RESPONSE = {
    "data": {"status": "non_beneficiaire", "date_debut_droit": None},
    "links": {},
    "meta": {},
}

AEEH_OPENING_RIGHTS_RESPONSE = {
    "data": {"status": "ouvrant_droit", "date_debut_droit": "2022-11-29"},
    "links": {},
    "meta": {},
}
