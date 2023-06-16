from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.subscription.models import SubscriptionStep
from pcapi.core.users import constants as users_constants
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class UserGeneratorForm(utils.PCForm):
    age = fields.PCIntegerField("Age", default=users_constants.ELIGIBILITY_AGE_18)
    id_provider = fields.PCSelectField(
        "Méthode d'identification",
        choices=[
            (FraudCheckType.DMS.name, "DMS"),
            (FraudCheckType.EDUCONNECT.name, "Educonnect"),
            (FraudCheckType.UBBLE.name, "Ubble"),
        ],
        default=FraudCheckType.UBBLE.name,
    )
    step = fields.PCSelectField(
        "Étape de validation",
        choices=[(step.name, step.get_title()) for step in SubscriptionStep if step != SubscriptionStep.MAINTENANCE],
        default=SubscriptionStep.EMAIL_VALIDATION.name,
    )
    is_beneficiary = fields.PCSwitchBooleanField("Bénéficiaire", default=False)
