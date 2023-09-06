from flask_wtf import FlaskForm
import wtforms

from pcapi.core.permissions import models as perm_models

from ..forms import fields
from ..forms import utils


class EditPermissionForm(FlaskForm):
    @classmethod
    def setup_form_fields(cls, permissions: list[perm_models.Permission]) -> None:
        for perm in permissions:
            perm_description = (
                perm_models.Permissions[perm.name].value if perm_models.Permissions.exists(perm.name) else ""
            )
            setattr(
                cls,
                perm.name,
                fields.PCSwitchBooleanField(perm_description),
            )

    def fill_form(self, permissions: list[perm_models.Permission], role: perm_models.Role) -> None:
        for perm in permissions:
            self._fields[perm.name].data = perm in role.permissions


class BOUserSearchForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField(label="")
    page = wtforms.HiddenField("page", default=1, validators=[wtforms.validators.Optional()])
    per_page = wtforms.HiddenField("per_page", default=30, validators=[wtforms.validators.Optional()])

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data and "%" in q.data:
            raise wtforms.validators.ValidationError("Le caractère % n'est pas autorisé")
        return q


class EditBOUserForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
