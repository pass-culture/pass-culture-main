""" app """
import os
from flask_cors import CORS
from flask import Flask
from mailjet_rest import Client

from models.db import db
from utils.config import IS_DEV
from utils.mailing import get_contact, subscribe_newsletter, MAILJET_API_KEY, MAILJET_API_SECRET

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

cors = CORS(app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# make Werkzeug match routing rules with or without a trailing slash
app.url_map.strict_slashes = False

with app.app_context():
    import models.install
    import utils.login_manager
    import utils.logger
    import local_providers
    import routes

    app.mailjet_client = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3')

    app.get_contact = get_contact
    app.subscribe_newsletter = subscribe_newsletter

    app.model = {}
    for model_name in models.__all__:
        app.model[model_name] = getattr(models, model_name)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=IS_DEV, use_reloader=True)
