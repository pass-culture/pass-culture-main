from pcapi.core.offers import tasks
from pcapi.flask_app import app as flask_app


celery_app = flask_app.extensions["celery"]
