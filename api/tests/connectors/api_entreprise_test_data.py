RESPONSE_SIREN_COMPANY = {
    "data": {
        "siren": "123456789",
        "rna": None,
        "siret_siege_social": "12345678900012",
        "categorie_entreprise": "PME",
        "type": "personne_morale",
        "personne_morale_attributs": {"raison_sociale": "LE PETIT RINTINTIN", "sigle": None},
        "personne_physique_attributs": {
            "pseudonyme": None,
            "prenom_usuel": None,
            "prenom_1": None,
            "prenom_2": None,
            "prenom_3": None,
            "prenom_4": None,
            "nom_usage": None,
            "nom_naissance": None,
            "sexe": None,
        },
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "forme_juridique": {"code": "5710", "libelle": "SAS, soci\u00e9t\u00e9 par actions simplifi\u00e9e"},
        "activite_principale": {
            "code": "47.61Z",
            "nomenclature": "NAFRev2",
            "libelle": "Commerce de d\u00e9tail de livres en magasin sp\u00e9cialis\u00e9",
        },
        "tranche_effectif_salarie": {
            "de": 100,
            "a": 199,
            "code": "22",
            "date_reference": "2021",
            "intitule": "100 \u00e0 199 salari\u00e9s",
        },
        "etat_administratif": "A",
        "economie_sociale_et_solidaire": False,
        "date_cessation": None,
        "date_creation": 1563832800,
    },
    "links": {
        "siege_social": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/12345678900012",
        "siege_social_adresse": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/12345678900012/adresse",
    },
    "meta": {"date_derniere_mise_a_jour": 1701298800, "redirect_from_siren": None},
}

RESPONSE_SIRET_COMPANY = {
    "data": {
        "siret": "12345678900012",
        "siege_social": True,
        "etat_administratif": "A",
        "date_fermeture": None,
        "enseigne": None,
        "activite_principale": {
            "code": "47.61Z",
            "nomenclature": "NAFRev2",
            "libelle": "Commerce de d\u00e9tail de livres en magasin sp\u00e9cialis\u00e9",
        },
        "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "date_creation": 1677625200,
        "unite_legale": {
            "siren": "123456789",
            "rna": None,
            "siret_siege_social": "12345678900012",
            "type": "personne_morale",
            "personne_morale_attributs": {"raison_sociale": "LE PETIT RINTINTIN", "sigle": None},
            "personne_physique_attributs": {
                "pseudonyme": None,
                "prenom_usuel": None,
                "prenom_1": None,
                "prenom_2": None,
                "prenom_3": None,
                "prenom_4": None,
                "nom_usage": None,
                "nom_naissance": None,
                "sexe": None,
            },
            "categorie_entreprise": "PME",
            "status_diffusion": "diffusible",
            "diffusable_commercialement": True,
            "forme_juridique": {"code": "5710", "libelle": "SAS, soci\u00e9t\u00e9 par actions simplifi\u00e9e"},
            "activite_principale": {
                "code": "47.61Z",
                "nomenclature": "NAFRev2",
                "libelle": "Commerce de d\u00e9tail de livres en magasin sp\u00e9cialis\u00e9",
            },
            "tranche_effectif_salarie": {
                "de": 100,
                "a": 199,
                "code": "22",
                "date_reference": "2021",
                "intitule": "100 \u00e0 199 salari\u00e9s",
            },
            "economie_sociale_et_solidaire": False,
            "date_creation": 1563832800,
            "etat_administratif": "A",
        },
        "adresse": {
            "status_diffusion": "diffusible",
            "complement_adresse": None,
            "numero_voie": "12",
            "indice_repetition_voie": "BIS",
            "type_voie": "AVENUE",
            "libelle_voie": "DU LIVRE",
            "code_postal": "58400",
            "libelle_commune": "LA CHARITE-SUR-LOIRE",
            "libelle_commune_etranger": None,
            "distribution_speciale": None,
            "code_commune": "58059",
            "code_cedex": None,
            "libelle_cedex": None,
            "code_pays_etranger": None,
            "libelle_pays_etranger": None,
            "acheminement_postal": {
                "l1": "LE PETIT RINTINTIN",
                "l2": "",
                "l3": "",
                "l4": "12 BIS AVENUE DU LIVRE",
                "l5": "",
                "l6": "58400 LA CHARITE-SUR-LOIRE",
                "l7": "FRANCE",
            },
        },
    },
    "links": {"unite_legale": "https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/123456789"},
    "meta": {"date_derniere_mise_a_jour": 1683151200, "redirect_from_siret": None},
}

RESPONSE_SIREN_ENTREPRISE_INDIVIDUELLE = {
    "data": {
        "siren": "111222333",
        "rna": None,
        "siret_siege_social": "11122233300022",
        "categorie_entreprise": "PME",
        "type": "personne_physique",
        "personne_morale_attributs": {"raison_sociale": None, "sigle": None},
        "personne_physique_attributs": {
            "pseudonyme": None,
            "prenom_usuel": "MARIE",
            "prenom_1": "MARIA",
            "prenom_2": "SALOMEA",
            "prenom_3": None,
            "prenom_4": None,
            "nom_usage": "CURIE",
            "nom_naissance": "SKLODOWSKA",
            "sexe": "F",
        },
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "forme_juridique": {"code": "1000", "libelle": "Entrepreneur individuel"},
        "activite_principale": {
            "code": "72.19Z",
            "nomenclature": "NAFRev2",
            "libelle": "Recherche-d\u00e9veloppement en autres sciences physiques et naturelles",
        },
        "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
        "etat_administratif": "A",
        "economie_sociale_et_solidaire": None,
        "date_cessation": None,
        "date_creation": 1704063600,
    },
    "links": {
        "siege_social": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/11122233300022",
        "siege_social_adresse": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/11122233300022/adresse",
    },
    "meta": {"date_derniere_mise_a_jour": 1704063600, "redirect_from_siren": None},
}

RESPONSE_SIRET_ENTREPRISE_INDIVIDUELLE = {
    "data": {
        "siret": "11122233300022",
        "siege_social": True,
        "etat_administratif": "A",
        "date_fermeture": None,
        "enseigne": None,
        "activite_principale": {
            "code": "72.19Z",
            "nomenclature": "NAFRev2",
            "libelle": "Recherche-d\u00e9veloppement en autres sciences physiques et naturelles",
        },
        "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "date_creation": 1704063600,
        "unite_legale": {
            "siren": "111222333",
            "rna": None,
            "siret_siege_social": "11122233300022",
            "type": "personne_physique",
            "personne_morale_attributs": {"raison_sociale": None, "sigle": None},
            "personne_physique_attributs": {
                "pseudonyme": None,
                "prenom_usuel": "MARIE",
                "prenom_1": "MARIA",
                "prenom_2": "SALOMEA",
                "prenom_3": None,
                "prenom_4": None,
                "nom_usage": "CURIE",
                "nom_naissance": "SKLODOWSKA",
                "sexe": "F",
            },
            "categorie_entreprise": "PME",
            "status_diffusion": "diffusible",
            "diffusable_commercialement": True,
            "forme_juridique": {"code": "1000", "libelle": "Entrepreneur individuel"},
            "activite_principale": {
                "code": "72.19Z",
                "nomenclature": "NAFRev2",
                "libelle": "Recherche-d\u00e9veloppement en autres sciences physiques et naturelles",
            },
            "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
            "economie_sociale_et_solidaire": None,
            "date_creation": 1704063600,
            "etat_administratif": "A",
        },
        "adresse": {
            "status_diffusion": "diffusible",
            "complement_adresse": None,
            "numero_voie": "36",
            "indice_repetition_voie": None,
            "type_voie": "QUAI",
            "libelle_voie": "DE BETHUNE",
            "code_postal": "75004",
            "libelle_commune": "PARIS 4",
            "libelle_commune_etranger": None,
            "distribution_speciale": None,
            "code_commune": "75104",
            "code_cedex": None,
            "libelle_cedex": None,
            "code_pays_etranger": None,
            "libelle_pays_etranger": None,
            "acheminement_postal": {
                "l1": "",
                "l2": "CURIE MARIE",
                "l3": "",
                "l4": "36 QUAI DE BETHUNE",
                "l5": "",
                "l6": "75004 PARIS 4",
                "l7": "FRANCE",
            },
        },
    },
    "links": {"unite_legale": "https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/111222333"},
    "meta": {"date_derniere_mise_a_jour": 1704063600, "redirect_from_siret": None},
}

RESPONSE_SIREN_COMPANY_WITH_NON_PUBLIC_DATA = {
    "data": {
        "siren": "987654321",
        "rna": None,
        "siret_siege_social": "98765432100016",
        "categorie_entreprise": "PME",
        "type": "personne_physique",
        "personne_morale_attributs": {"raison_sociale": None, "sigle": None},
        "personne_physique_attributs": {
            "pseudonyme": None,
            "prenom_usuel": "GEORGE",
            "prenom_1": "ARMANTINE",
            "prenom_2": "AURORE",
            "prenom_3": "LUCILE",
            "prenom_4": None,
            "nom_usage": "SAND",
            "nom_naissance": "DUPIN",
            "sexe": "F",
        },
        "diffusable_commercialement": False,
        "status_diffusion": "partiellement_diffusible",
        "forme_juridique": {"code": "1000", "libelle": "Entrepreneur individuel"},
        "activite_principale": {
            "code": "90.03B",
            "nomenclature": "NAFRev2",
            "libelle": "Autre cr\u00e9ation artistique",
        },
        "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
        "etat_administratif": "A",
        "economie_sociale_et_solidaire": None,
        "date_cessation": None,
        "date_creation": 1617228000,
    },
    "links": {
        "siege_social": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/98765432100016",
        "siege_social_adresse": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/98765432100016/adresse",
    },
    "meta": {"date_derniere_mise_a_jour": 1618178400, "redirect_from_siren": None},
}


RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA = {
    "data": {
        "siret": "98765432100016",
        "siege_social": True,
        "etat_administratif": "A",
        "date_fermeture": None,
        "enseigne": None,
        "activite_principale": {
            "code": "90.03B",
            "nomenclature": "NAFRev2",
            "libelle": "Autre cr\u00e9ation artistique",
        },
        "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
        "diffusable_commercialement": False,
        "status_diffusion": "partiellement_diffusible",
        "date_creation": 1618178400,
        "unite_legale": {
            "siren": "987654321",
            "rna": None,
            "siret_siege_social": "98765432100016",
            "type": "personne_physique",
            "personne_morale_attributs": {"raison_sociale": None, "sigle": None},
            "personne_physique_attributs": {
                "pseudonyme": None,
                "prenom_usuel": "GEORGE",
                "prenom_1": "ARMANTINE",
                "prenom_2": "AURORE",
                "prenom_3": "LUCILE",
                "prenom_4": None,
                "nom_usage": "SAND",
                "nom_naissance": "DUPIN",
                "sexe": "F",
            },
            "categorie_entreprise": "PME",
            "status_diffusion": "partiellement_diffusible",
            "diffusable_commercialement": False,
            "forme_juridique": {"code": "1000", "libelle": "Entrepreneur individuel"},
            "activite_principale": {
                "code": "90.03B",
                "nomenclature": "NAFRev2",
                "libelle": "Autre cr\u00e9ation artistique",
            },
            "tranche_effectif_salarie": {"de": None, "a": None, "code": None, "date_reference": None, "intitule": None},
            "economie_sociale_et_solidaire": None,
            "date_creation": 1618178400,
            "etat_administratif": "A",
        },
        "adresse": {
            "status_diffusion": "partiellement_diffusible",
            "complement_adresse": None,
            "numero_voie": "31",
            "indice_repetition_voie": None,
            "type_voie": "RUE",
            "libelle_voie": "DE SEINE",
            "code_postal": "75006",
            "libelle_commune": "PARIS 6",
            "libelle_commune_etranger": None,
            "distribution_speciale": None,
            "code_commune": "75106",
            "code_cedex": None,
            "libelle_cedex": None,
            "code_pays_etranger": None,
            "libelle_pays_etranger": None,
            "acheminement_postal": {
                "l1": "",
                "l2": "GEORGE SAND",
                "l3": "",
                "l4": "31 RUE DE SEINE",
                "l5": "",
                "l6": "75006 PARIS 6",
                "l7": "FRANCE",
            },
        },
    },
    "links": {"unite_legale": "https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/898116934"},
    "meta": {"date_derniere_mise_a_jour": 1618178400, "redirect_from_siret": None},
}


RESPONSE_SIREN_INACTIVE_COMPANY = {
    "data": {
        "siren": "777899888",
        "rna": None,
        "siret_siege_social": "77789988800021",
        "categorie_entreprise": None,
        "type": "personne_morale",
        "personne_morale_attributs": {"raison_sociale": "LE RIDEAU FERME", "sigle": None},
        "personne_physique_attributs": {
            "pseudonyme": None,
            "prenom_usuel": None,
            "prenom_1": None,
            "prenom_2": None,
            "prenom_3": None,
            "prenom_4": None,
            "nom_usage": None,
            "nom_naissance": None,
            "sexe": None,
        },
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "forme_juridique": {
            "code": "5499",
            "libelle": "Soci\u00e9t\u00e9 \u00e0 responsabilit\u00e9 limit\u00e9e (sans autre indication)",
        },
        "activite_principale": {"code": "90.01Z", "nomenclature": "NAFRev2", "libelle": "Arts du spectacle vivant"},
        "tranche_effectif_salarie": {
            "de": None,
            "a": None,
            "code": "NN",
            "date_reference": None,
            "intitule": "Unit\u00e9s non employeuses",
        },
        "etat_administratif": "C",
        "economie_sociale_et_solidaire": None,
        "date_cessation": 1703977200,
        "date_creation": 1262300400,
    },
    "links": {
        "siege_social": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/77789988800021",
        "siege_social_adresse": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/77789988800021/adresse",
    },
    "meta": {"date_derniere_mise_a_jour": 1618178400, "redirect_from_siren": None},
}

RESPONSE_SIRET_INACTIVE_COMPANY = {
    "data": {
        "siret": "77789988800021",
        "siege_social": True,
        "etat_administratif": "F",
        "date_fermeture": 1703977200,
        "enseigne": None,
        "activite_principale": {"code": "90.01Z", "nomenclature": "NAFRev2", "libelle": "Arts du spectacle vivant"},
        "tranche_effectif_salarie": {
            "de": None,
            "a": None,
            "code": "NN",
            "date_reference": None,
            "intitule": "Unit\u00e9s non employeuses",
        },
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "date_creation": 1262300400,
        "unite_legale": {
            "siren": "777899888",
            "rna": None,
            "siret_siege_social": "77789988800021",
            "type": "personne_morale",
            "personne_morale_attributs": {"raison_sociale": "LE RIDEAU FERME", "sigle": None},
            "personne_physique_attributs": {
                "pseudonyme": None,
                "prenom_usuel": None,
                "prenom_1": None,
                "prenom_2": None,
                "prenom_3": None,
                "prenom_4": None,
                "nom_usage": None,
                "nom_naissance": None,
                "sexe": None,
            },
            "categorie_entreprise": None,
            "status_diffusion": "diffusible",
            "diffusable_commercialement": True,
            "forme_juridique": {
                "code": "5499",
                "libelle": "Soci\u00e9t\u00e9 \u00e0 responsabilit\u00e9 limit\u00e9e (sans autre indication)",
            },
            "activite_principale": {"code": "90.01Z", "nomenclature": "NAFRev2", "libelle": "Arts du spectacle vivant"},
            "tranche_effectif_salarie": {
                "de": None,
                "a": None,
                "code": "NN",
                "date_reference": None,
                "intitule": "Unit\u00e9s non employeuses",
            },
            "economie_sociale_et_solidaire": None,
            "date_creation": 1262300400,
            "etat_administratif": "C",
        },
        "adresse": {
            "status_diffusion": "diffusible",
            "complement_adresse": "OCCI",
            "numero_voie": None,
            "indice_repetition_voie": None,
            "type_voie": None,
            "libelle_voie": None,
            "code_postal": "20260",
            "libelle_commune": "LUMIO",
            "libelle_commune_etranger": None,
            "distribution_speciale": None,
            "code_commune": "2B150",
            "code_cedex": None,
            "libelle_cedex": None,
            "code_pays_etranger": None,
            "libelle_pays_etranger": None,
            "acheminement_postal": {
                "l1": "LE RIDEAU FERME",
                "l2": "OCCI",
                "l3": "",
                "l4": "",
                "l5": "",
                "l6": "20260 LUMIO",
                "l7": "FRANCE",
            },
        },
    },
    "links": {"unite_legale": "https://entreprise.api.gouv.fr/v3/insee/sirene/unites_legales/777899888"},
    "meta": {"date_derniere_mise_a_jour": 1618178400, "redirect_from_siret": None},
}

RESPONSE_SIREN_WITHOUT_APE = {
    "data": {
        "siren": "194700936",
        "rna": None,
        "siret_siege_social": "19470093600017",
        "categorie_entreprise": None,
        "type": "personne_morale",
        "personne_morale_attributs": {
            "raison_sociale": "LYCEE D'ENSEIGNEMENT PROFESSIONNEL",
            "sigle": "LPO LYC METIER",
        },
        "personne_physique_attributs": {
            "pseudonyme": None,
            "prenom_usuel": None,
            "prenom_1": None,
            "prenom_2": None,
            "prenom_3": None,
            "prenom_4": None,
            "nom_usage": None,
            "nom_naissance": None,
            "sexe": None,
        },
        "diffusable_commercialement": True,
        "status_diffusion": "diffusible",
        "forme_juridique": {"code": "7331", "libelle": "\u00c9tablissement public local d'enseignement"},
        "activite_principale": {
            "code": None,
            "nomenclature": None,
            "libelle": "ancienne r\u00e9vision NAF () non support\u00e9e",
        },
        "tranche_effectif_salarie": {
            "de": None,
            "a": None,
            "code": "NN",
            "date_reference": None,
            "intitule": "Unit\u00e9s non employeuses",
        },
        "etat_administratif": "C",
        "economie_sociale_et_solidaire": None,
        "date_cessation": 415321200,
        "date_creation": -132022800,
    },
    "links": {
        "siege_social": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/19470093600017",
        "siege_social_adresse": "https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/19470093600017/adresse",
    },
    "meta": {"date_derniere_mise_a_jour": 1678921200, "redirect_from_siren": None},
}


RESPONSE_SIREN_ERROR_422 = {
    "errors": [
        {
            "code": "00301",
            "title": "Entit\u00e9 non traitable",
            "detail": "Le num\u00e9ro de siren n'est pas correctement formatt\u00e9",
            "source": {"parameter": "siren"},
            "meta": {},
        }
    ]
}


RESPONSE_SIREN_ERROR_429 = {"errors": ["Vous avez effectué trop de requêtes"]}

RESPONSE_RCS_REGISTERED_COMPANY = {
    "data": {
        "siren": "123456789",
        "date_extrait": "15 JANVIER 2024",
        "date_radiation": None,
        "date_immatriculation": "2024-01-01",
        "mandataires_sociaux": [
            {
                "type": "personne_physique",
                "nom": "EXEMPLE",
                "prenom": "PIERRE",
                "fonction": "PRESIDENT",
                "date_naissance": "1980-01",
            },
            {
                "type": "personne_physique",
                "nom": "JUSTE LEBLANC",
                "prenom": None,  # sometimes, data is not registered properly
                "fonction": None,
                "date_naissance": "1980-01",
            },
            {
                "type": "personne_physique",
                "raison_sociale": "AUDIT EXEMPLE - SOCIETE PAR ACTIONS SIMPLIFIEE",
                "fonction": "COMMISSAIRE AUX COMPTES TITULAIRE",
                "numero_identification": "123456789",
            },
        ],
        "observations": [],
        "nom_commercial": "",
        "etablissement_principal": {
            "activite": "TESTER L'INTEGRATION D'API ENTREPRISE",
            "origine_fonds": "CREATION",
            "mode_exploitation": "EXPLOITATION DIRECTE",
            "code_ape": "4761Z",
        },
        "capital": {"montant": 1000.0, "devise": "", "code_devise": ""},
        "greffe": {"valeur": "NEVERS", "code": "5801"},
        "personne_morale": {
            "forme_juridique": {"valeur": "SOCIETE PAR ACTIONS SIMPLIFIEE", "code": "SASh"},
            "denomination": "LE PETIT RINTINTIN",
            "date_cloture_exercice_comptable": "12-31",
            "date_fin_de_vie": "2123-12-31",
        },
        "personne_physique": {
            "adresse": {
                "nom_postal": "",
                "numero": "",
                "type": "",
                "voie": "",
                "ligne_1": "",
                "ligne_2": "",
                "localite": "",
                "code_postal": "",
                "bureau_distributeur": "",
                "pays": "",
            },
            "nationalite": {"valeur": "", "code": ""},
            "nom": "",
            "prenom": "",
            "naissance": {"pays": {"valeur": "", "code": ""}, "date": "", "lieu": ""},
        },
    },
    "links": {},
    "meta": {},
}

RESPONSE_RCS_DEREGISTERED_COMPANY = {
    "data": {
        "siren": "123456789",
        "date_extrait": "15 FEVRIER 2024",
        "date_radiation": "2024-02-05",
        "date_immatriculation": "2024-01-01",
        "mandataires_sociaux": [
            {
                "type": "personne_physique",
                "nom": "EXEMPLE",
                "prenom": "PIERRE",
                "fonction": "PRESIDENT",
                "date_naissance": "1980-01",
            },
        ],
        "observations": [
            {"numero": "1234", "libelle": "PREMIERE OBSERVATION", "date": "2024-01-15"},
            {"numero": "5678", "libelle": "DEUXIEME OBSERVATION", "date": "2024-02-03"},
        ],
        "nom_commercial": "",
        "etablissement_principal": {
            "activite": "TESTER L'INTEGRATION D'API ENTREPRISE",
            "origine_fonds": "CREATION",
            "mode_exploitation": "EXPLOITATION DIRECTE",
            "code_ape": "4761Z",
        },
        "capital": {"montant": 1000.0, "devise": "", "code_devise": ""},
        "greffe": {"valeur": "NEVERS", "code": "5801"},
        "personne_morale": {
            "forme_juridique": {"valeur": "SOCIETE PAR ACTIONS SIMPLIFIEE", "code": "SASh"},
            "denomination": "LE PETIT RINTINTIN",
            "date_cloture_exercice_comptable": "12-31",
            "date_fin_de_vie": "2123-12-31",
        },
        "personne_physique": {
            "adresse": {
                "nom_postal": "",
                "numero": "",
                "type": "",
                "voie": "",
                "ligne_1": "",
                "ligne_2": "",
                "localite": "",
                "code_postal": "",
                "bureau_distributeur": "",
                "pays": "",
            },
            "nationalite": {"valeur": "", "code": ""},
            "nom": "",
            "prenom": "",
            "naissance": {"pays": {"valeur": "", "code": ""}, "date": "", "lieu": ""},
        },
    },
    "links": {},
    "meta": {},
}

RESPONSE_RCS_NOT_REGISTERED_404 = {
    "errors": [
        {
            "code": "02003",
            "title": "Entit\u00e9 non trouv\u00e9e",
            "detail": "Le siren indiqu\u00e9 n'existe pas, n'est pas connu ou ne comporte aucune information pour cet appel.",
            "meta": {
                "provider": "Infogreffe",
                "provider_error": {"code": "006", "message": "DOSSIER NON TROUVE DANS LA BASE DE GREFFES"},
            },
        }
    ]
}


RESPONSE_URSSAF_OK = {
    "data": {
        "document_url": "https://storage.entreprise.api.gouv.fr/siade/0000000000-0000000000000000000000000000000000000000-attestation-vigilance-urssaf.pdf",
        "document_url_expires_in": 86400,
        "date_debut_validite": "2023-11-30",
        "date_fin_validite": "2024-05-31",
        "code_securite": "ABCD1234EFGH567",
        "entity_status": {
            "code": "ok",
            "libelle": "Attestation d\u00e9livr\u00e9e par l'Urssaf",
            "description": "La d\u00e9livrance de l'attestation de vigilance a \u00e9t\u00e9 valid\u00e9e par l'Urssaf. L'attestation est d\u00e9livr\u00e9e lorsque l'entit\u00e9 est \u00e0 jour de ses cotisations et contributions, ou bien dans le cas de situations sp\u00e9cifiques d\u00e9taill\u00e9es dans la documentation m\u00e9tier.",
        },
    },
    "links": {},
    "meta": {},
}

RESPONSE_URSSAF_REFUSED = {
    "data": {
        "document_url": None,
        "document_url_expires_in": None,
        "date_debut_validite": None,
        "date_fin_validite": None,
        "code_securite": None,
        "entity_status": {
            "code": "refus_de_delivrance",
            "libelle": "D\u00e9livrance de l'attestation refus\u00e9e par l'Urssaf",
            "description": "La d\u00e9livrance de l'attestation de vigilance a \u00e9t\u00e9 refus\u00e9e par l'Urssaf car l'entit\u00e9 n'est pas \u00e0 jour de ses cotisations sociales.",
        },
    },
    "links": {},
    "meta": {},
}

RESPONSE_URSSAF_ERROR_404 = {
    "errors": [
        {
            "code": "04003",
            "title": "Entit\u00e9 non trouv\u00e9e",
            "detail": "Le siret ou siren indiqu\u00e9 n'existe pas, n'est pas connu ou ne comporte aucune information pour cet appel",
            "meta": {
                "provider": "ACOSS",
                "provider_errors": [
                    {
                        "code": "FUNC517",
                        "message": "Le Siren est inconnu",
                        "description": "Le siren est inconnu du SI Attestations, radi\u00e9 ou hors p\u00e9rim\u00e8tre",
                    }
                ],
            },
        }
    ]
}

RESPONSE_DGFIP_OK = {
    "data": {
        "document_url": "https://storage.entreprise.api.gouv.fr/siade/0000000000-0000000000000000000000000000000000000000-attestation_fiscale_dgfip.pdf",
        "document_url_expires_in": 86400,
        "date_delivrance_attestation": "2024-01-16",
        "date_periode_analysee": "2023-12-31",
    },
    "links": {},
    "meta": {},
}

RESPONSE_DGFIP_ENTREPRISE_INDIVIDUELLE_502 = {
    "errors": [
        {
            "code": "03999",
            "title": "Erreur inconnue du fournisseur de donn\u00e9es",
            "detail": "La r\u00e9ponse retourn\u00e9e par le fournisseur de donn\u00e9es est invalide et inconnue de notre service. L'\u00e9quipe technique a \u00e9t\u00e9 notifi\u00e9e de cette erreur pour investigation.",
            "meta": {"provider": "DGFIP - Ad\u00e9lie"},
        }
    ]
}

RESPONSE_DGFIP_INACTIVE_COMPANY_404 = {
    "errors": [
        {
            "code": "03003",
            "title": "Entit\u00e9 non trouv\u00e9e",
            "detail": "L'identifiant indiqu\u00e9 n'existe pas, n'est pas connu ou ne comporte aucune information pour cet appel.",
            "meta": {"provider": "DGFIP - Ad\u00e9lie"},
        }
    ]
}
