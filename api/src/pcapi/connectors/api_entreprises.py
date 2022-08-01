import logging
import typing

from pcapi.connectors.utils.legal_category_code_to_labels import CODE_TO_CATEGORY_MAPPING
from pcapi.models.feature import FeatureToggle
from pcapi.utils import requests


if typing.TYPE_CHECKING:
    from pcapi.core.offerers.models import Offerer

logger = logging.getLogger(__name__)


class ApiEntrepriseException(Exception):
    pass


def get_by_offerer(offerer: "Offerer") -> dict:
    if FeatureToggle.DISABLE_ENTERPRISE_API.is_active():
        raise ApiEntrepriseException("DISABLE_ENTERPRISE_API activated")

    try:
        response = requests.get(f"https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/{offerer.siren}")
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get data from entreprise.data.gouv.fr", extra={"siren": offerer.siren})
        raise ApiEntrepriseException("Error getting API entreprise DATA for SIREN : {}".format(offerer.siren)) from exc

    if response.status_code != 200:
        raise ApiEntrepriseException("Error getting API entreprise DATA for SIREN : {}".format(offerer.siren))

    response_json = response.json()
    response_json["unite_legale"].pop("etablissements")
    return response_json


def get_by_siret(siret: str) -> dict:
    if FeatureToggle.DISABLE_ENTERPRISE_API.is_active():
        raise ApiEntrepriseException("DISABLE_ENTERPRISE_API activated")

    try:
        response = requests.get(f"https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/{siret}")
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.Timeout) as exc:
        logger.exception("Failed to get data from entreprise.data.gouv.fr", extra={"siret": siret})
        raise ApiEntrepriseException("Error getting API entreprise DATA for SIRET : {}".format(siret)) from exc

    if response.status_code != 200:
        raise ApiEntrepriseException(f"Error getting API entreprise DATA for SIRET : {siret}")

    return response.json()["etablissement"]


def get_offerer_legal_category(offerer: "Offerer") -> dict:
    try:
        legal_category_code = get_by_offerer(offerer)["unite_legale"]["categorie_juridique"]
        legal_category_label = CODE_TO_CATEGORY_MAPPING.get(int(legal_category_code)) if legal_category_code else None
    except ApiEntrepriseException as exc:
        legal_category_code = "Donnée indisponible"
        legal_category_label = "Donnée indisponible"
        logging.warning(
            "Could not reach API Entreprise",
            extra={"ApiEntrepriseException": exc, "offerer_id": offerer.id},
        )

    return {"legal_category_code": legal_category_code, "legal_category_label": legal_category_label}


def check_siret_is_still_active(siret: str) -> bool:
    venue_data = get_by_siret(siret)
    # See https://www.sirene.fr/sirene/public/variable/etatAdministratifEtablissement for the field
    return venue_data.get("etat_administratif", "F") == "A"
