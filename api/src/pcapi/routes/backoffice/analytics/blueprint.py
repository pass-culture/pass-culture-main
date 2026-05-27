import logging

from flask import current_app as app
from flask import request

from pcapi.routes.backoffice import blueprint as backoffice_blueprint
from pcapi.routes.backoffice.utils import access_control
from pcapi.routes.backoffice.utils import response as response_utils
from pcapi.routes.backoffice.utils.logs import log_backoffice_tracking_data

from .forms import AnalyticsRegisterForm


logger = logging.getLogger(__name__)

analytics_blueprint = backoffice_blueprint.child_backoffice_blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics",
)


@analytics_blueprint.route("/save", methods=["GET"])
@access_control.custom_login_required(redirect_to="backoffice_web.home")
def save() -> response_utils.BackofficeResponse:
    form = AnalyticsRegisterForm(request.args)
    if not form.validate():
        logger.error("Faulty analytics received", extra={"errors": {field.name: field.errors for field in form}})
        return ""

    with app.test_request_context(form.origin.data) as request_ctx:
        rule = request_ctx.request.url_rule

    if not rule:
        logger.error("Faulty analytics received", extra={"errors": f"No route found for url {form.origin.data}"})
        return ""

    log_backoffice_tracking_data(
        event_name="Analytics event",
        extra_data={"eventOrigin": rule.endpoint, "eventName": form.name.data, "eventType": form.type.data},
    )
    return ""
