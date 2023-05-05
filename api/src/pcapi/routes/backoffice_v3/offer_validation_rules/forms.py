from flask_wtf import FlaskForm

from pcapi.routes.backoffice_v3.forms import fields


class SearchRuleForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom de la règle")

    def is_empty(self) -> bool:
        return not any((self.q.data,))
