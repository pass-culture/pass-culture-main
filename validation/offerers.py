from models import ApiErrors


def check_valid_edition(data):
    invalid_fields_for_patch = set(data.keys()).difference({'iban', 'bic', 'isActive'})
    if invalid_fields_for_patch:
        api_errors = ApiErrors()
        for key in invalid_fields_for_patch:
            api_errors.add_error(key, 'Vous ne pouvez pas modifier ce champ')
        raise api_errors


def parse_boolean_param_validated(request):
    validated = request.args.get('validated')
    only_validated_offerers = True

    if validated:
        if validated.lower() in ('true', 'false'):
            only_validated_offerers = validated.lower() == 'true'
        else:
            errors = ApiErrors()
            errors.add_error('validated', 'Le paramètre \'validated\' doit être \'true\' ou \'false\'')
            raise errors

    return only_validated_offerers
