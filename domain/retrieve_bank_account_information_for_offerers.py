from typing import Callable


def get_all_file_ids_from_demarches_simplifiees_procedure(procedure_id: str, token: str,
                                                          get_all_files_for_procedure_in_demarches_simplifiees: Callable[[str, str], dict]):
    files = get_all_files_for_procedure_in_demarches_simplifiees(procedure_id, token)
    return [file['id'] for file in files['dossiers'] if file['state'] == 'closed']

