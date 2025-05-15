import enum
import re
import typing

import wtforms
from flask import url_for
from flask_wtf import FlaskForm

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.utils import has_current_user_permission


class SuspensionUserType(enum.Enum):
    PRO = "pro user"
    PUBLIC = "public user"
    ADMIN = "admin_user"


class SuspendUserForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison de la suspension",
        choices=[
            (opt.name, users_constants.SUSPENSION_REASON_CHOICES[opt]) for opt in users_constants.SuspensionReason
        ],
    )
    comment = fields.PCOptCommentField("Commentaire interne optionnel")
    clear_email = fields.PCSwitchBooleanField(
        "Supprimer l'adresse email (à utiliser pour les cas de doublons afin de la libérer)", full_row=True
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        suspension_type = kwargs.get("suspension_type")
        if suspension_type == SuspensionUserType.PRO:
            self.reason.choices = [
                (opt.name, users_constants.PRO_SUSPENSION_REASON_CHOICES[opt])
                for opt in set(users_constants.PRO_SUSPENSION_REASON_CHOICES)
            ]
        if suspension_type in (SuspensionUserType.PUBLIC, SuspensionUserType.ADMIN):
            self.reason.choices = [
                (opt.name, users_constants.PUBLIC_SUSPENSION_REASON_CHOICES[opt])
                for opt in set(users_constants.PUBLIC_SUSPENSION_REASON_CHOICES)
            ]
        if suspension_type in (SuspensionUserType.PRO, SuspensionUserType.ADMIN):
            del self.clear_email


class UnsuspendUserForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne optionnel")


def get_toggle_suspension_args(
    user: users_models.User,
    *,
    suspension_type: SuspensionUserType | None = None,
    required_permission: perm_models.Permissions | None = None,
) -> dict:
    """
    Additional arguments which must be passed to render_template when the page may show suspend/unsuspend button.
    """

    if user.isActive and has_current_user_permission(required_permission or perm_models.Permissions.SUSPEND_USER):
        return {
            "suspension_form": SuspendUserForm(suspension_type=suspension_type),
            "suspension_dst": url_for("backoffice_web.users.suspend_user", user_id=user.id),
        }
    if not user.isActive and has_current_user_permission(required_permission or perm_models.Permissions.UNSUSPEND_USER):
        return {
            "suspension_form": UnsuspendUserForm(),
            "suspension_dst": url_for("backoffice_web.users.unsuspend_user", user_id=user.id),
        }
    return {}


class BatchSuspendUsersForm(SuspendUserForm):
    user_ids = fields.PCTextareaField(
        "Liste des ID d'utilisateurs",
        rows=10,
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
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
