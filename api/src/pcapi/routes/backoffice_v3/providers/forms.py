from flask_wtf import FlaskForm
import wtforms

from ..forms import fields


class SearchProviderForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID ou nom de lieu, identifiant cinéma")


class EditProviderForm(FlaskForm):
    venue_id = fields.PCTomSelectField(
        "Lieu", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_venues", coerce=int
    )


class EditAllocineForm(EditProviderForm):
    theater_id = fields.PCStringField(
        "Identifiant cinéma (Allociné)",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=20, message="Doit contenir au maximum %(max)d caractères"),
        ),
    )
    internal_id = fields.PCStringField("Identifiant interne Allociné")


# TODO PC-21791
class EditBoostForm(EditProviderForm):
    cinema_id = fields.PCStringField("Identifiant Cinéma (Boost)")
    username = fields.PCStringField("Nom de l'utilisateur (Boost)")
    password = fields.PCStringField("Mot de passe (Boost)")
    cinema_url = fields.PCStringField(
        "URL du cinéma (Boost)",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.URL("Doit avoir la forme d'une URL"),
        ),
    )


# TODO PC-21790
class EditCGRForm(EditProviderForm):
    cinema_id = fields.PCStringField("URL du cinéma (CGR)")
    cinema_url = fields.PCStringField(
        "Identifiant Cinéma (CGR)",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.URL("Doit avoir la forme d'une URL"),
        ),
    )


# TODO PC-21792
class EditCineOfficeForm(EditProviderForm):
    cinema_id = fields.PCStringField("Identifiant cinéma (CDS)")
    account_id = fields.PCStringField("Nom de compte (CDS)")
    api_token = fields.PCStringField("Clé API (CDS)")
