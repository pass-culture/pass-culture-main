from typing import List

from wtforms.validators import DataRequired

from pcapi.admin.base_configuration import BaseAdminView


class UserOffererView(BaseAdminView):
    can_edit = True
    can_delete = True
    column_list = [
        "user.email",
        "user.firstName",
        "user.lastName",
        "user.id",
        "offerer.siren",
        "offerer.address",
        "offerer.name",
        "offerer.id",
        "rights",
    ]
    column_labels = {
        "user.email": "Email utilisateur",
        "user.firstName": "Prénom de l'utilisateur",
        "user.lastName": "Nom de l'utilisateur",
        "user.id": "Identifiant de l'utilisateur",
        "offerer.siren": "SIREN de la structure",
        "offerer.address": "Adresse de la structure",
        "offerer.name": "Nom de la structure",
        "offerer.id": "Identifiant de la structure",
        "rights": "Statut de l'utilisateur sur la structure",
    }
    column_sortable_list: List[str] = []
    column_searchable_list = [
        "user.email",
        "user.firstName",
        "user.lastName",
        "user.id",
        "offerer.siren",
        "offerer.address",
        "offerer.name",
        "offerer.id",
        "rights",
    ]
    column_filters = [
        "user.email",
        "user.firstName",
        "user.lastName",
        "offerer.siren",
        "offerer.address",
        "offerer.name",
        "rights",
    ]
    form_columns = ["rights"]
    form_args = dict(rights=dict(label="Statut de l'utilisateur sur la structure", validators=[DataRequired()]))
