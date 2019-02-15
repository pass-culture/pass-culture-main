import requests


class ApiDemarchesSimplifieesException(Exception):
    pass


def get_all_applications_for_procedure(procedure_id, token):
    response = requests.get(
        f"https://www.demarches-simplifiees.fr/api/v1/procedures/{procedure_id}/dossiers?token={token}",
        verify=False)

    if response.status_code != 200:
        raise ApiDemarchesSimplifieesException(
            f'Error getting API démarches simplifiées DATA for procedure_id: {procedure_id} and token {token}')

    return response.json()


def get_application_details(application_id, procedure_id, token):
    response = requests.get(
        f"https://www.demarches-simplifiees.fr/api/v1/procedures/{procedure_id}/dossiers/{application_id}?token={token}",
        verify=False)

    if response.status_code != 200:
        raise ApiDemarchesSimplifieesException(
            f'Error getting API démarches simplifiées DATA for procedure_id: {procedure_id}, application_id: {application_id} and token {token}')

    return response.json()
