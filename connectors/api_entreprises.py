import requests


class ApiEntrepriseException(Exception):
    pass


def get_by_offerer(offerer):
    response = requests.get("https://sirene.entreprise.api.gouv.fr/v1/siren/" + offerer.siren,
                            verify=False)  # FIXME: add root cerficate on docker image ?

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(offerer.siren))

    return response


def get_by_siren(siren):
    response = requests.get("https://sirene.entreprise.api.gouv.fr/v1/siren/" + siren,
                            verify=False)  # FIXME: add root cerficate on docker image ?

    if response.status_code != 200:
        raise ApiEntrepriseException('Error getting API entreprise DATA for SIREN : {}'.format(siren))

    return response
