import datetime
import enum

import wtforms
from dateutil.relativedelta import relativedelta
from flask_wtf import FlaskForm

from pcapi.core.categories import subcategories
from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_18_v2
from pcapi.core.subscription.ubble import schemas as ubble_schemas
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


def get_max_birth_date() -> datetime.date:
    return datetime.date.today() - relativedelta(years=15)


def get_min_birth_date() -> datetime.date:
    return datetime.date(1900, 1, 1)


def get_default_birth_date() -> datetime.date:
    return datetime.date.today() - relativedelta(years=18)


class UserGeneratorForm(utils.PCForm):
    age = fields.PCOptHiddenIntegerField(
        "Age",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=15, max=20, message="L'âge doit être entre 15 et 20 ans."),
        ],
    )
    birth_date = fields.PCDateField(
        "Date de naissance",
        validators=[
            wtforms.validators.Optional(),
            fields.DateRangeValidator(min=get_min_birth_date, max=get_max_birth_date),
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
    date_created = fields.PCDateField("Date de création du compte", default=datetime.date.today)
    credit = fields.PCDecimalField(
        "Crédit restant",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=0, max=GRANTED_DEPOSIT_AMOUNT_18_v2),
        ],
    )
    postal_code = fields.PCOptPostalCodeField("Code postal")

    def validate(self, extra_validators: dict | None = None) -> bool:
        # Ensure that we have either age exclusive or birth_date.
        is_valid = super().validate(extra_validators)
        if bool(self.age.data) == bool(self.birth_date.data):
            self.age.errors.append("Il faut renseigner soit l'âge soit la date de naissance.")
            self.birth_date.errors.append("Il faut renseigner soit l'âge soit la date de naissance.")
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


class QFMockType(enum.Enum):
    OK = "OK"
    HOUSEHOLDER_OK = "HOUSEHOLDER_OK"
    NOT_IN_TAX_HOUSEHOLD = "NOT_IN_TAX_HOUSEHOLD"
    QUOTIENT_FAMILIAL_TOO_HIGH = "QUOTIENT_FAMILIAL_TOO_HIGH"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    PERSON_NOT_FOUND = "PERSON_NOT_FOUND"
    DATA_PROVIDER_ERROR = "DATA_PROVIDER_ERROR"


class QuotientFamilialConfigurationForm(utils.PCForm):
    mock_type = fields.PCSelectField(
        "Type de mock",
        choices=[
            (QFMockType.OK.value, "Ok cas courant"),
            (QFMockType.HOUSEHOLDER_OK.value, "Ok émancipé"),
            (QFMockType.NOT_IN_TAX_HOUSEHOLD.value, "Pas associé au dossier demandé"),
            (QFMockType.QUOTIENT_FAMILIAL_TOO_HIGH.value, "Quotient familial trop élevé"),
            (QFMockType.APPLICATION_NOT_FOUND.value, "404 impossible de trouver le dossier"),
            (QFMockType.PERSON_NOT_FOUND.value, "422 problème de données d'identification"),
            (QFMockType.DATA_PROVIDER_ERROR.value, "502 erreur du fournisseur de données"),
        ],
        default=QFMockType.OK.value,
    )


class DisabledAdultAllowanceMockType(enum.Enum):
    RECIPIENT = "RECIPIENT"
    NON_RECIPIENT = "NON_RECIPIENT"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    PERSON_NOT_FOUND = "PERSON_NOT_FOUND"
    DATA_PROVIDER_ERROR = "DATA_PROVIDER_ERROR"


class DisabledAdultAllowanceConfigurationForm(utils.PCForm):
    mock_type = fields.PCSelectField(
        "Type de mock",
        choices=[
            (DisabledAdultAllowanceMockType.RECIPIENT.value, "Ok bénéficiaire"),
            (DisabledAdultAllowanceMockType.NON_RECIPIENT.value, "Non bénéficiaire"),
            (DisabledAdultAllowanceMockType.APPLICATION_NOT_FOUND.value, "404 impossible de trouver le dossier"),
            (DisabledAdultAllowanceMockType.PERSON_NOT_FOUND.value, "422 problème de données d'identification"),
            (DisabledAdultAllowanceMockType.DATA_PROVIDER_ERROR.value, "502 erreur du fournisseur de données"),
        ],
        default=DisabledAdultAllowanceMockType.RECIPIENT.value,
    )


class DisabledChildEducationAllowanceMockType(enum.Enum):
    RECIPIENT = "RECIPIENT"
    RIGHT_OPENING = "RIGHT_OPENING"
    NON_RECIPIENT = "NON_RECIPIENT"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    PERSON_NOT_FOUND = "PERSON_NOT_FOUND"
    DATA_PROVIDER_ERROR = "DATA_PROVIDER_ERROR"


class DisabledChildEducationAllowanceConfigurationForm(utils.PCForm):
    mock_type = fields.PCSelectField(
        "Type de mock",
        choices=[
            (DisabledChildEducationAllowanceMockType.RECIPIENT.value, "Ok bénéficiaire"),
            (DisabledChildEducationAllowanceMockType.RIGHT_OPENING.value, "Ok ouvrant droit"),
            (DisabledChildEducationAllowanceMockType.NON_RECIPIENT.value, "Non bénéficiaire"),
            (
                DisabledChildEducationAllowanceMockType.APPLICATION_NOT_FOUND.value,
                "404 impossible de trouver le dossier",
            ),
            (
                DisabledChildEducationAllowanceMockType.PERSON_NOT_FOUND.value,
                "422 problème de données d'identification",
            ),
            (
                DisabledChildEducationAllowanceMockType.DATA_PROVIDER_ERROR.value,
                "502 erreur du fournisseur de données",
            ),
        ],
        default=DisabledChildEducationAllowanceMockType.RECIPIENT.value,
    )


class OfferGeneratorForm(utils.PCForm):
    name = fields.PCStringField("Nom de l'offre")
    price = fields.PCDecimalField(
        "Prix de l'offre",
        validators=[
            wtforms.validators.DataRequired("Information obligatoire"),
        ],
    )
    subcategory_id = fields.PCSelectField(
        "Sous-catégorie",
        choices=[(subcategories.SEANCE_CINE.id, subcategories.SEANCE_CINE.app_label)],
        default=subcategories.SEANCE_CINE.id,
    )
    is_duo = fields.PCSwitchBooleanField("Offre Duo", default=False)
