import datetime

import wtforms
from dateutil.relativedelta import relativedelta
from flask_wtf import FlaskForm

from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_18_v3
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import models as users_models
from pcapi.core.users.generator import GeneratedIdProvider
from pcapi.core.users.generator import GeneratedSubscriptionStep
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


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
    date_range = fields.PCDateRangeField("intervalle de dates")
    select = fields.PCSelectWithPlaceholderValueField("un seul choix", choices=((1, "choix 1"), (2, "choix 2")))
    multiselect = fields.PCSelectMultipleField("plusieurs choix", choices=((1, "choix 1"), (2, "choix 2")))
    tomselect = fields.PCTomSelectField(
        "autocomplete",
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
    )
    switch = fields.PCSwitchBooleanField("interrupteur")


def get_max_birthdate() -> datetime.date:
    return datetime.date.today() - relativedelta(years=15)


def get_min_birthdate() -> datetime.date:
    return datetime.date.today() - relativedelta(years=20)


def get_default_birthdate() -> datetime.date:
    return datetime.date.today() - relativedelta(years=18)


class UserGeneratorForm(utils.PCForm):
    age = fields.PCOptHiddenIntegerField(
        "Age",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=15, max=20, message="L'âge doit être entre 15 et 20 ans."),
        ],
    )
    birthdate = fields.PCDateField(
        "Date de naissance",
        validators=[
            wtforms.validators.Optional(),
            fields.DateRangeValidator(min=get_min_birthdate, max=get_max_birthdate),
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
    date_created = fields.PCDateField("Date de dépôt du dossier", default=datetime.date.today)
    credit = fields.PCDecimalField(
        "Crédit restant",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=0, max=GRANTED_DEPOSIT_AMOUNT_18_v3),
        ],
    )
    postal_code = fields.PCOptPostalCodeField("Code postal")
    transition_17_18 = fields.PCCheckboxField("Transition 17-18")

    def validate(self, extra_validators: dict | None = None) -> bool:
        # Ensure that we have either age exclusive or birthdate.
        is_valid = super().validate(extra_validators)
        if bool(self.age.data) == bool(self.birthdate.data):
            self.age.errors.append("Il faut renseigner soit l'age soit la date de naissance.")
            self.birthdate.errors.append("Il faut renseigner soit l'age soit la date de naissance.")
            return False

        # Ensure that credit is handled only if the generated user is a beneficiary
        if self.credit.data is not None and self.step.data != GeneratedSubscriptionStep.BENEFICIARY.name:
            self.credit.errors.append("L'utilisateur généré doit être bénéficiaire pour pouvoir préciser son crédit")
            return False

        return is_valid


class UserDeletionForm(utils.PCForm):
    email = fields.PCEmailField("compte_sso_jeune@example.com")


def _get_ubble_final_code_choices() -> list[tuple[int, str]]:
    ok_response_codes = [(ubble_schemas.UBBLE_OK_REASON_CODE, "10000 - OK")]
    ubble_final_error_reason_code_choices = [
        (reason_code, f"{reason_code} - {fraud_reason_code.name}")
        for reason_code, fraud_reason_code in ubble_schemas.UBBLE_REASON_CODE_MAPPING.items()
        if reason_code > 62000
    ]
    return ok_response_codes + ubble_final_error_reason_code_choices


def _get_ubble_intermediate_code_choices() -> list[tuple[int, str]]:
    ubble_intermediate_reason_code_choices = [
        (reason_code, f"{reason_code} - {fraud_reason_code.name}")
        for reason_code, fraud_reason_code in ubble_schemas.UBBLE_REASON_CODE_MAPPING.items()
        if 61000 < reason_code < 62000
    ]
    return ubble_intermediate_reason_code_choices


class UbbleConfigurationForm(utils.PCForm):
    birth_date = fields.PCDateField("Date de naissance")
    id_document_number = fields.PCStringField("Numéro de pièce d'identité")
    final_response_code = fields.PCSelectField(
        "Code de réponse final", choices=_get_ubble_final_code_choices(), default=10000
    )
    intermediate_response_code = fields.PCSelectField(
        "Code de réponse intermédiaire (optionnel)",
        choices=_get_ubble_intermediate_code_choices(),
        validators=(wtforms.validators.Optional(),),
    )


class QuotientFamilialConfigurationForm(utils.PCForm):
    https_status_code = fields.PCSelectField(
        "Parent trouvé", choices=[(200, "Parent trouvé"), (404, "Parent non-trouvé")], default=200
    )
    quotient_familial_value = fields.PCIntegerField(
        "Valeur du Quotient Familial", default=bonus_constants.QUOTIENT_FAMILIAL_THRESHOLD
    )
    last_name = fields.PCStringField("Nom de famille de l'enfant")
    common_name = fields.PCOptStringField("Nom d'usage")
    first_names = fields.PCStringField("Prénoms de l'enfant, séparés par une virgule")
    birth_date = fields.PCDateField("Date de naissance")
    gender = fields.PCSelectField(
        "Genre de l'enfant",
        choices=[(users_models.GenderEnum.F.value, "Femme"), (users_models.GenderEnum.M.value, "Homme")],
    )
