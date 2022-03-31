from flask import flash
from flask import url_for
from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla import filters as fa_filters
from flask_admin.contrib.sqla import tools
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
from markupsafe import escape
from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
from pcapi.core.bookings.repository import offerer_has_ongoing_bookings
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererTag
from pcapi.core.offerers.models import OffererTagMapping
import pcapi.core.offerers.repository as offerers_repository
from pcapi.core.users.external import update_external_pro
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


def _get_emails_by_offerer(offerer: Offerer) -> set[str]:
    """
    Get all emails for which pro attributes may be modified when the offerer is updated or deleted.
    Any bookingEmail in a venue should be updated in sendinblue when offerer is disabled, deleted or its name changed
    """
    users_offerer = offerers_repository.find_all_user_offerers_by_offerer_id(offerer.id)
    emails = {user_offerer.user.email for user_offerer in users_offerer}

    emails |= {venue.bookingEmail for venue in offerers_repository.find_venues_by_managing_offerer_id(offerer.id)}

    return emails


def _venues_link(view, context, model, name) -> Markup:
    url = url_for("venue_for_offerer.index", id=model.id)
    return Markup('<a href="{}">Lieux associés</a>').format(escape(url))


class OffererTagFilter(fa_filters.BaseSQLAFilter):
    """
    Filter offerers based on tag (offerer_tag) name.
    """

    def apply(self, query: BaseQuery, value: str, alias: str = None) -> BaseQuery:
        parsed_value = tools.parse_like_term(value)
        return query.join(OffererTagMapping).join(OffererTag).filter(OffererTag.name.ilike(parsed_value))

    def operation(self):
        return lazy_gettext("contains")

    def clean(self, value: str) -> str:
        return value.strip()


class OffererView(BaseAdminView):
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "siren", "city", "postalCode", "address", "tags", "venues", "isActive"]
    column_labels = dict(
        name="Nom",
        siren="SIREN",
        city="Ville",
        postalCode="Code postal",
        address="Adresse",
        tags="Tags",
        venues="Lieux",
        isActive="Active",
    )
    column_searchable_list = ["name", "siren"]
    column_filters = ["postalCode", "city", "id", "name", OffererTagFilter(Offerer.id, "Tag"), "isActive"]
    form_columns = ["name", "siren", "city", "postalCode", "address", "tags", "isActive"]

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(venues=_venues_link)
        return formatters

    def delete_model(self, offerer: Offerer) -> bool:
        # Get users to update before association info is deleted
        # joined user is no longer available after delete_model()
        emails = _get_emails_by_offerer(offerer)

        try:
            delete_cascade_offerer_by_id(offerer.id)
        except CannotDeleteOffererWithBookingsException:
            flash("Impossible d'effacer une structure juridique pour laquelle il existe des réservations.", "error")
            return False

        for email in emails:
            update_external_pro(email)

        return True

    def update_model(self, form: Form, offerer: Offerer) -> bool:
        if offerer.isActive and not form.isActive.data:
            if offerer_has_ongoing_bookings(offerer.id):
                flash(
                    "Impossible de désactiver une structure juridique pour laquelle des réservations sont en cours.",
                    "error",
                )
                return False

        result = super().update_model(form, offerer)

        if result:
            for email in _get_emails_by_offerer(offerer):
                update_external_pro(email)

        return result
