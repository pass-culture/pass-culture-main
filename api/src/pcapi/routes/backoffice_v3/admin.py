from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models

from . import blueprint
from . import utils
from .forms import admin


@blueprint.backoffice_v3_web.route("/admin/roles", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def get_roles() -> utils.BackofficeResponse:
    roles = perm_api.list_roles()
    roles.sort(key=lambda role: role.name)
    permissions = perm_api.list_permissions()
    permissions.sort(key=lambda perm: perm.name)
    perm_forms = {}

    admin.EditPermissionForm.setup_form_fields(permissions)

    # fill the form with existing data
    for role in roles:
        perm_form = admin.EditPermissionForm()
        perm_form.fill_form(permissions, role)
        perm_forms[role] = perm_form

    return render_template("admin/roles.html", forms=perm_forms)


@blueprint.backoffice_v3_web.route("/admin/roles/<int:role_id>", methods=["PATCH"])
@utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def update_role(role_id: int) -> utils.BackofficeResponse:
    permissions = perm_api.list_permissions()

    admin.EditPermissionForm.setup_form_fields(permissions)

    new_permissions_ids = []
    perm_form = admin.EditPermissionForm()

    if not perm_form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return render_template("admin/roles.html"), 400

    for perm in permissions:
        if perm_form._fields[perm.name].data:
            new_permissions_ids.append(perm.id)

    roles = {role.id: role for role in perm_api.list_roles()}
    role_name = roles[role_id].name

    perm_api.update_role(role_id, role_name, tuple(new_permissions_ids))
    flash("Informations mises à jour", "success")

    return redirect(url_for(".get_roles"), code=303)
