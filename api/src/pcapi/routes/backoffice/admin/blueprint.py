from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user

from pcapi import settings
from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.models import feature as feature_models
from pcapi.notifications.internal.transactional import change_feature_flip as change_feature_flip_internal_message
from pcapi.repository import repository

from . import forms
from .. import blueprint
from .. import utils
from ..forms import empty as empty_forms


@blueprint.backoffice_web.route("/admin/roles", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def get_roles() -> utils.BackofficeResponse:
    roles = perm_api.list_roles()
    roles.sort(key=lambda role: role.name)
    permissions = perm_api.list_permissions()
    permissions.sort(key=lambda perm: perm.name)
    perm_forms = {}

    forms.EditPermissionForm.setup_form_fields(permissions)

    # fill the form with existing data
    for role in roles:
        perm_form = forms.EditPermissionForm()
        perm_form.fill_form(permissions, role)
        perm_forms[role] = perm_form

    return render_template("admin/roles.html", forms=perm_forms)


@blueprint.backoffice_web.route("/admin/roles/<int:role_id>", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def update_role(role_id: int) -> utils.BackofficeResponse:
    permissions = perm_api.list_permissions()

    forms.EditPermissionForm.setup_form_fields(permissions)

    new_permissions_ids = []
    perm_form = forms.EditPermissionForm()

    if not perm_form.validate():
        flash(utils.build_form_error_msg(perm_form), "warning")
        return render_template("admin/roles.html"), 400

    for perm in permissions:
        if perm_form._fields[perm.name].data:
            new_permissions_ids.append(perm.id)

    roles = {role.id: role for role in perm_api.list_roles()}
    role_name = roles[role_id].name

    perm_api.update_role(role_id, role_name, tuple(new_permissions_ids))
    flash("Informations mises à jour", "success")

    return redirect(url_for(".get_roles"), code=303)


@blueprint.backoffice_web.route("/admin/feature-flipping", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FEATURE_FLIPPING)
def list_feature_flags() -> utils.BackofficeResponse:
    feature_flags = feature_models.Feature.query.order_by(feature_models.Feature.name).all()
    form = empty_forms.EmptyForm()
    return render_template(
        "admin/feature_flipping.html", rows=feature_flags, toggle_feature_flag_form=form, env=settings.ENV
    )


@blueprint.backoffice_web.route("/admin/feature-flipping/<int:feature_flag_id>/enable", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FEATURE_FLIPPING)
def enable_feature_flag(feature_flag_id: int) -> utils.BackofficeResponse:
    return toggle_feature_flag(feature_flag_id, True)


@blueprint.backoffice_web.route("/admin/feature-flipping/<int:feature_flag_id>/disable", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FEATURE_FLIPPING)
def disable_feature_flag(feature_flag_id: int) -> utils.BackofficeResponse:
    return toggle_feature_flag(feature_flag_id, False)


def toggle_feature_flag(feature_flag_id: int, set_to_active: bool) -> utils.BackofficeResponse:
    feature_flag = feature_models.Feature.query.get_or_404(feature_flag_id)
    if feature_flag.isActive == set_to_active:
        flash(
            f"Le feature flag {feature_flag.name} est déjà " + ("activé" if feature_flag.isActive else "désactivé"),
            "warning",
        )
        return redirect(url_for(".list_feature_flags"), code=303)

    feature_flag.isActive = set_to_active
    repository.save(feature_flag)
    change_feature_flip_internal_message.send(feature=feature_flag, current_user=current_user)

    flash(
        f"Le feature flag {feature_flag.name} a été " + ("activé" if feature_flag.isActive else "désactivé"), "success"
    )
    return redirect(url_for(".list_feature_flags"), code=303)
