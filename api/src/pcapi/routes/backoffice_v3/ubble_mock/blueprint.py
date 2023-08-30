from flask import redirect
from flask import render_template
from flask import url_for

from pcapi.routes.backoffice_v3 import blueprint
from pcapi.routes.backoffice_v3 import utils
from pcapi.routes.internal.e2e_ubble import configure_identification_response

from . import forms


@blueprint.backoffice_v3_web.route("/admin/ubble-mock", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
def get_ubble_response() -> utils.BackofficeResponse:
    form = forms.UbbleResponseForm()
    return render_template(
        "admin/ubble_mock.html",
        form=form,
        dst=url_for("backoffice_v3_web.configure_ubble_response"),
    )


@blueprint.backoffice_v3_web.route("/admin/ubble-mock", methods=["POST"])
@utils.custom_login_required(redirect_to=".home")
def configure_ubble_response() -> utils.BackofficeResponse:
    form = forms.UbbleResponseForm()
    configure_identification_response(form.data)
    return redirect(url_for("backoffice_v3_web.get_ubble_response"), code=303)
