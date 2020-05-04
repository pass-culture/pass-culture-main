from typing import Dict

import requests

from models import Offerer


class ApiEntrepriseException(Exception):
    pass


def get_by_offerer(offerer: Offerer) -> Dict:
    return _get_by_siren(offerer.siren)


def _get_by_siren(siren: str) -> Dict:
    response = requests.get(f'https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/{siren}',
                            verify=False)

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(siren))

    response_json = response.json()
    etablissements = response_json["unite_legale"].pop("etablissements")

    response_json["other_etablissements_sirets"] = []

    response_json["other_etablissements_sirets"] = _extract_etablissements_communs_siren(etablissements)

    return response_json


def _extract_etablissements_communs_siren(etablissements):
    etablissements_communs = [etablissement for etablissement in etablissements if etablissement["etablissement_siege"] == "false"]
    return [etablissement["siret"] for etablissement in etablissements_communs]
