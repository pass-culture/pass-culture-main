from flask import abort
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin.base import expose
from flask_admin.form import SecureForm
from markupsafe import Markup
from sqlalchemy import func
from sqlalchemy.orm import query
from werkzeug import Response
from wtforms import Form
from wtforms import SelectField

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors import redis
from pcapi.connectors.api_entreprises import get_offerer_legal_category
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.api import update_pending_offer_validation_status
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.domain.user_emails import send_offer_validation_status_update_email
from pcapi.flask_app import app
from pcapi.models import Offer
from pcapi.settings import IS_PROD
from pcapi.utils.human_ids import humanize


class OfferView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ["id", "name", "type", "criteria", "validation"]
    column_sortable_list = ["name", "type", "criteria", "validation"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "criteria": "Tag",
        "criteria.name": "Tag",
    }
    # Do not add searchable column on offer view for performance reasons
    # use the filters feature instead
    column_filters = ["type", "criteria.name", "name", "validation"]
    form_columns = ["criteria"]
    simple_list_pager = True

    def on_model_change(self, form: Form, offer: Offer, is_created: bool = False) -> None:
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)


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
    return f"https://data-analytics.internal-passculture.app/question/901?offerid={offer_id}"


def _pro_offer_link(view, context, model, name) -> Markup:
    url = _pro_offer_url(model.id)
    text = "Offre PC"

    return Markup(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>')


def _related_offers_link(view, context, model, name) -> Markup:
    url = url_for("offer_for_venue.index", id=model.venue.id)
    text = "Offres associées"

    return Markup(f'<a href="{url}">{text}</a>')


def _metabase_offer_link(view, context, model, name) -> Markup:
    url = _metabase_offer_url(model.id)
    text = "Offre"

    return Markup(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>')


class OfferValidationForm(SecureForm):
    validation = SelectField(
        "validation", choices=[(choice.name, choice.value) for choice in OfferValidationStatus], coerce=str
    )


class ValidationView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ["id", "name", "validation", "venue.name", "score", "offer", "offers"]
    if IS_PROD:
        column_list.append("metabase")
    column_sortable_list = ["id", "name", "validation"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "validation": "Validation",
        "venue.name": "Lieu",
        "offer": "Offre",
        "offers": "Offres",
        "score": "Score",
        "metabase": "Metabase",
    }
    column_filters = ["type"]
    simple_list_pager = True

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(offer=_pro_offer_link)
        formatters.update(offers=_related_offers_link)
        formatters.update(metabase=_metabase_offer_link)
        return formatters

    def get_query(self):
        return self.session.query(self.model).filter(self.model.validation == OfferValidationStatus.PENDING)

    def get_count_query(self):
        return self.session.query(func.count("*")).filter(self.model.validation == OfferValidationStatus.PENDING)

    @expose("/edit/", methods=["GET", "POST"])
    def edit(self) -> Response:
        offer_id = request.args["id"]
        offer = Offer.query.get(offer_id)
        form = OfferValidationForm()
        if request.method == "POST":
            form = OfferValidationForm(request.form)
            if form.validate():
                validation_status = OfferValidationStatus[form.validation.data]
                is_offer_updated = update_pending_offer_validation_status(
                    offer, OfferValidationStatus[form.validation.data]
                )
                if is_offer_updated:
                    flash("Le statut de l'offre a bien été modifié", "success")

                    recipients = (
                        [offer.venue.bookingEmail]
                        if offer.venue.bookingEmail
                        else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
                    )

                    send_offer_validation_status_update_email(offer, validation_status, recipients)
                    if request.form["action"] == "save-and-go-next":
                        next_offer_query = (
                            Offer.query.filter(Offer.validation == OfferValidationStatus.PENDING)
                            .filter(Offer.id != offer_id)
                            .limit(1)
                        )
                        if next_offer_query.count() > 0:
                            next_offer = next_offer_query.one()
                            return redirect(url_for(".edit", id=next_offer.id))
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
        context = {
            "form": form,
            "cancel_link_url": url_for("/validation.index_view"),
            "legal_category_code": legal_category_code,
            "legal_category_label": legal_category_label,
            "pc_offer_url": _pro_offer_url(offer.id),
            "metabase_offer_url": _metabase_offer_url(offer.id) if IS_PROD else None,
            "offer_name": offer.name,
        }
        return self.render("admin/edit_offer_validation.html", **context)
