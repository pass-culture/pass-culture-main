from flask import flash
from flask import url_for
from flask_admin.babel import lazy_gettext
from flask_admin.contrib.sqla import filters as fa_filters
from flask_admin.contrib.sqla import tools
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from jinja2.runtime import Context
from markupsafe import Markup
from markupsafe import escape
from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.bookings.repository import offerer_has_ongoing_bookings
from pcapi.core.external import zendesk_sell
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.exceptions as offerers_exceptions
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import OffererTag
import pcapi.core.offerers.repository as offerers_repository
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils.urls import build_pc_pro_offerer_link


def _format_offerer_name(view: BaseAdminView, context: Context, model: Offerer, name: str) -> Markup:
    url = build_pc_pro_offerer_link(model)
    return Markup('<a href="{url}">{name}</a>').format(url=url, name=model.name)


def _format_venues_link(view: BaseAdminView, context: Context, model: Offerer, name: str) -> Markup:
    url = url_for("venue_for_offerer.index", id=model.id)
    return Markup('<a href="{}">Lieux associés</a>').format(escape(url))


def _format_validation_status(view: BaseAdminView, context: Context, model: Offerer, name: str) -> Markup:
    match model.validationStatus:
        case ValidationStatus.NEW:
            text = "Nouvelle structure"
        case ValidationStatus.PENDING:
            text = "En attente"
        case ValidationStatus.VALIDATED:
            text = "Validée"
        case ValidationStatus.REJECTED:
            text = "Rejetée"
        case _:  # this case should not happen
            text = str(model.validationStatus)
    return Markup("<span>{text}</span>").format(text=text)


class OffererTagFilter(fa_filters.BaseSQLAFilter):
    """
    Filter offerers based on tag (offerer_tag) name.
    """

    def apply(self, query: BaseQuery, value: str, alias: str = None) -> BaseQuery:
        parsed_value = tools.parse_like_term(value)
        return query.join(OffererTag, Offerer.tags).filter(OffererTag.name.ilike(parsed_value))

    def operation(self):  # type: ignore [no-untyped-def]
        return lazy_gettext("contains")

    def clean(self, value: str) -> str:
        return value.strip()


class OffererView(BaseAdminView):
    can_edit = True
    can_delete = True
    column_list = [
        "id",
        "name",
        "siren",
        "city",
        "postalCode",
        "address",
        "tags",
        "venues",
        "validationStatus",
        "isActive",
    ]
    column_labels = dict(
        name="Nom",
        siren="SIREN",
        city="Ville",
        postalCode="Code postal",
        address="Adresse",
        tags="Tags",
        venues="Lieux",
        validationStatus="État de validation",
        isActive="Active",
    )
    column_searchable_list = ["name", "siren"]
    column_filters = [
        "postalCode",
        "city",
        "id",
        "name",
        OffererTagFilter(Offerer.id, "Tag"),
        "validationStatus",
        "isActive",
    ]
    form_columns = ["name", "siren", "city", "postalCode", "address", "tags", "isActive"]

    @property
    def column_formatters(self):  # type: ignore [no-untyped-def]
        formatters = super().column_formatters
        formatters.update(
            name=_format_offerer_name, venues=_format_venues_link, validationStatus=_format_validation_status
        )
        return formatters

    def delete_model(self, offerer: Offerer) -> bool:
        # Get users to update before association info is deleted
        # joined user is no longer available after delete_model()
        emails = offerers_repository.get_emails_by_offerer(offerer)

        try:
            offerers_api.delete_offerer(offerer.id)
        except offerers_exceptions.CannotDeleteOffererWithBookingsException:
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

            history_api.log_action(history_models.ActionType.OFFERER_SUSPENDED, current_user, offerer=offerer)

        elif not offerer.isActive and form.isActive.data:
            history_api.log_action(history_models.ActionType.OFFERER_UNSUSPENDED, current_user, offerer=offerer)

        result = super().update_model(form, offerer)

        if result:
            for email in offerers_repository.get_emails_by_offerer(offerer):
                update_external_pro(email)

            zendesk_sell.update_offerer(offerer)

        return result

    def create_model(self, form: Form) -> Offerer:
        offerer = super().create_model(form)

        if offerer:
            zendesk_sell.create_offerer(offerer)

        return offerer
