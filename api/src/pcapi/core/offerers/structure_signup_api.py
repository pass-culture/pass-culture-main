import enum

import pcapi.core.offerers.models as offerers_models


# structures with an APE not in this list will have an additional warning
APE_CODE_WHITELIST = (
    "18",
    "23",
    "26",
    "43",
    "47",
    "58",
    "59",
    "60",
    "74",
    "82",
    "84",
    "85",
    "90",
    "91",
    "93",
    "94",
)


class EligibilityDocument(enum.Enum):
    WEBSITE = "WEBSITE"
    RESUME_OR_PORTFOLIO = "RESUME_OR_PORTFOLIO"
    DIPLOMAS = "DIPLOMAS"
    SOUND_DESIGN_DIPLOMAS = "SOUND_DESIGN_DIPLOMAS"
    PRICES = "PRICES"
    SHOP_PICTURES = "SHOP_PICTURES"
    SOUND_STUDIO_PICTURES = "SOUND_STUDIO_PICTURES"
    CRIMINAL_RECORDS = "CRIMINAL_RECORDS"
    DESCRIPTION = "DESCRIPTION"


class ImportanceLevelMessageSignupSimulation(enum.Enum):
    INFO = "INFO"
    ALERT = "ALERT"


class ContentMessageSignupSimulation(enum.Enum):
    COLLECTIVE = "COLLECTIVE"
    BOOKSTORE = "BOOKSTORE"
    UNUSUAL_APE_CODE = "UNUSUAL_APE_CODE"


def get_signup_documents(
    ape_code: str,
    legal_category_code: str,
    targets: list[offerers_models.OffererTarget],
    activity: offerers_models.Activity,
) -> dict[str, list]:
    """Determine les documents necessaires a l homologation ainsi que les warnings a afficher en fonction du code ape, de la categorie jusridique et de l activite d'un siret"""

    # everyone must provide a website
    eligibility_documents = [EligibilityDocument.WEBSITE]
    messages = []

    # if target is collective, display warning for adage inscription
    if offerers_models.OffererTarget.COLLECTIVE in targets:
        messages.append(
            {
                "importance_level": ImportanceLevelMessageSignupSimulation.INFO,
                "content": ContentMessageSignupSimulation.COLLECTIVE,
            }
        )
    # Commune ou collectivité territoriale (Administration publique générale) OR Enseignement supérieur OR Etablissement Public National
    if ape_code == "8411Z" or ape_code == "8542Z" or legal_category_code.startswith("73"):
        return {"documents": eligibility_documents, "messages": messages}

    # from here, all structures need to provide an offer description
    eligibility_documents.append(EligibilityDocument.DESCRIPTION)

    # from here, display warning if ape code is unusual
    if not ape_code.startswith(APE_CODE_WHITELIST):
        messages.append(
            {
                "importance_level": ImportanceLevelMessageSignupSimulation.ALERT,
                "content": ContentMessageSignupSimulation.UNUSUAL_APE_CODE,
            }
        )

    # studio d'enregistrement
    if ape_code == "5920Z":
        eligibility_documents += [
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
        ]
        # studio d'enregistrement en entreprise uninomiale
        if legal_category_code.startswith("1"):
            eligibility_documents.append(EligibilityDocument.CRIMINAL_RECORDS)
        return {"documents": eligibility_documents, "messages": messages}

    # entreprise "uninomiale"
    if legal_category_code.startswith("1"):
        eligibility_documents += [EligibilityDocument.RESUME_OR_PORTFOLIO, EligibilityDocument.DIPLOMAS]
        # Entreprise uninomiale en contact avec des mineurs
        if activity in [
            offerers_models.Activity.ARTISTIC_PRACTICE,
            offerers_models.Activity.CULTURAL_CENTRE,
            offerers_models.Activity.CULTURAL_MEDIATION,
            offerers_models.Activity.HERITAGE_SITE,
            offerers_models.Activity.RADIO_OR_MUSIC_STREAMING,
            offerers_models.Activity.SCIENTIFIC_CULTURE,
            offerers_models.Activity.TOURIST_INFORMATION_CENTRE,
            offerers_models.Activity.OTHER,
        ]:
            eligibility_documents += [
                EligibilityDocument.CRIMINAL_RECORDS,
            ]

    # point de vente de livres
    if ape_code.startswith("581") or activity.value in (
        offerers_models.Activity.BOOKSTORE.value,
        offerers_models.Activity.PUBLISHING_HOUSE.value,
    ):
        eligibility_documents.append(EligibilityDocument.SHOP_PICTURES)
        messages.append(
            {
                "importance_level": ImportanceLevelMessageSignupSimulation.ALERT,
                "content": ContentMessageSignupSimulation.BOOKSTORE,
            }
        )
        return {"documents": eligibility_documents, "messages": messages}

    # standard case
    return {
        "documents": eligibility_documents,
        "messages": messages,
    }
