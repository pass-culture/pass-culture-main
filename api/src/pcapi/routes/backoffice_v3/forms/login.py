from wtforms import validators

from . import fields
from . import utils


class GetLoginRedirectForm(utils.PCForm):
    class Meta:
        csrf = False

    redirect = fields.PCStringField(
        "redirect",
        validators=[
            validators.Length(max=1500),
        ],
    )
