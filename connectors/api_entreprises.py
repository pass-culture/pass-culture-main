import requests


def get_by_siren(entity):
    return requests.get("https://sirene.entreprise.api.gouv.fr/v1/siren/" + entity.siren, verify=False)  # FIXME: add root cerficate on docker image ?
