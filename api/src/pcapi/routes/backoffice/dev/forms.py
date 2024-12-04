from flask_wtf import FlaskForm
import wtforms

from pcapi.core.users import constants as users_constants
from pcapi.core.users.generator import GeneratedIdProvider
from pcapi.core.users.generator import GeneratedSubscriptionStep
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils

from ..forms import fields


class SimpleComponentsForm(FlaskForm):
    checkbox = fields.PCCheckboxField("checkbox")
    stringfield = fields.PCStringField("string field")
    password = fields.PCPasswordField("password")
    postal_code = fields.PCPostalCodeField("code postal")
    text_area = fields.PCTextareaField("text area")
    interger = fields.PCIntegerField("nombre entier")
    decimal = fields.PCDecimalField("nombre décimal")
    date_time = fields.PCDateTimeField("date et heure")
    date = fields.PCDateField("date")
    date_range = fields.PCDateRangeField("interval de dates")
    select = fields.PCSelectWithPlaceholderValueField("un seul choix", choices=((1, "choix 1"), (2, "choix 2")))
    multiselect = fields.PCSelectMultipleField("plusieurs choix", choices=((1, "choix 1"), (2, "choix 2")))
    tomselect = fields.PCTomSelectField(
        "autocomplete",
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
    )
    switch = fields.PCSwitchBooleanField("interrupteur")


class UserGeneratorForm(utils.PCForm):
    age = fields.PCIntegerField(
        "Age",
        default=users_constants.ELIGIBILITY_AGE_18,
        validators=[
            wtforms.validators.NumberRange(min=15, max=20, message="L'âge doit être entre 15 et 20 ans."),
        ],
    )
    id_provider = fields.PCSelectField(
        "Méthode d'identification",
        choices=[
            (GeneratedIdProvider.DMS.name, "DMS"),
            (GeneratedIdProvider.EDUCONNECT.name, "Educonnect"),
            (GeneratedIdProvider.UBBLE.name, "Ubble"),
        ],
        default=GeneratedIdProvider.UBBLE.name,
    )
    step = fields.PCSelectField(
        "Étape de validation",
        choices=[
            (GeneratedSubscriptionStep.EMAIL_VALIDATION.name, "Email Validé"),
            (GeneratedSubscriptionStep.PHONE_VALIDATION.name, "Téléphone validé"),
            (GeneratedSubscriptionStep.PROFILE_COMPLETION.name, "Profil complété"),
            (GeneratedSubscriptionStep.IDENTITY_CHECK.name, "Identité vérifiée"),
            (GeneratedSubscriptionStep.HONOR_STATEMENT.name, "Attesté sur l'honneur"),
            (GeneratedSubscriptionStep.BENEFICIARY.name, "Bénéficiaire"),
        ],
        default=GeneratedSubscriptionStep.EMAIL_VALIDATION.name,
    )
    transition_17_18 = fields.PCCheckboxField("Transition 17-18")


class UserDeletionForm(utils.PCForm):
    email = fields.PCEmailField("compte_sso_jeune@example.com")
