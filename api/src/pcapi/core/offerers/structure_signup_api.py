import enum
import typing
from collections import OrderedDict
from dataclasses import dataclass
from urllib.parse import urlencode

from pcapi import settings
from pcapi.core.offerers import models as offerers_models


# APE is "Activité Principale Exercée"
# structures with an APE not in this list will have an additional warning
APE_CODE_WHITELIST: typing.Final = (
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

APE_CODES_ADMINISTRATION_PUBLIQUE_GENERALE: typing.Final = {"8411Z", "8411Y"}
APE_CODES_ENSEIGNEMENT_SUPERIEUR: typing.Final = {"8542Z", "8540Y"}
APE_CODES_STUDIO_ENREGISTREMENT: typing.Final = {"5920Z", "5920Y"}


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


class SignupSimulationMessageLevel(enum.Enum):
    INFO = "INFO"
    ALERT = "ALERT"


class SignupSimulationMessageType(enum.Enum):
    COLLECTIVE = "COLLECTIVE"
    BOOKSTORE = "BOOKSTORE"
    UNUSUAL_APE_CODE = "UNUSUAL_APE_CODE"


@dataclass
class SignupSimulationMessage:
    level: SignupSimulationMessageLevel
    type: SignupSimulationMessageType


COLLECTIVE_MESSAGE = SignupSimulationMessage(
    level=SignupSimulationMessageLevel.INFO, type=SignupSimulationMessageType.COLLECTIVE
)
UNUSUAL_APE_CODE_MESSAGE = SignupSimulationMessage(
    level=SignupSimulationMessageLevel.ALERT, type=SignupSimulationMessageType.UNUSUAL_APE_CODE
)
BOOKSTORE_MESSAGE = SignupSimulationMessage(
    level=SignupSimulationMessageLevel.ALERT, type=SignupSimulationMessageType.BOOKSTORE
)

MINOR_CONTACT_ACTIVITIES: typing.Final = {
    offerers_models.Activity.ARTISTIC_PRACTICE,
    offerers_models.Activity.CULTURAL_CENTRE,
    offerers_models.Activity.CULTURAL_MEDIATION,
    offerers_models.Activity.HERITAGE_SITE,
    offerers_models.Activity.RADIO_OR_MUSIC_STREAMING,
    offerers_models.Activity.SCIENTIFIC_CULTURE,
    offerers_models.Activity.TOURIST_INFORMATION_CENTRE,
    offerers_models.Activity.OTHER,
}


@dataclass
class SignupSimulationResult:
    documents: list[EligibilityDocument]
    messages: list[SignupSimulationMessage]


def _is_national_public_institution(legal_category_code: str) -> bool:
    return legal_category_code.startswith("73")


def _is_single_member_structure(legal_category_code: str) -> bool:
    return legal_category_code.startswith("1")


def _is_bookstore(ape_code: str, activity: offerers_models.Activity) -> bool:
    return ape_code.startswith("581") or activity in {
        offerers_models.Activity.BOOKSTORE,
        offerers_models.Activity.PUBLISHING_HOUSE,
    }


def get_signup_documents(
    ape_code: str,
    legal_category_code: str,
    is_open_to_public: bool,
    activity: offerers_models.Activity,
) -> list[EligibilityDocument]:
    """List the necessary documents for homologation depending on signup inputs and siret data"""

    # all structures must provide a website
    eligibility_documents = [EligibilityDocument.WEBSITE]

    # public structures do not need any other document
    if (
        ape_code in APE_CODES_ADMINISTRATION_PUBLIQUE_GENERALE
        or ape_code in APE_CODES_ENSEIGNEMENT_SUPERIEUR
        or _is_national_public_institution(legal_category_code)
    ):
        return eligibility_documents

    # all other structures need to provide an offer description
    eligibility_documents.append(EligibilityDocument.DESCRIPTION)

    # recording studio case
    if ape_code in APE_CODES_STUDIO_ENREGISTREMENT:
        eligibility_documents += [
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
        ]

        # additional document for single member recording studio
        if _is_single_member_structure(legal_category_code):
            eligibility_documents.append(EligibilityDocument.CRIMINAL_RECORDS)

        return eligibility_documents

    # single member structure case
    if _is_single_member_structure(legal_category_code):
        eligibility_documents += [EligibilityDocument.RESUME_OR_PORTFOLIO, EligibilityDocument.DIPLOMAS]

        # additional document for single member structures that have contacts with minors
        if activity in {
            offerers_models.Activity.ARTISTIC_PRACTICE,
            offerers_models.Activity.CULTURAL_CENTRE,
            offerers_models.Activity.CULTURAL_MEDIATION,
            offerers_models.Activity.HERITAGE_SITE,
            offerers_models.Activity.RADIO_OR_MUSIC_STREAMING,
            offerers_models.Activity.SCIENTIFIC_CULTURE,
            offerers_models.Activity.TOURIST_INFORMATION_CENTRE,
            offerers_models.Activity.OTHER,
        }:
            eligibility_documents.append(EligibilityDocument.CRIMINAL_RECORDS)

    # bookstore case
    if _is_bookstore(ape_code, activity) and is_open_to_public:
        eligibility_documents.append(EligibilityDocument.SHOP_PICTURES)

    return eligibility_documents


def get_signup_messages(
    ape_code: str,
    targets: list[offerers_models.TargetAudience],
    activity: offerers_models.Activity,
) -> list[SignupSimulationMessage]:
    """List warnings depending on signup inputs and siret data"""
    messages = []

    # warning for adage inscription
    if offerers_models.TargetAudience.COLLECTIVE in targets:
        messages.append(COLLECTIVE_MESSAGE)

    # warning for unusual ape code
    if not ape_code.startswith(APE_CODE_WHITELIST):
        messages.append(UNUSUAL_APE_CODE_MESSAGE)

    # warning for bookstores
    if _is_bookstore(ape_code, activity):
        messages.append(BOOKSTORE_MESSAGE)

    return messages


def build_signup_structure_params(structure_simulation_info: offerers_models.StructureSimulationInfo) -> str:
    # use an OrderedDict to get a deterministic output
    params = OrderedDict(
        {
            "siret": structure_simulation_info.siret,
            "isOpenToPublic": "true" if structure_simulation_info.is_open_to_public else "false",
            "targets": [target.name for target in structure_simulation_info.targets],
            "activity": structure_simulation_info.activity.name,
        }
    )
    return urlencode(params, doseq=True)


def build_signup_link(structure_simulation_info: offerers_models.StructureSimulationInfo) -> str:
    encoded_params = build_signup_structure_params(structure_simulation_info)
    return f"{settings.PRO_URL}/inscription/compte/creation?{encoded_params}"
