import enum
import typing
from dataclasses import dataclass

from pcapi.core.offerers import models as offerers_models


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

APE_ADMINISTRATION_PUBLIQUE_GENERALE: typing.Final = "8411Z"
APE_ENSEIGNEMENT_SUPERIEUR: typing.Final = "8542Z"
APE_RECORDING_STUDIO: typing.Final = "5920Z"


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


def _is_national_public_institution(legal_category_code: str) -> bool:
    # 73xxx is "Etablissement Public National"
    return legal_category_code.startswith("73")


def _is_single_member_structure(legal_category_code: str) -> bool:
    return legal_category_code.startswith("1")


def _is_bookstore_ape(ape_code: str) -> bool:
    return ape_code.startswith("581")


def get_signup_documents_and_messages(
    ape_code: str,
    legal_category_code: str,
    is_open_to_public: bool,
    targets: list[offerers_models.OffererTarget],
    activity: offerers_models.Activity,
) -> tuple[list[EligibilityDocument], list[SignupSimulationMessage]]:
    """List the necessary documents for homologation and warnings depending on signup inputs and siret data"""

    # all structures must provide a website
    eligibility_documents = [EligibilityDocument.WEBSITE]
    messages = []

    # if "collective" is a target, display a warning for adage inscription
    if offerers_models.OffererTarget.COLLECTIVE in targets:
        messages.append(COLLECTIVE_MESSAGE)

    if (
        ape_code == APE_ADMINISTRATION_PUBLIQUE_GENERALE
        or ape_code == APE_ENSEIGNEMENT_SUPERIEUR
        or _is_national_public_institution(legal_category_code)
    ):
        return eligibility_documents, messages

    # all other structures need to provide an offer description
    eligibility_documents.append(EligibilityDocument.DESCRIPTION)

    # display a warning if ape code is unusual
    if not ape_code.startswith(APE_CODE_WHITELIST):
        messages.append(UNUSUAL_APE_CODE_MESSAGE)

    if ape_code == APE_RECORDING_STUDIO:
        eligibility_documents += [
            EligibilityDocument.RESUME_OR_PORTFOLIO,
            EligibilityDocument.PRICES,
            EligibilityDocument.SOUND_DESIGN_DIPLOMAS,
            EligibilityDocument.SOUND_STUDIO_PICTURES,
        ]

        # additional document for single member recording studio
        if _is_single_member_structure(legal_category_code):
            eligibility_documents.append(EligibilityDocument.CRIMINAL_RECORDS)

        return eligibility_documents, messages

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

    if _is_bookstore_ape(ape_code) or activity in {
        offerers_models.Activity.BOOKSTORE,
        offerers_models.Activity.PUBLISHING_HOUSE,
    }:
        eligibility_documents.append(EligibilityDocument.SHOP_PICTURES)
        messages.append(BOOKSTORE_MESSAGE)

    return eligibility_documents, messages
