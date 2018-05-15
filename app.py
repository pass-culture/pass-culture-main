import os
from os.path import isfile, join
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from utils.config import IS_DEV

dev_env_file_dir = join(os.getcwd(), 'dev_env_file')
if IS_DEV and isfile(dev_env_file_dir):
    load_dotenv(dotenv_path=dev_env_file_dir, override=True)

app = Flask(__name__, static_url_path='/static')

app.secret_key = os.environ.get('FLASK_SECRET', '+%+3Q23!zbc+!Dd@')

cors = CORS(app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# make Werkzeug match routing rules with or without a trailing slash
app.url_map.strict_slashes = False

with app.app_context():
    import models
    import utils.login_manager
    import local_providers
    import routes

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=IS_DEV, use_reloader=True)
