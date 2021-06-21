from flask.helpers import flash
from wtforms import Form
from wtforms import validators
from wtforms.fields.core import Field
from wtforms.fields.core import StringField
from wtforms.validators import ValidationError

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.offerers.models import ApiKey
from pcapi.models.db import db
from pcapi.repository.offerer_queries import find_by_siren
from pcapi.utils.token import random_token


def check_siren(form: Form, field: Field) -> None:
    offerer = find_by_siren(field.data)
    if not offerer:
        raise ValidationError("Aucune structure existante avec ce SIREN.")
    if ApiKey.query.filter_by(offererId=offerer.id).first():
        raise ValidationError("Cette structure a déjà une clé API.")


class ApiKeyView(BaseAdminView):
    can_create = True
    column_list = ["offerer.siren", "value"]
    column_labels = {"offerer.siren": "Siren de la structure", "value": "Clé API"}
    form_columns = None
    form_excluded_columns = ["offerer", "value"]
    column_formatters = dict(
        value=lambda v, c, m, p: f"{m.value[:8]}************************************************{m.value[-8:]}"
    )

    def get_create_form(self) -> Form:
        form = super().get_form()
        form.offererSiren = StringField(
            "SIREN",
            [
                validators.DataRequired(),
                validators.Length(9, 9, "Un SIREN contient 9 caractères"),
                check_siren,
            ],
        )
        return form

    def on_model_change(self, form: Form, model: ApiKey, is_created: bool) -> None:
        if is_created:
            with db.session.no_autoflush:
                model.offererId = find_by_siren(form.offererSiren.data).id
            model.value = random_token(64)
        flash(
            f"La Clé API ne peut être régénérée ni ré-affichée, veillez à la sauvegarder immédiatement : {model.value}"
        )
        super().on_model_change(form, model, is_created)
