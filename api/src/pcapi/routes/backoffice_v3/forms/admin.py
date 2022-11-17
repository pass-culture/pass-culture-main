from flask_wtf import FlaskForm

from pcapi.core.permissions import models as perm_models

from . import fields


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
