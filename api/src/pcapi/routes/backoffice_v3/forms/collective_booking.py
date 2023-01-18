from flask_wtf import FlaskForm
import wtforms

from . import fields


class GetCollectiveBookingListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID réservation collective")
    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = wtforms.HiddenField("Par page", default="100", validators=(wtforms.validators.Optional(),))

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            q.data = q.data.strip()
            if not q.data.isnumeric():
                raise wtforms.validators.ValidationError("Le format de l'ID de réservation est incorrect")
        return q
