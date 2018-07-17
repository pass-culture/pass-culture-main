from flask import current_app as app, jsonify
from flask_login import LoginManager, login_user

from models.api_errors import ApiErrors
from models.user import User

app.login_manager = LoginManager()
app.login_manager.init_app(app)
User = User

app.config['REMEMBER_COOKIE_DURATION'] = 365 * 24 * 3600


def get_user_with_credentials(identifier, password):
    errors = ApiErrors()
    errors.status_code = 401

    if identifier is None:
        errors.addError('identifier', 'Identifiant manquant')
    if password is None:
        errors.addError('password', 'Mot de passe manquant')
    errors.maybeRaise()

    user = User.query.filter_by(email=identifier).first()

    if not user:
        errors.addError('identifier', 'Identifiant incorrect')
        raise errors
    if not user.isValidated:
        errors.addError('identifier', "Ce compte n'est pas validé.")
        raise errors
    if not user.checkPassword(password):
        errors.addError('password', 'Mot de passe incorrect')
        raise errors

    login_user(user, remember=True)
    return user

app.get_user_with_credentials = get_user_with_credentials

@app.login_manager.user_loader
def get_user_with_id(user_id):
    return User.query.get(user_id)


@app.login_manager.request_loader
def get_user_with_request(request):
    auth = request.authorization
    if not auth:
        return None
    user = get_user_with_credentials(auth.username, auth.password)
    return user


@app.login_manager.unauthorized_handler
def send_401():
    e = ApiErrors()
    e.addError('global', 'Authentification nécessaire')
    return jsonify(e.errors), 401
