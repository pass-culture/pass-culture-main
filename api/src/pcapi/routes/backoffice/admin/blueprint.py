from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from werkzeug.exceptions import NotFound

from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.history import models as history_models
from pcapi.core.permissions import api as perm_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import feature as feature_models
from pcapi.notifications.internal.transactional import change_feature_flip as change_feature_flip_internal_message

from . import forms
from .. import blueprint
from .. import utils
from ..forms import empty as empty_forms


@blueprint.backoffice_web.route("/admin/roles", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PERMISSIONS)
def get_roles() -> utils.BackofficeResponse:
    roles = perm_api.list_roles()
    roles.sort(key=lambda role: role.name)

    roles_for_permissions = (
        db.session.query(perm_models.Permission.name, sa.func.array_agg(perm_models.Role.name))
        .select_from(perm_models.Permission)
        .outerjoin(perm_models.RolePermission)
        .outerjoin(perm_models.Role)
        .group_by(perm_models.Permission.name)
        .order_by(perm_models.Permission.name)
        .all()
    )

    return render_template(
        "admin/roles.html",
        active_tab=request.args.get("active_tab", "matrix"),
        roles=roles,
        permissions=dict(roles_for_permissions),
    )


@blueprint.backoffice_web.route("/admin/roles-matrix", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def get_roles_management() -> utils.BackofficeResponse:
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

    return render_template("admin/roles_management.html", forms=perm_forms)


@blueprint.backoffice_web.route("/admin/roles-history", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_PERMISSIONS)
def get_roles_history() -> utils.BackofficeResponse:
    actions_history = (
        history_models.ActionHistory.query.filter_by(actionType=history_models.ActionType.ROLE_PERMISSIONS_CHANGED)
        .order_by(history_models.ActionHistory.actionDate.desc())
        .options(
            sa_orm.joinedload(history_models.ActionHistory.authorUser).load_only(
                users_models.User.id, users_models.User.firstName, users_models.User.lastName
            ),
        )
        .all()
    )

    return render_template("admin/roles_history.html", actions=actions_history)


@blueprint.backoffice_web.route("/admin/roles/<int:role_id>", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PERMISSIONS)
def update_role(role_id: int) -> utils.BackofficeResponse:
    permissions = perm_api.list_permissions()

    forms.EditPermissionForm.setup_form_fields(permissions)

    perm_form = forms.EditPermissionForm()
    if not perm_form.validate():
        flash(utils.build_form_error_msg(perm_form), "warning")
        return redirect(url_for(".get_roles", active_tab="management"), code=303)

    new_permissions_ids = []
    for perm in permissions:
        if perm_form._fields[perm.name].data:
            new_permissions_ids.append(perm.id)

    roles = {role.id: role for role in perm_api.list_roles()}
    role_name = roles[role_id].name

    perm_api.update_role(
        role_id, role_name, tuple(new_permissions_ids), author=current_user, comment=perm_form.comment.data
    )
    flash(Markup("Le rôle <b>{name}</b> a été mis à jour").format(name=role_name), "success")

    return redirect(url_for(".get_roles", active_tab="management"), code=303)


@blueprint.backoffice_web.route("/admin/feature-flipping", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
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
    feature_flag = feature_models.Feature.query.filter_by(id=feature_flag_id).one_or_none()
    if not feature_flag:
        raise NotFound()

    if feature_flag.isActive == set_to_active:
        flash(
            f"Le feature flag {feature_flag.name} est déjà " + ("activé" if feature_flag.isActive else "désactivé"),
            "warning",
        )
        return redirect(url_for(".list_feature_flags"), code=303)

    feature_flag.isActive = set_to_active
    db.session.add(feature_flag)
    db.session.flush()
    change_feature_flip_internal_message.send(feature=feature_flag, current_user=current_user)

    flash(
        f"Le feature flag {feature_flag.name} a été " + ("activé" if feature_flag.isActive else "désactivé"), "success"
    )
    return redirect(url_for(".list_feature_flags"), code=303)


@blueprint.backoffice_web.route("/admin/subcategories", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
def get_subcategories() -> utils.BackofficeResponse:

    all_subcategories = subcategories.ALL_SUBCATEGORIES_DICT.values()

    return render_template("admin/subcategories.html", rows=all_subcategories)
