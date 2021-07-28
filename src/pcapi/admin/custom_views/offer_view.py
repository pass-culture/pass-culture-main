from datetime import datetime
import logging
from typing import Union

from flask import abort
from flask import flash
from flask import has_app_context
from flask import redirect
from flask import request
from flask import url_for
from flask_admin.actions import action
from flask_admin.base import expose
from flask_admin.contrib.sqla.filters import FilterEqual
from flask_admin.form import SecureForm
from flask_admin.helpers import get_form_data
from flask_admin.helpers import is_form_submitted
from flask_login import current_user
from markupsafe import Markup
from markupsafe import escape
from sqlalchemy import func
from sqlalchemy.orm import query
from werkzeug import Response
import wtforms
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError
import yaml

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors.api_entreprises import get_offerer_legal_category
from pcapi.core import search
from pcapi.core.bookings.api import cancel_bookings_from_rejected_offer
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api as offers_api
from pcapi.core.offers.api import import_offer_validation_config
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.offer_validation import compute_offer_validation_score
from pcapi.core.offers.offer_validation import parse_offer_validation_config
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.validation import check_user_can_load_config
from pcapi.domain.admin_emails import send_offer_validation_notification_to_administration
from pcapi.domain.user_emails import send_offer_validation_status_update_email
from pcapi.models import Offer
from pcapi.repository import repository
from pcapi.settings import IS_PROD
from pcapi.utils.human_ids import humanize
from pcapi.workers.push_notification_job import send_cancel_booking_notification


logger = logging.getLogger(__name__)


def offer_category_formatter(view, context, model, name) -> str:
    if model.subcategoryId is None:
        return ""
    return subcategories.ALL_SUBCATEGORIES_DICT[model.subcategoryId].category_id


class ExtraDataFilterEqual(FilterEqual):
    def get_column(self, alias: str) -> str:
        return super().get_column(alias).astext


class OfferView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    can_export = True
    column_list = [
        "id",
        "name",
        "type",
        "subcategoryId",
        "categoryId",
        "criteria",
        "rankingWeight",
        "validation",
        "lastValidationDate",
        "isEducational",
    ]
    column_sortable_list = ["name", "type", "criteria", "rankingWeight", "validation", "lastValidationDate"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "subcategoryId": "Sous-catégorie",
        "categoryId": "Catégorie",
        "criteria": "Tag",
        "criteria.name": "Tag",
        "rankingWeight": "Pondération",
        "lastValidationDate": "Dernière date de validation",
        "isEducational": "Offre EAC",
    }
    # Do not add searchable column on offer view for performance reasons
    # use the filters feature instead
    column_filters = [
        "id",
        "type",
        "subcategoryId",
        "criteria.name",
        "name",
        "rankingWeight",
        "validation",
        "lastValidationDate",
        "isEducational",
        ExtraDataFilterEqual(column=Offer.extraData["isbn"], name="ISBN"),
        ExtraDataFilterEqual(column=Offer.extraData["visa"], name="Visa d'exploitation"),
        ExtraDataFilterEqual(column=Offer.extraData["theater"]["allocine_room_id"], name="Identifiant Allociné"),
    ]
    form_columns = ["criteria", "rankingWeight", "isEducational"]
    simple_list_pager = True

    def get_edit_form(self) -> wtforms.Form:
        form = super().get_form()
        form.name = wtforms.StringField(
            "Nom de l'offre",
            render_kw={"readonly": True},
        )
        if has_app_context() and self.check_super_admins():
            form.validation = wtforms.SelectField(
                "Validation",
                choices=[(s.name, s.value) for s in OfferValidationStatus],
                coerce=str,
                description="Vous pouvez choisir uniquement APPROVED ou REJECTED",
            )
        return form

    @property
    def column_formatters(self):
        formatters = super().column_formatters.copy()
        formatters.update(
            {
                "categoryId": offer_category_formatter,
            }
        )
        return formatters

    def on_form_prefill(self, form, id):  # pylint:disable=redefined-builtin
        if hasattr(form, "validation"):
            current_offer = self.session.query(self.model).get(id)
            form.validation.data = current_offer.validation.value

    def on_model_change(self, form: wtforms.Form, model: Offer, is_created: bool) -> None:
        if hasattr(form, "validation"):
            previous_validation = form._fields["validation"].object_data
            new_validation = OfferValidationStatus[form.validation.data]
            if previous_validation != new_validation and new_validation in (
                OfferValidationStatus.DRAFT,
                OfferValidationStatus.PENDING,
            ):
                raise ValidationError("Le statut de validation ne peut pas être changé vers DRAFT ou PENDING")

    def after_model_change(self, form: wtforms.Form, offer: Offer, is_created: bool = False) -> None:
        if hasattr(form, "validation"):
            previous_validation = form._fields["validation"].object_data
            new_validation = offer.validation
            if previous_validation != new_validation:
                offer.lastValidationDate = datetime.utcnow()
                if new_validation == OfferValidationStatus.APPROVED:
                    offer.isActive = True
                if new_validation == OfferValidationStatus.REJECTED:
                    offer.isActive = False
                    cancelled_bookings = cancel_bookings_from_rejected_offer(offer)
                    if cancelled_bookings:
                        send_cancel_booking_notification.delay([booking.id for booking in cancelled_bookings])

                repository.save(offer)

                recipients = (
                    [offer.venue.bookingEmail]
                    if offer.venue.bookingEmail
                    else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
                )
                send_offer_validation_status_update_email(offer, new_validation, recipients)
                send_offer_validation_notification_to_administration(new_validation, offer)

                flash("Le statut de l'offre a bien été modifié", "success")

        search.async_index_offer_ids([offer.id])

    def get_query(self) -> query:
        return self.session.query(self.model).filter(Offer.validation != OfferValidationStatus.DRAFT).from_self()


class OfferForVenueSubview(OfferView):
    column_searchable_list = ["name", "criteria.name"]
    list_template = "admin/venue_offers_list.html"

    @expose("/", methods=(["GET"]))
    def index(self):
        self._template_args["venue_name"] = self._get_venue_name()
        return super().index_view()

    def is_visible(self) -> bool:
        return False

    def get_query(self) -> query:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> query:
        return self._extend_query(super().get_count_query())

    def _extend_query(self, query_to_override: query) -> query:
        venue_id = request.args.get("id")

        if venue_id is None:
            abort(400, "Venue id required")

        return query_to_override.filter(Offer.venueId == venue_id)

    def _get_venue_name(self) -> str:
        venue_id = request.args.get("id")

        if venue_id is None:
            abort(400, "Venue id required")

        venue = Venue.query.filter(Venue.id == venue_id).one()
        if not venue:
            abort(404, "Ce lieu n'existe pas ou plus")

        return venue.name


def _pro_offer_url(offer_id: int) -> str:
    return f"{settings.PRO_URL}/offres/{humanize(offer_id)}/edition"


def _metabase_offer_url(offer_id: int) -> str:
    return f"https://support.internal-passculture.app/question/115?offer_id={offer_id}"


def _venue_url(venue: Venue) -> str:
    offerer_id = venue.managingOfferer.id
    venue_id = venue.id
    if venue.isVirtual:
        return f"{settings.PRO_URL}/accueil?structure={humanize(offerer_id)}"
    return f"{settings.PRO_URL}/structures/{humanize(offerer_id)}/lieux/{humanize(venue_id)}"


def _offerer_url(offerer_id: int) -> str:
    return f"{settings.PRO_URL}/accueil?structure={humanize(offerer_id)}"


def _pro_offer_link(view, context, model, name) -> Markup:
    url = _pro_offer_url(model.id)
    return Markup('<a href="{}" target="_blank" rel="noopener noreferrer">Offre PC</a>').format(escape(url))


def _related_offers_link(view, context, model, name) -> Markup:
    url = url_for("offer_for_venue.index", id=model.venue.id)
    return Markup('<a href="{}">Offres associées</a>').format(escape(url))


def _metabase_offer_link(view, context, model, name) -> Markup:
    url = _metabase_offer_url(model.id)
    return Markup('<a href="{}" target="_blank" rel="noopener noreferrer">Offre</a>').format(escape(url))


def _offerer_link(view, context, model, name) -> Markup:
    url = _offerer_url(model.venue.managingOffererId)
    link = Markup('<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>')
    return link.format(url=escape(url), name=escape(model.venue.managingOfferer.name))


def _venue_link(view, context, model, name) -> Markup:
    url = _venue_url(model.venue)
    link = Markup('<a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>')
    return link.format(url=escape(url), name=escape(model.venue.publicName or model.venue.name))


def _compute_score(view, context, model, name) -> float:
    current_config = offers_repository.get_current_offer_validation_config()
    validation_items = parse_offer_validation_config(model, current_config)[1]
    return compute_offer_validation_score(validation_items)


class OfferValidationForm(SecureForm):
    validation = wtforms.SelectField(
        "validation",
        choices=[(choice.name, choice.value) for choice in OfferValidationStatus if choice.name != "DRAFT"],
        coerce=str,
    )


class ValidationView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    list_template = "admin/offer_validation_list.html"

    column_list = ["id", "name", "validation", "venue", "offerer", "score", "offer", "offers", "dateCreated"]
    if IS_PROD:
        column_list.append("metabase")
    column_sortable_list = ["id", "name", "validation", "dateCreated"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "validation": "Validation",
        "venue": "Lieu",
        "offerer": "Structure",
        "offer": "Offre",
        "offers": "Offres",
        "score": "Score",
        "metabase": "Metabase",
        "dateCreated": "Date de création",
    }
    column_filters = ["name", "venue.name", "id", "dateCreated"]
    column_default_sort = ("id", True)
    page_size = 100

    def is_accessible(self):
        return super().is_accessible() and self.check_super_admins()

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(score=_compute_score)
        formatters.update(offer=_pro_offer_link)
        formatters.update(offers=_related_offers_link)
        formatters.update(metabase=_metabase_offer_link)
        formatters.update(offerer=_offerer_link)
        formatters.update(venue=_venue_link)
        return formatters

    def get_query(self):
        return self.session.query(self.model).filter(self.model.validation == OfferValidationStatus.PENDING)

    def get_count_query(self):
        return self.session.query(func.count("*")).filter(self.model.validation == OfferValidationStatus.PENDING)

    def _batch_validate(self, offers, validation_status):
        count = 0
        not_updated_offers = []
        for offer in offers:
            try:
                is_offer_updated = offers_api.update_pending_offer_validation(offer, validation_status)
                if is_offer_updated:
                    count += 1
                    offer.lastValidationDate = datetime.utcnow()
                    recipients = (
                        [offer.venue.bookingEmail]
                        if offer.venue.bookingEmail
                        else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
                    )
                    send_offer_validation_status_update_email(offer, validation_status, recipients)
                    send_offer_validation_notification_to_administration(validation_status, offer)
                else:
                    not_updated_offers += offer
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception(
                    "Une erreur s'est produite lors de la mise à jour du statut de validation: %s",
                    exc,
                    extra={"offer": offer},
                )
        flash("%d offres ont été modifiées avec succès en %s" % (count, validation_status))
        if not_updated_offers:
            flash(
                "Une erreur s'est produite lors de la mise à jour du statut de validation des offres: %s"
                % not_updated_offers,
                "error",
            )

    @action("approve", "Approuver", "Etes-vous sûr(e) de vouloir approuver les offres sélectionnées ?")
    def action_approve(self, ids):
        offers_to_approve = Offer.query.filter(Offer.id.in_(ids))
        self._batch_validate(offers_to_approve, OfferValidationStatus.APPROVED)

    @action("reject", "Rejeter", "Etes-vous sûr(e) de vouloir rejeter les offres sélectionnées ?")
    def action_reject(self, ids):
        offers_to_reject = Offer.query.filter(Offer.id.in_(ids))
        self._batch_validate(offers_to_reject, OfferValidationStatus.REJECTED)

    @expose("/edit/", methods=["GET", "POST"])
    def edit(self) -> Response:
        offer_id = request.args["id"]
        offer = Offer.query.get(offer_id)
        form = OfferValidationForm()
        if request.method == "POST":
            form = OfferValidationForm(request.form)
            if form.validate():
                validation_status = OfferValidationStatus[form.validation.data]
                is_offer_updated = offers_api.update_pending_offer_validation(
                    offer, OfferValidationStatus[form.validation.data]
                )
                if is_offer_updated:
                    flash("Le statut de l'offre a bien été modifié", "success")
                    offer.lastValidationDate = datetime.utcnow()
                    recipients = (
                        [offer.venue.bookingEmail]
                        if offer.venue.bookingEmail
                        else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
                    )

                    send_offer_validation_status_update_email(offer, validation_status, recipients)
                    send_offer_validation_notification_to_administration(validation_status, offer)
                    if request.form["action"] == "save-and-go-next":
                        next_offer_query = (
                            Offer.query.filter(Offer.validation == OfferValidationStatus.PENDING)
                            .filter(Offer.id < offer_id)
                            .order_by(Offer.id.desc())
                            .limit(1)
                        )
                        if next_offer_query.count() > 0:
                            next_offer = next_offer_query.one()
                            return redirect(url_for(".edit", id=next_offer.id))
                        return redirect(url_for("/validation.index_view"))
                    if request.form["action"] == "save":
                        return redirect(url_for("/validation.index_view"))
                else:
                    flash("Une erreur s'est produite lors de la mise à jour du statut de validation", "error")

        form.validation.default = offer.validation.value
        form.process()
        legal_category = get_offerer_legal_category(offer.venue.managingOfferer)
        legal_category_code = legal_category["legal_category_code"] or "Ce lieu n'a pas de code de catégorie juridique"
        legal_category_label = (
            legal_category["legal_category_label"] or "Ce lieu n'a pas de libellé de catégorie juridique"
        )
        current_config = offers_repository.get_current_offer_validation_config()
        validation_items = parse_offer_validation_config(offer, current_config)[1]
        context = {
            "form": form,
            "cancel_link_url": url_for("/validation.index_view"),
            "legal_category_code": legal_category_code,
            "legal_category_label": legal_category_label,
            "pc_offer_url": _pro_offer_url(offer.id),
            "metabase_offer_url": _metabase_offer_url(offer.id) if IS_PROD else None,
            "offer_name": offer.name,
            "offer_score": compute_offer_validation_score(validation_items),
            "venue_name": offer.venue.publicName or offer.venue.name,
            "offerer_name": offer.venue.managingOfferer.name,
            "venue_url": _venue_url(offer.venue),
            "offerer_url": _offerer_url(offer.venue.managingOfferer.id),
        }
        return self.render("admin/edit_offer_validation.html", **context)


def yaml_formatter(view, context, model, name) -> Markup:
    value = getattr(model, name)
    yaml_value = yaml.dump(value, indent=4)
    return Markup("<pre>{}</pre>".format(yaml_value))


def user_formatter(view, context, model, name) -> str:
    author = getattr(model, name)
    return author.email if author else ""


def date_formatter(view, context, model, name) -> datetime:
    config_date = getattr(model, name)
    return config_date.strftime("%Y-%m-%d %H:%M:%S")


class OfferValidationConfigForm(SecureForm):
    specs = wtforms.TextAreaField("Configuration", [InputRequired()])


class ImportConfigValidationOfferView(BaseAdminView):
    can_create = True
    can_edit = False
    can_view_details = True
    can_delete = False
    column_list = ["id", "dateCreated", "userId", "user"]
    column_sortable_list = ["id", "dateCreated"]
    column_labels = {
        "id": "Id",
        "dateCreated": "Date de création",
        "userId": "ID Utilisateur",
        "user": "Utilisateur",
    }

    column_default_sort = ("dateCreated", True)

    column_formatters = {
        "specs": yaml_formatter,
        "user": user_formatter,
        "dateCreated": date_formatter,
    }

    form_excluded_columns = ("id", "dateCreated", "userId", "user")
    form_widget_args = {"specs": {"rows": 40, "style": "color: black"}}

    def create_form(self, obj=None):
        if not is_form_submitted():
            current_config = offers_repository.get_current_offer_validation_config()
            if current_config:
                form = OfferValidationConfigForm()
                form.specs.data = yaml.dump(current_config.specs, indent=4, allow_unicode=True)
                return form

        return OfferValidationConfigForm(get_form_data())

    def create_model(self, form: wtforms.Form) -> Union[None, OfferValidationConfig]:
        check_user_can_load_config(current_user)
        config = import_offer_validation_config(form.specs.data, current_user)
        return config
