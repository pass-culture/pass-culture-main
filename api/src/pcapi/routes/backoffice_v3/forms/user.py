from flask import url_for
from flask_wtf import FlaskForm

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice_v3.utils import has_current_user_permission

from . import fields


class SuspendUserForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison de la suspension",
        choices=[
            (opt.name, users_constants.SUSPENSION_REASON_CHOICES[opt]) for opt in users_constants.SuspensionReason
        ],
    )
    comment = fields.PCOptCommentField("Commentaire interne optionnel")


class UnsuspendUserForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne optionnel")


def get_toggle_suspension_args(user: users_models.User) -> dict:
    """
    Additional arguments which must be passed to render_template when the page may show suspend/unsuspend button.
    """

    if user.isActive and has_current_user_permission(perm_models.Permissions.SUSPEND_USER):
        return {
            "suspension_form": SuspendUserForm(),
            "suspension_dst": url_for("backoffice_v3_web.users.suspend_user", user_id=user.id),
        }
    if not user.isActive and has_current_user_permission(perm_models.Permissions.UNSUSPEND_USER):
        return {
            "suspension_form": UnsuspendUserForm(),
            "suspension_dst": url_for("backoffice_v3_web.users.unsuspend_user", user_id=user.id),
        }
    return {}
