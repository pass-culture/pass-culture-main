from domain.password import check_password_strength
from models import ApiErrors
from models.api_errors import ResourceNotFoundError


def check_allowed_changes_for_user(data):
    changes_allowed = {
        'culturalSurveyId',
        'culturalSurveyFilledDate',
        'departementCode',
        'email',
        'needsToFillCulturalSurvey',
        'phoneNumber',
        'postalCode',
        'publicName',
    }
    changes_asked = set(data)
    api_errors = ApiErrors()
    changes_not_allowed = changes_asked.difference(changes_allowed)
    if changes_not_allowed:
        for change in changes_not_allowed:
            api_errors.add_error(change, 'Vous ne pouvez pas changer cette information')
        raise api_errors


def check_valid_signup_pro(request):
    contact_ok = request.json.get('contact_ok')
    password = request.json.get('password')
    email = request.json.get('email')
    phone_number = request.json.get('phoneNumber')

    _check_email_is_present(email)
    _check_valid_contact_ok(contact_ok)
    _check_phone_number_is_present(phone_number)
    _check_password_is_present(password)
    check_password_strength('password', password)


def check_valid_signup_webapp(request):
    contact_ok = request.json.get('contact_ok')
    password = request.json.get('password')
    email = request.json.get('email')

    _check_email_is_present(email)
    _check_valid_contact_ok(contact_ok)
    _check_password_is_present(password)
    check_password_strength('password', password)


def check_valid_signin(identifier: str, password: str):
    errors = ApiErrors()
    errors.status_code = 401

    if identifier is None:
        errors.add_error('identifier', 'Identifiant manquant')
    if password is None:
        errors.add_error('password', 'Mot de passe manquant')

    errors.maybe_raise()


def _check_phone_number_is_present(phone_number):
    if phone_number is None:
        errors = ApiErrors()
        errors.add_error('phoneNumber', 'Vous devez renseigner un numéro de téléphone.')
        raise errors


def _check_password_is_present(password):
    if not password:
        errors = ApiErrors()
        errors.add_error('password', 'Vous devez renseigner un mot de passe.')
        raise errors


def _check_valid_contact_ok(contact_ok):
    if not contact_ok or _contact_ok_is_not_checked(contact_ok):
        errors = ApiErrors()
        errors.add_error('contact_ok', 'Vous devez obligatoirement cocher cette case.')
        raise errors


def _check_email_is_present(email):
    if email is None:
        errors = ApiErrors()
        errors.add_error('email', 'Vous devez renseigner un email.')
        raise errors


def _contact_ok_is_not_checked(contact_ok):
    contact_ok_is_not_checked_as_bool = contact_ok is not True
    contact_ok_is_not_checked_as_str = str(contact_ok).lower() != 'true'
    return contact_ok_is_not_checked_as_bool and contact_ok_is_not_checked_as_str


def check_validation_token_has_been_already_used(user):
    if user is None:
        errors = ResourceNotFoundError()
        errors.add_error(
            'validation',
              "Aucun(e) objet ne correspond à ce code de validation" \
               + " ou l'objet est déjà validé"
        )
        raise errors
