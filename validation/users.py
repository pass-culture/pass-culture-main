from models import ApiErrors


def check_allowed_changes_for_user(data):
    changes_allowed = {'email', 'publicName', 'postalCode', 'phoneNumber', 'departementCode'}
    changes_asked = set(data)
    api_errors = ApiErrors()
    changes_not_allowed = changes_asked.difference(changes_allowed)
    if changes_not_allowed:
        for change in changes_not_allowed:
            api_errors.addError(change, 'Vous ne pouvez pas changer cette information')
        raise api_errors