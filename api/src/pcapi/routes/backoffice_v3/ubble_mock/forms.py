from pcapi.core.fraud import models as fraud_models
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class UbbleResponseForm(utils.PCForm):
    user_id = fields.PCIntegerField("ID de l'utilisateur")
    status = fields.PCSelectField(
        "Status de la réponse",
        choices=[
            (fraud_models.FraudCheckStatus.OK.name, "OK"),
            (fraud_models.FraudCheckStatus.KO.name, "KO"),
            (fraud_models.FraudCheckStatus.SUSPICIOUS.name, "SUSPICIOUS"),
        ],
        default=fraud_models.FraudCheckStatus.OK.name,
    )
