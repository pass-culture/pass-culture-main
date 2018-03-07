from flask import current_app as app, request
from flask_login import LoginManager, login_user

app.login_manager = LoginManager()
app.login_manager.init_app(app)
User = app.model.User

def get_user_with_credentials (identifier, password):
    if identifier is None or password is None:
        abort(400) # missing arguments

    user = User.query.filter_by(email=identifier).first()

    if not user:
        print("Wrong identifier")
        return {
            "error": 401,
            "message": "Le password ou l'identifiant est invalide"
        }
    if user.checkPassword(password):
        login_user(user)
        return user
    else:
        print("Wrong password")
        return {
            "error": 401,
            "message": "Le password ou l'identifiant est invalide"
        }

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
