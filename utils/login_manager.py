""" login_manager """
from flask import current_app as app, jsonify, session
from flask_login import LoginManager

from models.api_errors import ApiErrors
from models.user import User
from repository.user_queries import existing_user_session
from utils.credentials import get_user_with_credentials

app.login_manager = LoginManager()
app.login_manager.init_app(app)

app.config['REMEMBER_COOKIE_DURATION'] = 365 * 24 * 3600


@app.login_manager.user_loader
def get_user_with_id(user_id):
    session_uuid = session.get('session_uuid')
    if existing_user_session(user_id, session_uuid):
        return User.query.get(user_id)
    else:
        return None


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
