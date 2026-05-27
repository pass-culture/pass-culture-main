from wtforms import validators

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class AnalyticsRegisterForm(utils.PCForm):
    class Meta:
        csrf = False

    name = fields.PCStringField()
    type = fields.PCStringField()
    origin = fields.PCStringField(
        validators=[
            validators.DataRequired(""),
            validators.Length(min=1, max=512),
        ]
    )
