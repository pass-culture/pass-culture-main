import datetime
from functools import reduce
import re

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core import search
from pcapi.core.bookings import api as bookings_api
from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import models as criteria_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository
from pcapi.utils import date as date_utils
from pcapi.workers import push_notification_job

from . import autocomplete
from . import utils
from .forms import empty as empty_forms
from .forms import offer as offer_forms


list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.READ_OFFERS,
)


def _get_offers(form: offer_forms.GetOffersListForm) -> list[offers_models.Offer]:
    base_query = offers_models.Offer.query.options(
        sa.orm.load_only(
            offers_models.Offer.id,
            offers_models.Offer.name,
            offers_models.Offer.subcategoryId,
            offers_models.Offer.rankingWeight,
            offers_models.Offer.dateCreated,
            offers_models.Offer.validation,
            offers_models.Offer.lastValidationDate,
            offers_models.Offer.lastValidationType,
            offers_models.Offer.isActive,
        ),
        sa.orm.joinedload(offers_models.Offer.stocks).load_only(
            offers_models.Stock.offerId,
            # needed to check if stock is bookable and compute initial/remaining stock:
            offers_models.Stock.beginningDatetime,
            offers_models.Stock.bookingLimitDatetime,
            offers_models.Stock.isSoftDeleted,
            offers_models.Stock.quantity,
            offers_models.Stock.dnBookedQuantity,
        ),
        sa.orm.joinedload(offers_models.Offer.criteria).load_only(criteria_models.Criterion.name),
        sa.orm.joinedload(offers_models.Offer.venue).load_only(
            offerers_models.Venue.managingOffererId, offerers_models.Venue.departementCode, offerers_models.Venue.name
        )
        # needed to check if stock is bookable and compute initial/remaining stock:
        .joinedload(offerers_models.Venue.managingOfferer).load_only(
            offerers_models.Offerer.name, offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus
        ),
    )
    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        base_query = base_query.filter(offers_models.Offer.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        base_query = base_query.filter(offers_models.Offer.dateCreated <= to_datetime)

    if form.criteria.data:
        base_query = base_query.outerjoin(offers_models.Offer.criteria).filter(
            criteria_models.Criterion.id.in_(form.criteria.data)
        )

    if form.category.data:
        base_query = base_query.filter(
            offers_models.Offer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.department.data:
        base_query = base_query.join(offers_models.Offer.venue).filter(
            offerers_models.Venue.departementCode.in_(form.department.data)
        )

    if form.venue.data:
        base_query = base_query.filter(offers_models.Offer.venueId.in_(form.venue.data))

    if form.offerer.data:
        base_query = base_query.join(offers_models.Offer.venue).filter(
            offerers_models.Venue.managingOffererId.in_(form.offerer.data)
        )

    if form.status.data:
        base_query = base_query.filter(offers_models.Offer.validation.in_(form.status.data))

    if form.only_validated_offerers.data:
        base_query = (
            base_query.join(offers_models.Offer.venue)
            .join(offerers_models.Venue.managingOfferer)
            .filter(offerers_models.Offerer.isValidated)
        )

    if form.q.data:
        search_query = form.q.data
        or_filters = []

        if form.where.data == offer_forms.OfferSearchColumn.EAN.name or (
            form.where.data == offer_forms.OfferSearchColumn.ALL.name and utils.is_ean_valid(search_query)
        ):
            or_filters.append(offers_models.Offer.extraData["ean"].astext == utils.format_ean_or_visa(search_query))

        if form.where.data == offer_forms.OfferSearchColumn.VISA.name or (
            form.where.data == offer_forms.OfferSearchColumn.ALL.name and utils.is_visa_valid(search_query)
        ):
            or_filters.append(offers_models.Offer.extraData["visa"].astext == utils.format_ean_or_visa(search_query))

        if form.where.data in (offer_forms.OfferSearchColumn.ALL.name, offer_forms.OfferSearchColumn.ID.name):
            if search_query.isnumeric():
                or_filters.append(offers_models.Offer.id == int(search_query))
            else:
                terms = re.split(r"[,;\s]+", search_query)
                if all(term.isnumeric() for term in terms):
                    or_filters.append(offers_models.Offer.id.in_([int(term) for term in terms]))

        if form.where.data == offer_forms.OfferSearchColumn.NAME.name or (
            form.where.data == offer_forms.OfferSearchColumn.ALL.name and not or_filters
        ):
            name_query = "%{}%".format(search_query)
            or_filters.append(offers_models.Offer.name.ilike(name_query))

        if or_filters:
            query = base_query.filter(or_filters[0])
            if len(or_filters) > 1:
                # Same as for bookings, where union has better performance than or_
                query = query.union(*(base_query.filter(f) for f in or_filters[1:]))
        else:
            # Fallback, no result -- this should not happen when validate_q() checks searched string
            query = base_query.filter(False)
    else:
        query = base_query

    if form.sort.data:
        query = query.order_by(getattr(getattr(offers_models.Offer, form.sort.data), form.order.data)())

    # +1 to check if there are more results than requested
    return query.limit(form.limit.data + 1).all()


def _get_initial_stock(offer: offers_models.Offer) -> int | str:
    quantities = [stock.quantity for stock in offer.bookableStocks]
    if None in quantities:
        return "Illimité"
    # only integers in quantities
    return sum(quantities)  # type: ignore [arg-type]


def _get_remaining_stock(offer: offers_models.Offer) -> int | str:
    remaining_quantities = [stock.remainingQuantity for stock in offer.bookableStocks]
    if "unlimited" in remaining_quantities:
        return "Illimité"
    # only integers in remaining_quantities
    return sum(remaining_quantities)  # type: ignore [arg-type]


@list_offers_blueprint.route("", methods=["GET"])
def list_offers() -> utils.BackofficeResponse:
    form = offer_forms.GetOffersListForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("offer/list.html", rows=[], form=form), 400

    if form.is_empty():
        return render_template("offer/list.html", rows=[], form=form)

    offers = _get_offers(form)

    if len(offers) > form.limit.data:
        flash(
            f"Il y a plus de {form.limit.data} résultats dans la base de données, la liste ci-dessous n'en donne donc "
            "qu'une partie. Veuillez affiner les filtres de recherche.",
            "info",
        )
        offers = offers[: form.limit.data]

    autocomplete.prefill_criteria_choices(form.criteria)
    autocomplete.prefill_offerers_choices(form.offerer)
    autocomplete.prefill_venues_choices(form.venue)

    return render_template(
        "offer/list.html",
        rows=offers,
        form=form,
        date_created_sort_url=form.get_sort_link(".list_offers") if form.sort.data else None,
        get_initial_stock=_get_initial_stock,
        get_remaining_stock=_get_remaining_stock,
    )


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_edit_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = (
        offers_models.Offer.query.filter_by(id=offer_id)
        .options(
            sa.orm.joinedload(offers_models.Offer.criteria).load_only(
                criteria_models.Criterion.id, criteria_models.Criterion.name
            )
        )
        .one_or_none()
    )
    if not offer:
        raise NotFound()

    form = offer_forms.EditOfferForm()
    form.criteria.choices = [(criterion.id, criterion.name) for criterion in offer.criteria]
    if offer.rankingWeight:
        form.rankingWeight.data = offer.rankingWeight

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.edit_offer", offer_id=offer.id),
        div_id=f"edit-offer-modal-{offer.id}",
        title=f"Édition de l'offre {offer.name}",
        button_text="Enregistrer les modifications",
    )


@list_offers_blueprint.route("/batch/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_batch_validate_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.batch_validate_offers"),
        div_id="batch-validate-offer-modal",
        title="Voulez-vous valider les offres sélectionnées ?",
        button_text="Valider",
    )


@list_offers_blueprint.route("/batch-validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def batch_validate_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_validate_offers(form.object_ids_list)
    flash("Les offres ont été validées avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/batch/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_batch_reject_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.batch_reject_offers"),
        div_id="batch-reject-offer-modal",
        title="Voulez-vous rejeter les offres sélectionnées ?",
        button_text="Rejeter",
    )


@list_offers_blueprint.route("/batch-reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def batch_reject_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_reject_offers(form.object_ids_list)
    flash("Les offres ont été rejetées avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/batch/edit", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_batch_edit_offer_form() -> utils.BackofficeResponse:
    form = offer_forms.BatchEditOfferForm()
    if form.object_ids.data:
        if not form.validate():
            flash(utils.build_form_error_msg(form), "warning")
            return redirect(request.referrer, 400)

        offers = (
            offers_models.Offer.query.filter(offers_models.Offer.id.in_(form.object_ids_list))
            .options(
                sa.orm.joinedload(offers_models.Offer.criteria).load_only(
                    criteria_models.Criterion.id, criteria_models.Criterion.name
                )
            )
            .all()
        )
        criteria = list(reduce(set.intersection, [set(offer.criteria) for offer in offers]))  # type: ignore

        if len(criteria) > 0:
            form.criteria.choices = [(criterion.id, criterion.name) for criterion in criteria]

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.batch_edit_offer"),
        div_id="batch-edit-offer-modal",
        title="Édition des offres",
        button_text="Enregistrer les modifications",
    )


@list_offers_blueprint.route("/batch-edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def batch_edit_offer() -> utils.BackofficeResponse:
    form = offer_forms.BatchEditOfferForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(form.object_ids_list)).all()
    criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(form.criteria.data)).all()

    previous_criteria = list(reduce(set.intersection, [set(offer.criteria) for offer in offers]))  # type: ignore
    deleted_criteria = list(set(previous_criteria).difference(criteria))

    for offer in offers:
        if offer.criteria:
            offer.criteria.extend(criterion for criterion in criteria if criterion not in offer.criteria)
            for criterion in deleted_criteria:
                offer.criteria.remove(criterion)
        else:
            offer.criteria = criteria

        if form.rankingWeight.data == 0:
            offer.rankingWeight = None
        elif form.rankingWeight.data:
            offer.rankingWeight = form.rankingWeight.data

        repository.save(offer)

    search.async_index_offer_ids(form.object_ids_list)

    flash("Les offres ont été modifiées avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def edit_offer(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.get_or_404(offer_id)
    form = offer_forms.EditOfferForm()

    if not form.validate():
        flash("Le formulaire n'est pas valide", "danger")
        return redirect(request.referrer, 400)

    criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(form.criteria.data)).all()

    offer.criteria = criteria
    offer.rankingWeight = form.rankingWeight.data
    repository.save(offer)

    #  Immediately index offer if tags are updated: tags are used by
    #  other tools (eg. building playlists for the home page) and
    #  waiting N minutes for the next indexing cron tasks is painful.
    search.reindex_offer_ids([offer.id])

    flash("L'offre a été modifiée avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_validate_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.validate_offer", offer_id=offer.id),
        div_id=f"validate-offer-modal-{offer.id}",
        title=f"Validation de l'offre {offer.name}",
        button_text="Valider l'offre",
    )


@list_offers_blueprint.route("/<int:offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def validate_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_offers([offer_id])
    flash("L'offre a été validée avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def get_reject_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.offer.reject_offer", offer_id=offer.id),
        div_id=f"reject-offer-modal-{offer.id}",
        title=f"Rejet de l'offre {offer.name}",
        button_text="Rejeter l'offre",
    )


@list_offers_blueprint.route("/<int:offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.FRAUD_ACTIONS)
def reject_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_reject_offers([offer_id])
    flash("L'offre a été rejetée avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_v3_web.offer.list_offers"), 303)


def _batch_validate_offers(offer_ids: list[int]) -> None:
    new_validation = offers_models.OfferValidationStatus.APPROVED
    offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids)).all()

    for offer in offers:
        if offer.validation != new_validation:
            offer.validation = new_validation
            offer.lastValidationDate = datetime.datetime.utcnow()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.isActive = True

            repository.save(offer)

            recipients = (
                [offer.venue.bookingEmail]
                if offer.venue.bookingEmail
                else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
            )
            transactional_mails.send_offer_validation_status_update_email(offer, new_validation, recipients)

    search.async_index_offer_ids(offer_ids)


def _batch_reject_offers(offer_ids: list[int]) -> None:
    new_validation = offers_models.OfferValidationStatus.REJECTED
    offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids)).all()

    for offer in offers:
        if offer.validation != new_validation:
            offer.validation = new_validation
            offer.lastValidationDate = datetime.datetime.utcnow()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.isActive = False
            # cancel_bookings_from_rejected_offer can raise handled exceptions that drop the
            # modifications of the offer; we save them here first
            repository.save(offer)

            cancelled_bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)
            if cancelled_bookings:
                push_notification_job.send_cancel_booking_notification.delay(
                    [booking.id for booking in cancelled_bookings]
                )

            repository.save(offer)

            recipients = (
                [offer.venue.bookingEmail]
                if offer.venue.bookingEmail
                else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
            )
            transactional_mails.send_offer_validation_status_update_email(offer, new_validation, recipients)

    search.async_index_offer_ids(offer_ids)
