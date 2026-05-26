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


# TODO question lucie: renvoyer des sets plutot que des listes? osef de l ordre + evite doublons donc remise de uninomial chelou avant sound studio


class EligibilityDocuments(enum.Enum):  # EligibilityProofs?
    WEBSITE = "Site internet ou support de communication en ligne"  # TODO c'est un champ # Site internet ou autre support de communication en ligne (ou détail des offres proposées)
    RESUME_OR_PORTFOLIO = "CV ou portfolio"  # CV ou portfolio ou liste d’expériences professionnelles
    DIPLOMAS = "Diplômes"
    SOUND_DESIGN_DIPLOMAS = "Diplôme ou attestation dans les métiers du son"  # Diplôme d’ingénieur du son ou attestation de formation dans les métiers du son
    PRICES = "Grille tarifaire"  # Grille tarifaire détaillée
    SHOP_PICTURES = "Photos du point de vente"  # Photos du point de vente montrant la devanture et les rayonnages
    SOUND_STUDIO_PICTURES = "Photos et vidéos des locaux et du matériel"  # Photos et vidéos montrant la qualité des locaux et du matériel à disposition
    CRIMINAL_RECORDS = "Extrait de casier judiciaire B3"  # Extrait de casier judiciaire (bulletin n°3)
    DESCRIPTION = "Description détaillée de vos offres"


class ImportanceLevelMessageSignupSimulation(enum.Enum):
    INFO = "INFO"
    ALERT = "ALERT"


# TODO voir si nec d avoir l enum ou si on leur envoi que des strings
class ContentMessageSignupSimulation(enum.Enum):
    COLLECTIVE = "En plus de ces éléments, il vous sera demandé lors de votre dépôt de dossier ADAGE :\nUn descriptif de votre projet professionnel artistique et culturel\nVos motivations à proposer des offres aux groupes scolaires"
    BOOKSTORE = "Vous devez obligatoirement disposer d'un point de vente physique pour proposer des offres de vente de livres sur le pass Culture."
    UNUSUAL_APE_CODE = "Attention, seules certaines activités fixées par arrêté sont éligibles au pass Culture"


def signup_simulation(
    apeCode: str,
    legal_category_code: str,
    isOpenToPublic: bool,
    targets: list[str],
    activity: offerers_models.Activity,
) -> dict[str, list]:
    """Determine les documents necessaires a l homologation ainsi que les warnings a afficher en donction du code ape, de la categorie jusridique et de l activite d'un siret"""
    # Everyone has to provide a website
    eligibility_documents = [EligibilityDocuments.WEBSITE]
    messages = []
    # if target is educationnal/school/collective offers, display warning for adage inscription
    if (
        offerers_models.Target.EDUCATIONAL.value in targets
        or offerers_models.Target.INDIVIDUAL_AND_EDUCATIONAL.value in targets
    ):
        messages.append(
            {
                "importance_level": ImportanceLevelMessageSignupSimulation.ALERT,
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

    # recording studio
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

    # entreprise "uninomiale" AKA one-person company
    if legal_category_code.startswith("1"):
        eligibility_documents += [EligibilityDocuments.RESUME_OR_PORTFOLIO, EligibilityDocuments.DIPLOMAS]
        # Entreprise uninomiale with contacts with minors
        if activity in [
            offerers_models.Activity.ART_SCHOOL,
            offerers_models.Activity.ARTISTIC_PRACTICE,
            offerers_models.Activity.CULTURAL_MEDIATION,
            offerers_models.Activity.HERITAGE_SITE,
            offerers_models.Activity.RADIO_OR_MUSIC_STREAMING,
            offerers_models.Activity.SCIENCE_CENTRE,
            offerers_models.Activity.TOURIST_INFORMATION_CENTRE,
            offerers_models.Activity.OTHER,
        ]:
            eligibility_documents += [
                EligibilityDocuments.CRIMINAL_RECORDS,
            ]

    # bookseller
    if apeCode.startswith("581") or activity in (
        offerers_models.Activity.BOOKSTORE,
        offerers_models.Activity.PUBLISHING_HOUSE,
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
