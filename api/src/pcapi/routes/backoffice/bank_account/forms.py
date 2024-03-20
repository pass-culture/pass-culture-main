from wtforms import validators

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class EditBankAccountForm(utils.PCForm):
    label = fields.PCStringField(
        "Intitulé du compte bancaire",
        validators=[
            validators.DataRequired("Information obligatoire"),
            validators.Length(min=1, max=64, message="doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
