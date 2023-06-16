from pcapi.core.users import constants as users_constants
from pcapi.core.users.generator import GeneratedIdProvider
from pcapi.core.users.generator import GeneratedSubscriptionStep
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class UserGeneratorForm(utils.PCForm):
    age = fields.PCIntegerField("Age", default=users_constants.ELIGIBILITY_AGE_18)
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
