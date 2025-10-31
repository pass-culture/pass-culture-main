import datetime

import flask
import wtforms
from flask import flash
from flask_wtf import FlaskForm

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class SearchHighlightForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Recherche dans le nom")

    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (10, "Afficher 10 résultats maximum"),
            (25, "Afficher 25 résultats maximum"),
            (50, "Afficher 50 résultats maximum"),
            (100, "Afficher 100 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        return not any((self.q.data,))


class CreateHighlightForm(FlaskForm):
    name = fields.PCStringField(
        "Nom du temps fort",
        validators=(
            wtforms.validators.InputRequired("Le nom est obligatoire"),
            wtforms.validators.Length(max=200, message="doit contenir moins de %(max)d caractères"),
        ),
    )

    description = fields.PCTextareaField(
        "Description",
        rows=10,
        validators=(
            wtforms.validators.InputRequired("La description est obligatoire"),
            wtforms.validators.Length(max=300, message="ne doit pas dépasser %(max)d caractères"),
        ),
    )
    availability_timespan = fields.PCDateRangeField(
        "Dates de disponibilité sur l'espace partenaire",
        validators=(
            wtforms.validators.InputRequired("Les dates de disponibilité sur l'espace partenaire sont obligatoires"),
        ),
        drops="up",
    )
    highlight_timespan = fields.PCDateRangeField(
        "Dates du temps fort",
        validators=(wtforms.validators.InputRequired("Les dates du temps fort sont obligatoires"),),
        drops="up",
    )
    image = fields.PCImageField(
        "Image du temps fort (max. 1 Mo)",
        validators=(wtforms.validators.InputRequired("L'image du temps fort est obligatoire"),),
    )

    def get_image_as_bytes(self, request: flask.Request) -> bytes:
        """
        Get the image from the POSTed data (request)
        """
        blob = request.files["image"]
        return blob.read()

    def get_image_mimetype(self, request: flask.Request) -> str:
        return request.files["image"].mimetype

    def validate(self, extra_validators: dict | None = None) -> bool:
        if not super().validate(extra_validators):
            return False

        availability_timespan = self._fields["availability_timespan"].data
        highlight_timespan = self._fields["highlight_timespan"].data

        if availability_timespan[1] > highlight_timespan[1]:
            flash(
                "La disponibilité sur l'espace partenaire ne peut pas se terminer après la fin du temps fort",
                "warning",
            )
            return False
        return True

    def validate_availability_timespan(self, dates: fields.PCDateRangeField) -> fields.PCDateRangeField:
        if dates.data[1] and dates.data[1].date() < datetime.date.today():
            raise wtforms.validators.ValidationError(
                "La date de fin de disponibilité sur l'espace partenaire ne peut pas être dans le passé",
            )
        return dates

    def validate_highlight_timespan(self, dates: fields.PCDateRangeField) -> fields.PCDateRangeField:
        if dates.data[1] and dates.data[1].date() < datetime.date.today():
            raise wtforms.validators.ValidationError(
                "La date de fin du temps fort ne peut pas être dans le passé",
            )
        return dates


class UpdateHighlightForm(CreateHighlightForm):
    image = fields.PCImageField(
        "Ajouter une image seulement pour modifier la précédente. Image du temps fort (max. 1 Mo)",
    )
