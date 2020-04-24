import requests

from models import Offerer


class ApiEntrepriseException(Exception):
    pass


def get_by_offerer(offerer: Offerer) -> dict:
    return _get_by_siren(offerer.siren)


def _get_by_siren(siren: str) -> dict:
    response = requests.get("https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/" + siren,
                            verify=False)

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(siren))

    response_json = response.json()
    etablissements = response_json["unite_legale"].pop("etablissements")

    response_json["other_etablissements_sirets"] = []

    for etablissement in etablissements:
        __not_etablissement_siege = etablissement["etablissement_siege"] == "false"
        if __not_etablissement_siege:
            response_json["other_etablissements_sirets"].append(etablissement["siret"])

    return response_json
