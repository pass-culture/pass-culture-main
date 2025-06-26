from pcapi.core.offers import tasks  # noqa: F401
from pcapi.flask_app import app as flask_app


celery_app = flask_app.extensions["celery"]
