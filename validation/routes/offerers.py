from models import ApiErrors


def check_valid_edition(data):
    invalid_fields_for_patch = set(data.keys()).difference({'iban', 'bic', 'isActive'})
    if invalid_fields_for_patch:
        api_errors = ApiErrors()
        for key in invalid_fields_for_patch:
            api_errors.add_error(key, 'Vous ne pouvez pas modifier ce champ')
        raise api_errors
