import logging

from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin.actions import action
from flask_admin.babel import lazy_gettext
from flask_admin.base import expose
from flask_admin.contrib.sqla import filters as fa_filters
from flask_admin.contrib.sqla import tools
from flask_admin.contrib.sqla.fields import QuerySelectMultipleField
from flask_admin.helpers import get_redirect_target
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from jinja2.runtime import Context
from markupsafe import Markup
from markupsafe import escape
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import abort
from wtforms import Form
from wtforms.fields import BooleanField
from wtforms.fields import HiddenField
from wtforms.fields import IntegerField

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core import search
from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
import pcapi.core.criteria.api as criteria_api
import pcapi.core.criteria.models as criteria_models
from pcapi.core.finance import repository as finance_repository
from pcapi.core.offerers.api import VENUE_ALGOLIA_INDEXED_FIELDS
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
import pcapi.core.offerers.repository as offerers_repository
from pcapi.core.offers.api import update_stock_id_at_providers
from pcapi.core.users.external import update_external_pro
from pcapi.core.users.external import zendesk_sell
from pcapi.models import db
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id
from pcapi.utils.mailing import build_pc_pro_offerer_link
from pcapi.utils.mailing import build_pc_pro_venue_bookings_link
from pcapi.utils.mailing import build_pc_pro_venue_link


logger = logging.getLogger(__name__)


def _format_offers_link(view: BaseAdminView, context: Context, model: Venue, name: str) -> Markup:
    url = url_for("offer_for_venue.index", id=model.id)
    return Markup('<a href="{}">Offres associées</a>').format(escape(url))


def _format_bookings_link(view: BaseAdminView, context: Context, model: Venue, name: str) -> Markup:
    url = build_pc_pro_venue_bookings_link(model)
    return Markup('<a href="{}">Réservations</a>').format(escape(url))


def _format_venue_provider(view: BaseAdminView, context: Context, model: Venue, name: str) -> Markup | None:
    if not model.venueProviders:
        return None
    url = url_for("venue_providers.index_view", id=model.id)
    return Markup('<a href="{url}">{text}</a>').format(url=url, text=model.venueProviders[0].provider.name)


def _format_venue_type_code(view: BaseAdminView, context: Context, model: Venue, name: str) -> Markup:
    return Markup("<span>{text}</span>").format(text=model.venueTypeCode.value if model.venueTypeCode else "")


def _format_venue_name(view: BaseAdminView, context: Context, model: Venue, name: str) -> Markup:
    url = build_pc_pro_venue_link(model)
    return Markup('<a href="{url}">{name}</a>').format(url=url, name=model.name)


def _format_offerer_name(view: BaseAdminView, context: Context, model: Venue, name: str) -> Markup:
    url = build_pc_pro_offerer_link(model.managingOfferer)
    return Markup('<a href="{url}">{name}</a>').format(url=url, name=model.managingOfferer.name)


class VenueChangeForm(Form):
    ids = HiddenField()
    is_permanent = BooleanField(
        label="Lieu permanent",
    )
    tags = QuerySelectMultipleField(
        get_label="name",
        query_factory=lambda: criteria_models.Criterion.query.all(),  # pylint: disable=unnecessary-lambda
        allow_blank=True,
    )
    remove_other_tags = BooleanField(
        label="Supprimer tous les autres tags",
    )


class VenueCriteriaFilter(fa_filters.BaseSQLAFilter):
    """
    Filter venues based on tag (criterion) name.
    """

    def apply(self, query: BaseQuery, value: str, alias=None) -> BaseQuery:  # type: ignore [no-untyped-def]
        parsed_value = tools.parse_like_term(value)
        return (
            query.join(criteria_models.VenueCriterion)
            .join(criteria_models.Criterion, Venue.criteria)
            .filter(criteria_models.Criterion.name.ilike(parsed_value))
        )

    def operation(self):  # type: ignore [no-untyped-def]
        return lazy_gettext("contains")

    def clean(self, value: str) -> str:
        return value.strip()


class VenueView(BaseAdminView):
    list_template = "admin/bulk_edit_components/custom_list_with_modal.html"
    can_edit = True
    can_delete = True
    column_list = [
        "id",
        "name",
        "siret",
        "city",
        "postalCode",
        "address",
        "venueTypeCode",
        "venueLabel.label",
        "criteria",
        "offres",
        "bookings",
        "publicName",
        "latitude",
        "longitude",
        "isPermanent",
        "provider_name",
        "managingOfferer.name",
        "dateCreated",
        "isActive",
        "adageId",
        "dmsToken",
    ]
    column_labels = {
        "name": "Nom",
        "siret": "SIRET",
        "city": "Ville",
        "postalCode": "Code postal",
        "address": "Adresse",
        "venueTypeCode": "Type de lieu",
        "venueLabel.label": "Label du lieu",
        "criteria": "Tag",
        "bookings": "Réservations du lieu",
        "publicName": "Nom d'usage",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "isPermanent": "Lieu permanent",
        "provider_name": "Provider",
        "managingOfferer.name": "Structure",
        "dateCreated": "Date de création",
        "isActive": "Structure active",
        "adageId": "ID Adage",
        "dmsToken": "ID DMS",
    }
    column_searchable_list = ["name", "siret", "publicName"]
    column_filters = [
        "postalCode",
        "city",
        "publicName",
        "id",
        "dmsToken",
        "managingOfferer.name",
        "venueTypeCode",
        "venueLabel.label",
        VenueCriteriaFilter(Venue.id, "Tag"),
    ]
    form_columns = [
        "name",
        "siret",
        "city",
        "postalCode",
        "address",
        "publicName",
        "latitude",
        "longitude",
        "adageId",
        "isPermanent",
        "criteria",
    ]
    form_overrides = {"adageId": IntegerField}

    def get_query(self) -> BaseQuery:
        return (
            self._extend_query(super().get_query())
            .options(joinedload(Venue.managingOfferer))
            .options(joinedload(Venue.venueProviders))
            .options(joinedload(Venue.venueLabel))
            .options(joinedload(Venue.criteria))
        )

    def get_count_query(self) -> BaseQuery:
        return self._extend_query(super().get_count_query())

    @staticmethod
    def _extend_query(query_to_override: BaseQuery) -> BaseQuery:
        venue_id = request.args.get("id")

        if venue_id:
            return query_to_override.filter(Venue.id == venue_id)

        return query_to_override

    @property
    def column_formatters(self):  # type: ignore [no-untyped-def]
        formatters = super().column_formatters
        formatters.update(
            {
                "name": _format_venue_name,
                "venueTypeCode": _format_venue_type_code,
                "provider_name": _format_venue_provider,
                "offres": _format_offers_link,
                "bookings": _format_bookings_link,
                "managingOfferer.name": _format_offerer_name,
            }
        )
        return formatters

    def delete_model(self, venue: Venue) -> bool:
        emails = offerers_repository.get_emails_by_venue(venue)
        try:
            delete_cascade_venue_by_id(venue.id)
            for email in emails:
                update_external_pro(email)
            return True
        except CannotDeleteVenueWithBookingsException:
            flash("Impossible d'effacer un lieu pour lequel il existe des réservations.", "error")
        return False

    def update_model(self, new_venue_form: Form, venue: Venue) -> bool:
        has_siret_changed = new_venue_form.siret.data != venue.siret
        if has_siret_changed:
            bu_with_same_target_siret = finance_repository.find_business_unit_by_siret(new_venue_form.siret.data)
            if bu_with_same_target_siret:
                flash(
                    f"Ce SIRET a déjà été attribué au point de remboursement {bu_with_same_target_siret.name},"
                    f" il ne peut pas être attribué à ce lieu.",
                    "error",
                )
                return False

            related_bu = finance_repository.find_business_unit_by_siret(venue.siret)  # type: ignore [arg-type]
            if related_bu:
                flash(
                    f"Le SIRET de ce lieu est le SIRET de référence du point de remboursement {related_bu.name},"
                    f" il ne peut pas être modifié.",
                    "error",
                )
                return False

        # adageId validation and cleanning
        if new_venue_form.adageId.data == "":
            new_venue_form.adageId.data = None
        if new_venue_form.adageId.data is not None and new_venue_form.adageId.data < 1:
            flash("L'adageId doit être un nombre entier supérieur ou égal à 1")
            return False

        old_siret = venue.siret

        changed_attributes = {
            field
            for field in VENUE_ALGOLIA_INDEXED_FIELDS
            if hasattr(new_venue_form, field) and getattr(new_venue_form, field).data != getattr(venue, field)
        }

        if str(new_venue_form.adageId.data) != venue.adageId:
            emails = offerers_repository.get_emails_by_venue(venue)
            for email in emails:
                update_external_pro(email)

            old_adage_id = venue.adageId or ""
            new_adage_id = new_venue_form.adageId.data or ""
            logger.info(
                '[ADMIN] User with email "%s" changed the adageId for venue "%s" (id: %s) from "%s" to "%s"',
                current_user.email,
                venue.name,
                venue.id,
                old_adage_id,
                new_adage_id,
            )

        # A failed update (invalid DB constraint for example) does not raise but returns False
        update_success = super().update_model(new_venue_form, venue)
        if not update_success:
            return False

        # Immediately index venue if tags (criteria) are involved:
        # tags are used by other tools (eg. building playlists for the
        # home page) and waiting N minutes for the next indexing
        # cron tasks is painful.
        if "criteria" in changed_attributes:
            search.reindex_venue_ids([venue.id])

            # remove criteria to avoid an unnecessary call to
            # async_index_offers_of_venue_ids: no need to update the
            # offers if the only change is the venue's tags.
            changed_attributes.remove("criteria")
        else:
            search.async_index_venue_ids([venue.id])

        if has_siret_changed and old_siret:
            update_stock_id_at_providers(venue, old_siret)

        if changed_attributes:
            search.async_index_offers_of_venue_ids([venue.id])

        # Update pro attributes for all related emails: bookingEmail (no distinct former and new because bookingEmail
        # cannot be changed from backoffice) and pro users
        for email in offerers_repository.get_emails_by_venue(venue):
            update_external_pro(email)

        zendesk_sell.update_venue(venue)

        return True

    def create_model(self, form: Form) -> Venue:
        venue = super().create_model(form)

        if venue:
            zendesk_sell.create_venue(venue)

        return venue

    @action("bulk_edit", "Édition multiple")
    def action_bulk_edit(self, ids):  # type: ignore [no-untyped-def]
        url = get_redirect_target() or self.get_url(".index_view")
        return redirect(url, code=307)

    @expose("/", methods=["POST"])
    def index(self):  # type: ignore [no-untyped-def]
        url = get_redirect_target() or self.get_url(".index_view")
        ids = request.form.getlist("rowid")
        joined_ids = ",".join(ids)
        change_form = VenueChangeForm()
        change_form.ids.data = joined_ids
        change_form.is_permanent.data = True

        criteria_in_common = (
            db.session.query(criteria_models.Criterion)
            .join(criteria_models.VenueCriterion)
            .filter(criteria_models.VenueCriterion.venueId.in_(ids))
            .group_by(criteria_models.Criterion.id)
            .having(func.count(criteria_models.VenueCriterion.criterionId) == len(ids))
            .all()
        )
        change_form.tags.data = criteria_in_common

        self._template_args["url"] = url
        self._template_args["change_form"] = change_form
        self._template_args["change_modal"] = True
        self._template_args["update_view"] = "venue.update_view"
        self._template_args["modal_title"] = f"Éditer des Lieux - {len(ids)} lieu(x) sélectionné(s)"

        return self.index_view()

    @expose("/update/", methods=["POST"])
    def update_view(self):  # type: ignore [no-untyped-def]
        url = get_redirect_target() or self.get_url(".index_view")
        change_form = VenueChangeForm(request.form)
        if change_form.validate():

            venue_ids: list[str] = change_form.ids.data.split(",")
            is_permanent: bool = change_form.is_permanent.data
            criteria: list[criteria_models.VenueCriterion] = change_form.data["tags"]
            remove_other_tags = change_form.data["remove_other_tags"]

            Venue.query.filter(Venue.id.in_(venue_ids)).update(
                values={"isPermanent": is_permanent}, synchronize_session=False
            )

            criteria_ids = [crit.id for crit in criteria]
            criteria_api.VenueUpdate(venue_ids, criteria_ids, replace_tags=remove_other_tags).run()

            db.session.commit()
            return redirect(url)

        # Form didn't validate
        flash("Le formulaire est invalide: %s" % (change_form.errors), "error")
        return redirect(url, code=307)


class VenueForOffererSubview(VenueView):
    column_searchable_list = ["name", "criteria.name", "siret", "city", "postalCode", "publicName"]
    list_template = "admin/offerer_venues_list.html"

    @expose("/", methods=(["GET", "POST"]))
    def index(self):  # type: ignore [no-untyped-def]
        if request.method == "POST":
            return super().index()
        self._template_args["offerer_name"] = self._get_offerer_name()
        return super().index_view()

    def is_visible(self) -> bool:
        return False

    def get_query(self) -> BaseQuery:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> BaseQuery:
        return self._extend_query(super().get_count_query())

    def _extend_query(self, query_to_override: BaseQuery) -> BaseQuery:  # type: ignore [override]
        offerer_id = request.args.get("id")

        if offerer_id is None:
            abort(400, "Offerer id required")

        return query_to_override.filter(Venue.managingOffererId == offerer_id)

    def _get_offerer_name(self) -> str:
        offerer_id = request.args.get("id")

        if offerer_id is None:
            abort(400, "Offerer id required")

        offerer = Offerer.query.filter(Offerer.id == offerer_id).one()
        if not offerer:
            abort(404, "Cette structure n'existe pas ou plus")

        return offerer.name
