from pcapi.core.subscription.models import SubscriptionStep
from pcapi.core.users import constants as users_constants
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class UserGeneratorForm(utils.PCForm):
    age = fields.PCIntegerField("Age", default=users_constants.ELIGIBILITY_AGE_18)
    step = fields.PCSelectField(
        "Étape de validation",
        choices=[(step.value, step.get_title()) for step in SubscriptionStep if step != SubscriptionStep.MAINTENANCE],
        default=SubscriptionStep.EMAIL_VALIDATION.value,
        coerce=lambda value: SubscriptionStep(value) if SubscriptionStep.is_valid(value) else None,
    )
    is_beneficiary = fields.PCSwitchBooleanField("Bénéficiaire", default=False)
