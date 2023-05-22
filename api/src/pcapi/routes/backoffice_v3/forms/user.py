import re
import typing

from flask import url_for
from flask_wtf import FlaskForm
import wtforms

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


class BatchSuspendUsersForm(SuspendUserForm):
    user_ids = fields.PCTextareaField(
        "Liste des ID d'utilisateurs",
        rows=10,
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=10000, message="doit contenir entre %(min)d et %(max)d caractères"),
        ),
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("user_ids", last=False)

    def validate_user_ids(self, user_ids: fields.PCTextareaField) -> fields.PCTextareaField:
        if user_ids.data:
            if not re.match(r"^[\d\s,;]+$", user_ids.data):
                raise wtforms.validators.ValidationError(
                    "Seuls les chiffres, espaces, tabulations, retours à la ligne et virgules sont autorisés"
                )
            user_ids.data = " ".join(re.split(r"[\s,;]+", user_ids.data)).strip()
        return user_ids

    def get_user_ids(self) -> set[int]:
        return {int(user_id) for user_id in self.user_ids.data.split(" ")}
