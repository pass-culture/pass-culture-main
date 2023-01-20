from flask_wtf import FlaskForm

from . import fields


class GetOffersListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Id de l'offre, nom")
