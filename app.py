#!/usr/bin/env python
import os

from flask import Flask
from flask_admin import Admin
from flask_cors import CORS
from flask_login import LoginManager
from mailjet_rest import Client
from werkzeug.middleware.profiler import ProfilerMiddleware
from admin.install import install_admin_views
from models.mediation import upsertTutoMediations
from repository.features import feature_request_profiling_enabled
from local_providers.install import install_local_providers
from models.db import db
from models.install import install_models
from routes import install_routes
from utils.config import IS_DEV
from utils.json_encoder import EnumJSONEncoder
from utils.mailing import get_contact, \
    MAILJET_API_KEY, \
    MAILJET_API_SECRET, \
    subscribe_newsletter

app = Flask(__name__, static_url_path='/static')
login_manager = LoginManager()
admin = Admin(name='pc Back Office', url='/pc/back-office', template_mode='bootstrap3')


if feature_request_profiling_enabled():
    profiling_restrictions = [os.environ.get('PROFILE_REQUESTS_LINES_LIMIT', 100)]
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                      restrictions=profiling_restrictions)

app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.json_encoder = EnumJSONEncoder
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_POOL_SIZE'] = int(os.environ.get('DATABASE_POOL_SIZE', 20))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False if IS_DEV else True
app.config['REMEMBER_COOKIE_DURATION'] = 90 * 24 * 3600
app.config['PERMANENT_SESSION_LIFETIME'] = 90 * 24 * 3600
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

@app.teardown_request
def remove_db_session(exc):
    try:
        db.session.remove()
    except AttributeError:
        pass


admin.init_app(app)
db.init_app(app)
login_manager.init_app(app)
cors = CORS(app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# make Werkzeug match routing rules with or without a trailing slash
app.url_map.strict_slashes = False

with app.app_context():
    if IS_DEV:
        install_models()
        upsertTutoMediations()
        install_local_providers()
    import utils.login_manager
    install_routes()
    install_admin_views(admin, db.session)

    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

    app.get_contact = get_contact
    app.subscribe_newsletter = subscribe_newsletter


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=IS_DEV, use_reloader=True)
