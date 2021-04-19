from pcapi.connectors.utils.legal_category_code_to_labels import CODE_TO_CATEGORY_MAPPING
from pcapi.core.offerers.models import Offerer
from pcapi.utils import requests


class ApiEntrepriseException(Exception):
    pass


def get_by_offerer(offerer: Offerer) -> dict:
    response = requests.get(
        f"https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/{offerer.siren}", verify=False
    )

    if response.status_code != 200:
        raise ApiEntrepriseException("Error getting API entreprise DATA for SIREN : {}".format(offerer.siren))

    response_json = response.json()
    etablissements = response_json["unite_legale"].pop("etablissements")
    response_json["other_etablissements_sirets"] = []
    response_json["other_etablissements_sirets"] = _extract_etablissements_communs_siren(etablissements)
    return response_json


def _extract_etablissements_communs_siren(etablissements: list[dict]) -> list[dict]:
    etablissements_communs = [
        etablissement for etablissement in etablissements if etablissement["etablissement_siege"] == "false"
    ]
    return [etablissement["siret"] for etablissement in etablissements_communs]


def get_offerer_legal_category(offerer: Offerer) -> dict:
    legal_category = get_by_offerer(offerer)["unite_legale"]["categorie_juridique"]
    legal_category_label = CODE_TO_CATEGORY_MAPPING.get(int(legal_category)) if legal_category else None

    return {"legal_category_code": legal_category, "legal_category_label": legal_category_label}
