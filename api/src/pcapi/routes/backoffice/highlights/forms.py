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
        "Nom de la valorisation thématique",
        validators=(
            wtforms.validators.InputRequired("Le nom est obligatoire"),
            wtforms.validators.Length(max=60, message="doit contenir moins de %(max)d caractères"),
        ),
    )

    description = fields.PCTextareaField(
        "Description",
        rows=10,
        allow_line_breaks=False,  # line breaks are not rendered in the PRO app
        validators=(
            wtforms.validators.InputRequired("La description est obligatoire"),
            wtforms.validators.Length(max=300, message="ne doit pas dépasser %(max)d caractères"),
        ),
    )
    availability_datespan = fields.PCDateRangeField(
        "Dates de diffusion sur l'espace partenaire",
        validators=(
            wtforms.validators.InputRequired("Les dates de diffusion sur l'espace partenaire sont obligatoires"),
        ),
        drops="up",
        upper_inc=True,
    )
    highlight_datespan = fields.PCDateRangeField(
        "Dates de l'évènement",
        validators=(wtforms.validators.InputRequired("Les dates de l'évènement sont obligatoires"),),
        drops="up",
        upper_inc=True,
    )
    communication_date = fields.PCDateField(
        "Date de mise en avant (envoi du mail aux acteurs culturels)",
        validators=(wtforms.validators.InputRequired("La date de mise en avant est obligatoire"),),
    )
    image = fields.PCImageField(
        "Image de la valorisation thématique (max. 3 Mo)",
        validators=(wtforms.validators.InputRequired("L'image de la valorisation thématique est obligatoire"),),
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

        availability_datespan = self._fields["availability_datespan"].data
        highlight_datespan = self._fields["highlight_datespan"].data
        communication_date = self._fields["communication_date"].data

        if communication_date > highlight_datespan[1].date():
            flash(
                "La date de mise en avant ne peut pas être après la fin de l'évènement",
                "warning",
            )
            return False

        if availability_datespan[1] > highlight_datespan[1]:
            flash(
                "La diffusion sur l'espace partenaire ne peut pas se terminer après la fin de l'évènement",
                "warning",
            )
            return False
        return True


class UpdateHighlightForm(CreateHighlightForm):
    image = fields.PCImageField(
        "Ajouter une image seulement pour modifier la précédente. Image de la valorisation thématique (max. 3 Mo)",
    )
