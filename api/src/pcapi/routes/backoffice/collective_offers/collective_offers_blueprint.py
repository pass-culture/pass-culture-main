import datetime
import re
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from markupsafe import escape
import sqlalchemy as sa
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import NotFound

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.collective_offers import forms
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils import regions as regions_utils


blueprint = utils.child_backoffice_blueprint(
    "collective_offer",
    __name__,
    url_prefix="/pro/collective-offer",
    permission=perm_models.Permissions.READ_OFFERS,
)


aliased_stock = sa.orm.aliased(educational_models.CollectiveStock)

SEARCH_FIELD_TO_PYTHON = {
    "FORMATS": {
        "field": "formats",
        "column": educational_models.CollectiveOffer.formats,
    },
    "INSTITUTION": {
        "field": "institution",
        "column": educational_models.CollectiveOffer.institutionId,
    },
    "CREATION_DATE": {
        "field": "date",
        "column": educational_models.CollectiveOffer.dateCreated,
    },
    "DEPARTMENT": {
        "field": "department",
        "column": offerers_models.Venue.departementCode,
        "inner_join": "venue",
    },
    "REGION": {
        "field": "region",
        "column": offerers_models.Venue.departementCode,
        "inner_join": "venue",
        "special": regions_utils.get_department_codes_for_regions,
    },
    "EVENT_DATE": {
        "field": "date",
        "column": aliased_stock.beginningDatetime,
        "inner_join": "stock",
    },
    "BOOKING_LIMIT_DATE": {
        "field": "date",
        "column": aliased_stock.bookingLimitDatetime,
        "inner_join": "stock",
    },
    "ID": {
        "field": "string",
        "column": educational_models.CollectiveOffer.id,
        "special": lambda q: [int(id_) for id_ in re.findall(r"\d+", q or "")],
    },
    "NAME": {
        "field": "string",
        "column": educational_models.CollectiveOffer.name,
    },
    "OFFERER": {
        "field": "offerer",
        "column": offerers_models.Venue.managingOffererId,
        "inner_join": "venue",
    },
    "STATUS": {
        "field": "status",
        "column": educational_models.CollectiveOffer.status,
    },
    "VENUE": {
        "field": "venue",
        "column": educational_models.CollectiveOffer.venueId,
    },
    "VALIDATION": {"field": "validation", "column": educational_models.CollectiveOffer.validation},
    "PRICE": {
        "field": "price",
        "column": aliased_stock.price,
        "inner_join": "stock",
    },
}

JOIN_DICT: dict[str, list[dict[str, typing.Any]]] = {
    "stock": [
        {
            "name": "stock",
            "args": (
                aliased_stock,
                educational_models.CollectiveOffer.collectiveStock,
            ),
        }
    ],
    "venue": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, educational_models.CollectiveOffer.venue),
        }
    ],
}


def _get_collective_offer_ids_query(form: forms.GetCollectiveOfferAdvancedSearchForm) -> BaseQuery:
    base_query, inner_joins, _, warnings = utils.generate_search_query(
        query=educational_models.CollectiveOffer.query,
        search_parameters=form.search.data,
        fields_definition=SEARCH_FIELD_TO_PYTHON,
        joins_definition=JOIN_DICT,
        subqueries_definition={},
    )
    for warning in warnings:
        flash(escape(warning), "warning")

    if form.only_validated_offerers.data:
        if "venue" not in inner_joins:
            base_query = base_query.join(offerers_models.Venue, educational_models.CollectiveOffer.venue)
        if "offerer" not in inner_joins:
            base_query = base_query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
        base_query = base_query.filter(offerers_models.Offerer.isValidated)

    if form.sort.data:
        base_query = base_query.order_by(
            getattr(getattr(educational_models.CollectiveOffer, form.sort.data), form.order.data)()
        )

    # +1 to check if there are more results than requested
    return base_query.with_entities(educational_models.CollectiveOffer.id).limit(form.limit.data + 1)


def _get_collective_offers(
    form: forms.GetCollectiveOfferAdvancedSearchForm,
) -> list[educational_models.CollectiveOffer]:
    # Aggregate validation rules as an array of names returned in a single row
    rules_subquery = (
        sa.select(sa.func.array_agg(offers_models.OfferValidationRule.name))
        .select_from(offers_models.OfferValidationRule)
        .join(educational_models.ValidationRuleCollectiveOfferLink)
        .filter(
            educational_models.ValidationRuleCollectiveOfferLink.collectiveOfferId
            == educational_models.CollectiveOffer.id
        )
        .correlate(educational_models.CollectiveOffer)
        .scalar_subquery()
    )

    query = (
        db.session.query(
            educational_models.CollectiveOffer,
            rules_subquery.label("rules"),
        )
        .filter(educational_models.CollectiveOffer.id.in_(_get_collective_offer_ids_query(form).subquery()))
        .options(
            sa.orm.load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.name,
                educational_models.CollectiveOffer.dateCreated,
                educational_models.CollectiveOffer.validation,
                educational_models.CollectiveOffer.formats,
                educational_models.CollectiveOffer.authorId,
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).load_only(
                educational_models.CollectiveStock.beginningDatetime,
                educational_models.CollectiveStock.startDatetime,
                educational_models.CollectiveStock.endDatetime,
                educational_models.CollectiveStock.price,
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue, innerjoin=True).load_only(
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.departementCode,
            )
            # needed to check if stock is bookable and compute initial/remaining stock:
            .joinedload(offerers_models.Venue.managingOfferer, innerjoin=True)
            .load_only(
                offerers_models.Offerer.name, offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus
            )
            .joinedload(offerers_models.Offerer.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.confidenceRule)
            .load_only(offerers_models.OffererConfidenceRule.confidenceLevel),
            sa.orm.joinedload(educational_models.CollectiveOffer.institution).load_only(
                educational_models.EducationalInstitution.name,
                educational_models.EducationalInstitution.institutionId,
                educational_models.EducationalInstitution.institutionType,
                educational_models.EducationalInstitution.city,
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.author).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
        )
    )

    if form.sort.data:
        order = form.order.data or "desc"
        query = query.order_by(getattr(getattr(educational_models.CollectiveOffer, form.sort.data), order)())

    return query.all()


@blueprint.route("", methods=["GET"])
def list_collective_offers() -> utils.BackofficeResponse:
    form = forms.GetCollectiveOfferAdvancedSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("collective_offer/list.html", rows=[], form=form), 400

    if form.is_empty():
        form_data = MultiDict(utils.get_query_params())
        form_data.update({"search-0-search_field": "ID", "search-0-operator": "IN"})
        form = forms.GetCollectiveOfferAdvancedSearchForm(formdata=form_data)
        return render_template("collective_offer/list.html", rows=[], form=form)

    collective_offers = _get_collective_offers(form)
    collective_offers = utils.limit_rows(collective_offers, form.limit.data)

    return render_template(
        "collective_offer/list.html",
        rows=collective_offers,
        form=form,
        date_created_sort_url=(
            form.get_sort_link_with_search_data(".list_collective_offers") if form.sort.data else None
        ),
    )


@blueprint.route("/<int:collective_offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_validate_collective_offer_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.filter_by(id=collective_offer_id).one_or_none()
    if not collective_offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.collective_offer.validate_collective_offer", collective_offer_id=collective_offer.id
        ),
        div_id=f"validate-collective-offer-modal-{collective_offer.id}",
        title=f"Validation de l'offre {collective_offer.name}",
        button_text="Valider l'offre",
    )


@blueprint.route("/<int:collective_offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.APPROVED, [collective_offer_id])
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)


def _batch_validate_or_reject_collective_offers(
    validation: offer_mixin.OfferValidationStatus, collective_offer_ids: list[int]
) -> bool:
    collective_offers = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id.in_(collective_offer_ids),
        educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
    ).all()

    if len(collective_offer_ids) != len(collective_offers):
        flash(
            (
                "Seules les offres collectives en attente peuvent être validées"
                if validation is offer_mixin.OfferValidationStatus.APPROVED
                else "Seules les offres collectives en attente peuvent être rejetées"
            ),
            "warning",
        )
        return False

    collective_offer_update_succeed_ids: list[int] = []
    collective_offer_update_failed_ids: list[int] = []

    for collective_offer in collective_offers:
        old_validation_status = collective_offer.validation
        new_validation_status = validation
        collective_offer.validation = new_validation_status
        collective_offer.lastValidationDate = datetime.datetime.utcnow()
        collective_offer.lastValidationType = offer_mixin.OfferValidationType.MANUAL
        collective_offer.lastValidationAuthorUserId = current_user.id

        if validation is offer_mixin.OfferValidationStatus.APPROVED:
            collective_offer.isActive = True

        try:
            db.session.commit()
        except Exception:  # pylint: disable=broad-except
            collective_offer_update_failed_ids.append(collective_offer.id)
            continue

        collective_offer_update_succeed_ids.append(collective_offer.id)

        recipients = (
            [collective_offer.venue.bookingEmail]
            if collective_offer.venue.bookingEmail
            else [recipient.user.email for recipient in collective_offer.venue.managingOfferer.UserOfferers]
        )

        transactional_mails.send_offer_validation_status_update_email(
            collective_offer, old_validation_status, new_validation_status, recipients
        )

        if collective_offer.institutionId is not None:
            adage_client.notify_institution_association(serialize_collective_offer(collective_offer))

    if len(collective_offer_update_succeed_ids) == 1:
        flash(
            (
                "L'offre collective a été validée"
                if validation is offer_mixin.OfferValidationStatus.APPROVED
                else "L'offre collective a été rejetée"
            ),
            "success",
        )
    elif collective_offer_update_succeed_ids:
        flash(
            (
                f"Les offres collectives {', '.join(map(str, collective_offer_update_succeed_ids))} ont été validées"
                if validation is offer_mixin.OfferValidationStatus.APPROVED
                else f"Les offres collectives {', '.join(map(str, collective_offer_update_succeed_ids))} ont été rejetées"
            ),
            "success",
        )

    if len(collective_offer_update_failed_ids) > 0:
        flash(
            (
                f"Une erreur est survenue lors de la validation des offres collectives : {', '.join(map(str, collective_offer_update_failed_ids))}"
                if validation is offer_mixin.OfferValidationStatus.APPROVED
                else f"Une erreur est survenue lors du rejet des offres collectives : {', '.join(map(str, collective_offer_update_failed_ids))}"
            ),
            "warning",
        )
    return True


@blueprint.route("/<int:collective_offer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_reject_collective_offer_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.filter_by(id=collective_offer_id).one_or_none()
    if not collective_offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.collective_offer.reject_collective_offer", collective_offer_id=collective_offer.id),
        div_id=f"reject-collective-offer-modal-{collective_offer.id}",
        title=f"Rejet de l'offre {collective_offer.name}",
        button_text="Rejeter l'offre",
    )


@blueprint.route("/<int:collective_offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.REJECTED, [collective_offer_id])
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)


@blueprint.route("/batch/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_collective_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.collective_offer.batch_validate_collective_offers"),
        div_id="batch-validate-modal",
        title="Voulez-vous valider les offres collectives sélectionnées ?",
        button_text="Valider",
    )


@blueprint.route("/batch/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_collective_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.collective_offer.batch_reject_collective_offers"),
        div_id="batch-reject-modal",
        title="Voulez-vous rejeter les offres collectives sélectionnées ?",
        button_text="Rejeter",
    )


@blueprint.route("/batch/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_validate_collective_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)

    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.APPROVED, form.object_ids_list)
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)


@blueprint.route("/batch/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_collective_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)

    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.REJECTED, form.object_ids_list)
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)


def _is_collective_offer_price_editable(collective_offer: educational_models.CollectiveOffer) -> bool:
    # if the offer has no stock it has no price therefore its price cannot be updated
    if not collective_offer.collectiveStock:
        return False

    # cannot update an offer's price while the cashflow generation script is running
    if finance_api.are_cashflows_being_generated():
        return False

    # cannot update an offer's stock if it already has a pricing
    pricing_query = (
        db.session.query(finance_models.Pricing.id)
        .join(educational_models.CollectiveBooking, finance_models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == collective_offer.id,
            finance_models.Pricing.status.in_(
                (finance_models.PricingStatus.PROCESSED, finance_models.PricingStatus.INVOICED)
            ),
        )
    )
    if pricing_query.one_or_none():
        return False

    return True


@blueprint.route("/<int:collective_offer_id>/details", methods=["GET"])
def get_collective_offer_details(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer_query = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id == collective_offer_id
    ).options(
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
        sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
            educational_models.CollectiveStock.collectiveBookings
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.venue),
        sa.orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(offerers_models.Venue.managingOfferer),
        sa.orm.joinedload(educational_models.CollectiveOffer.lastValidationAuthor).load_only(
            users_models.User.firstName, users_models.User.lastName
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.teacher).load_only(
            educational_models.EducationalRedactor.firstName,
            educational_models.EducationalRedactor.lastName,
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.institution).load_only(
            educational_models.EducationalInstitution.name
        ),
        sa.orm.joinedload(educational_models.CollectiveOffer.template).load_only(
            educational_models.CollectiveOfferTemplate.name,
        ),
    )
    collective_offer = collective_offer_query.one_or_none()
    if not collective_offer:
        flash("Cette offre collective n'existe pas", "warning")
        return redirect(url_for("backoffice_web.collective_offer.list_collective_offers"), code=303)

    is_collective_offer_price_editable = _is_collective_offer_price_editable(collective_offer)
    return render_template(
        "collective_offer/details.html",
        collective_offer=collective_offer,
        is_collective_offer_price_editable=is_collective_offer_price_editable,
    )


@blueprint.route("/<int:collective_offer_id>/update-price", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def edit_collective_offer_price(collective_offer_id: int) -> utils.BackofficeResponse:
    redirect_url = request.referrer or url_for(
        "backoffice_web.collective_offer.get_collective_offer_details", collective_offer_id=collective_offer_id
    )
    collective_offer = (
        educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.id == collective_offer_id)
        .options(
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
            sa.orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue),
            sa.orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
                offerers_models.Venue.managingOfferer
            ),
        )
        .one_or_none()
    )

    if not collective_offer:
        flash("Cette offre collective n'existe pas", "warning")
        return redirect(redirect_url, code=303)

    is_collective_offer_price_editable = _is_collective_offer_price_editable(collective_offer)

    if not is_collective_offer_price_editable:
        flash("Cette offre n'est pas modifiable", "warning")
        return redirect(redirect_url, code=303)

    form = forms.EditCollectiveOfferPrice()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(redirect_url, code=303)
    price = form.price.data
    number_of_tickets = form.numberOfTickets.data

    collective_booking = (
        educational_models.CollectiveBooking.query.join(
            educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock
        )
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == collective_offer.id,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.CANCELLED,
        )
        .one_or_none()
    )

    if collective_booking:
        is_confirmed_or_used = collective_booking.status in [
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.USED,
        ]
        if is_confirmed_or_used and price > collective_offer.collectiveStock.price:
            flash("Impossible d'augmenter le prix d'une offre confirmée", "warning")
            return redirect(redirect_url, code=303)

        if is_confirmed_or_used and number_of_tickets > collective_offer.collectiveStock.numberOfTickets:
            flash("Impossible d'augmenter le nombre de participants d'une offre confirmée", "warning")
            return redirect(redirect_url, code=303)

        try:
            cancelled_event = finance_api.cancel_latest_event(collective_booking)
            if cancelled_event:
                finance_api.add_event(
                    motive=finance_models.FinanceEventMotive.BOOKING_USED,
                    booking=collective_booking,
                )
            db.session.commit()
        except finance_exceptions.NonCancellablePricingError:
            flash("Impossible, réservation est déjà remboursée (ou en cours de remboursement)", "warning")
            db.session.rollback()
            return redirect(redirect_url, code=303)

    collective_offer.collectiveStock.price = price
    collective_offer.collectiveStock.numberOfTickets = number_of_tickets
    db.session.commit()

    flash("L'offre collective a été mise à jour", "success")
    return redirect(redirect_url, code=303)


@blueprint.route("/<int:collective_offer_id>/update-price", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_collective_offer_price_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = educational_models.CollectiveOffer.query.filter_by(id=collective_offer_id).one_or_none()
    if not collective_offer:
        raise NotFound()

    form = forms.EditCollectiveOfferPrice(
        price=collective_offer.collectiveStock.price,
        numberOfTickets=collective_offer.collectiveStock.numberOfTickets,
    )
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.collective_offer.edit_collective_offer_price", collective_offer_id=collective_offer_id
        ),
        div_id="update-collective-offer-price",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Ajuster le prix de l'offre collective {collective_offer_id}",
        button_text="Ajuster le prix",
    )
