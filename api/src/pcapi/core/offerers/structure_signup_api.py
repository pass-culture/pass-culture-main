import enum

import pcapi.core.offerers.models as offerers_models


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


class EligibilityDocuments(enum.Enum):
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


def create_signup_documents_list(
    apeCode: str,
    legal_category_code: str,
    isOpenToPublic: bool,
    targets: list[offerers_models.OffererTarget],
    activity: offerers_models.Activity,
) -> dict[str, list]:
    """Determine les documents necessaires a l homologation ainsi que les warnings a afficher en fonction du code ape, de la categorie jusridique et de l activite d'un siret"""
    # Everyone has to provide a website
    eligibility_documents = [EligibilityDocuments.WEBSITE]
    messages = []
    # if target is educationnal/school/collective offers, display warning for adage inscription
    if offerers_models.OffererTarget.COLLECTIVE in targets:
        messages.append(
            {
                "importance_level": ImportanceLevelMessageSignupSimulation.INFO,
                "content": ContentMessageSignupSimulation.COLLECTIVE,
            }
        )
    # Commune ou collectivité territoriale (Administration publique générale) OR Enseignement supérieur OR Etablissement Public National
    if apeCode == "8411Z" or apeCode == "8542Z" or legal_category_code.startswith("73"):
        return {"documents": eligibility_documents, "messages": messages}

    # from here, all structures need to provide an offer description
    eligibility_documents.append(EligibilityDocuments.DESCRIPTION)
    # from here, display warning if ape code is unusual
    if not apeCode.startswith(APE_CODE_WHITELIST):
        messages.append(
            {
                "importance_level": ImportanceLevelMessageSignupSimulation.ALERT,
                "content": ContentMessageSignupSimulation.UNUSUAL_APE_CODE,
            }
        )

    # studio d'enregistrement
    if apeCode == "5920Z":
        eligibility_documents += [
            EligibilityDocuments.RESUME_OR_PORTFOLIO,
            EligibilityDocuments.PRICES,
            EligibilityDocuments.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocuments.SOUND_STUDIO_PICTURES,
        ]
        # studio d'enregistrement en entreprise uninomiale
        if legal_category_code.startswith("1"):
            eligibility_documents.append(EligibilityDocuments.CRIMINAL_RECORDS)
        return {"documents": eligibility_documents, "messages": messages}

    # entreprise "uninomiale"
    if legal_category_code.startswith("1"):
        eligibility_documents += [EligibilityDocuments.RESUME_OR_PORTFOLIO, EligibilityDocuments.DIPLOMAS]
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
                EligibilityDocuments.CRIMINAL_RECORDS,
            ]

    # point de vente de livres
    if apeCode.startswith("581") or activity.value in (
        offerers_models.Activity.BOOKSTORE.value,
        offerers_models.Activity.PUBLISHING_HOUSE.value,
    ):
        eligibility_documents.append(EligibilityDocuments.SHOP_PICTURES)
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
