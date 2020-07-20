from models import ApiErrors
from typing import Dict


def validate_save_mailing_contact_request(json: Dict):
    if 'email' not in json or not json['email']:
        errors = ApiErrors()
        errors.add_error('email', 'L\'email est manquant')
        raise errors

    if 'date_of_birth' not in json or not json['date_of_birth']:
        errors = ApiErrors()
        errors.add_error('date_of_birth', 'La date de naissance est manquante')
        raise errors

    if 'department_code' not in json or not json['department_code']:
        errors = ApiErrors()
        errors.add_error('department_code', 'Le code département est manquant')
        raise errors
