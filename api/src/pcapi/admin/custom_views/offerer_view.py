from flask import flash
from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla import filters as fa_filters
from flask_admin.contrib.sqla import tools
from sqlalchemy.orm import Query
from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererTag
from pcapi.core.offerers.models import OffererTagMapping
from pcapi.core.users.external import update_external_pro
from pcapi.repository import user_offerer_queries
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


class OffererTagFilter(fa_filters.BaseSQLAFilter):
    """
    Filter offerers based on tag (offerer_tag) name.
    """

    def apply(self, query: Query, value: str, alias: str = None) -> Query:
        parsed_value = tools.parse_like_term(value)
        return query.join(OffererTagMapping).join(OffererTag).filter(OffererTag.name.ilike(parsed_value))

    def operation(self):
        return lazy_gettext("contains")

    def clean(self, value: str) -> str:
        return value.strip()


class OffererView(BaseAdminView):
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "siren", "city", "postalCode", "address", "tags"]
    column_labels = dict(
        name="Nom", siren="SIREN", city="Ville", postalCode="Code postal", address="Adresse", tags="Tags"
    )
    column_searchable_list = ["name", "siren"]
    column_filters = ["postalCode", "city", "id", "name", OffererTagFilter(Offerer.id, "Tag")]
    form_columns = ["name", "siren", "city", "postalCode", "address", "tags"]

    def delete_model(self, offerer: Offerer) -> bool:
        # Get users to update before association info is deleted
        # joined user is no longer available after delete_model()
        users_offerer = user_offerer_queries.find_all_by_offerer_id(offerer.id)
        emails = [user_offerer.user.email for user_offerer in users_offerer]

        try:
            delete_cascade_offerer_by_id(offerer.id)
        except CannotDeleteOffererWithBookingsException:
            flash("Impossible d'effacer une structure juridique pour laquelle il existe des réservations.", "error")
            return False

        for email in emails:
            update_external_pro(email)

        return True

    def update_model(self, form: Form, offerer: Offerer) -> bool:
        result = super().update_model(form, offerer)

        if result:
            for user_offerer in user_offerer_queries.find_all_by_offerer_id(offerer.id):
                update_external_pro(user_offerer.user.email)

        return result
