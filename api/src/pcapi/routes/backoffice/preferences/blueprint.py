from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user

from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.preferences import forms


# Preferences are currently limited to permission READ_PRO_ENTITY because a single setting is available, which only
# concerns search for pro; this required permission may be removed in the future so that everyone has access.
preferences_blueprint = utils.child_backoffice_blueprint(
    "preferences",
    __name__,
    url_prefix="/preferences",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@preferences_blueprint.route("", methods=["GET"])
def edit_preferences() -> utils.BackofficeResponse:
    preferences = current_user.backoffice_profile.preferences

    form = forms.EditPreferencesForm(departments=preferences.get("departments"))

    return render_template(
        "preferences/edit.html",
        form=form,
        dst=url_for(".save_preferences"),
    )


@preferences_blueprint.route("", methods=["POST"])
def save_preferences() -> utils.BackofficeResponse:
    form = forms.EditPreferencesForm()

    preferences = current_user.backoffice_profile.preferences
    preferences.update(
        {
            "departments": form.departments.data,
        }
    )
    current_user.backoffice_profile.preferences = preferences
    db.session.flush()

    flash("Les préférences ont été enregistrées", "success")
    return redirect(request.referrer or url_for(".edit_preferences"), 303)
