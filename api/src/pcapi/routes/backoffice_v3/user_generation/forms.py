from pcapi.core.users import constants as users_constants
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class UserGeneratorForm(utils.PCForm):
    age = fields.PCIntegerField("Age", default=users_constants.ELIGIBILITY_AGE_18)
    is_email_validated = fields.PCSwitchBooleanField("Email validé", default=True)
    is_beneficiary = fields.PCSwitchBooleanField("Bénéficiaire", default=False)
