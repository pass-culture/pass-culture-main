import requests
from requests import Response

from models import Offerer


class ApiEntrepriseException(Exception):
    pass


def get_by_offerer(offerer: Offerer) -> Response:
    return get_by_siren(offerer.siren)


def get_by_siren(siren: str) -> Response:
    response = requests.get("https://entreprise.data.gouv.fr/api/sirene/v1/siren/" + siren,
                            verify=False)

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(siren))

    return response


def get_by_siret(siret: str) -> Response:
    response = requests.get("https://entreprise.data.gouv.fr/api/sirene/v1/siret/" + siret,
                            verify=False)

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIRET : {}'.format(siret))

    return response
