import wtforms

from pcapi.core.fraud.models import UBBLE_OK_REASON_CODE
from pcapi.core.fraud.models import UBBLE_REASON_CODE_MAPPING
from pcapi.core.users import constants as users_constants
from pcapi.core.users.generator import GeneratedIdProvider
from pcapi.core.users.generator import GeneratedSubscriptionStep
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


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


def _get_ubble_first_response_code_choices() -> list[tuple[int, str]]:
    ok_response_codes = [(UBBLE_OK_REASON_CODE, "10000 - OK")]
    ubble_error_reason_code_choices = [
        (reason_code, f"{reason_code} - {fraud_reason_code.name}")
        for reason_code, fraud_reason_code in UBBLE_REASON_CODE_MAPPING.items()
        if reason_code > 60000
    ]
    return ok_response_codes + ubble_error_reason_code_choices


def _get_ubble_final_response_code_choices() -> list[tuple[int, str]]:
    ok_response_codes = [(UBBLE_OK_REASON_CODE, "10000 - OK")]
    ubble_final_error_reason_code_choices = [
        (reason_code, f"{reason_code} - {fraud_reason_code.name}")
        for reason_code, fraud_reason_code in UBBLE_REASON_CODE_MAPPING.items()
        if reason_code > 62000
    ]
    return ok_response_codes + ubble_final_error_reason_code_choices


class UbbleConfigurationForm(utils.PCForm):
    birth_date = fields.PCDateField("Date de naissance")
    first_response_code = fields.PCSelectField(
        "Premier code de réponse", choices=_get_ubble_first_response_code_choices()
    )
    second_response_code = fields.PCSelectField(
        "Second code de réponse",
        choices=_get_ubble_final_response_code_choices(),
        validators=(wtforms.validators.Optional(),),
    )
