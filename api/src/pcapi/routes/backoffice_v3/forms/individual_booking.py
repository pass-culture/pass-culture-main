import re

from flask_wtf import FlaskForm
import wtforms

from . import fields


BOOKING_TOKEN_RE = re.compile(r"^[\dA-Z]{6}$")


class GetIndividualBookingListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Code contremarque")
    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = wtforms.HiddenField("Par page", default="100", validators=(wtforms.validators.Optional(),))

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            q.data = q.data.strip()
            if not BOOKING_TOKEN_RE.match(q.data):
                raise wtforms.validators.ValidationError("Le format de la contremarque est incorrect")
        return q
