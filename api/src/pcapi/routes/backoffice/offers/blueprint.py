import datetime
from functools import partial
from functools import reduce
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
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
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.offers import forms
from pcapi.utils import date as date_utils
from pcapi.workers import push_notification_job


list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.READ_OFFERS,
)

aliased_stock = sa.orm.aliased(offers_models.Stock)

SEARCH_FIELD_TO_PYTHON = {
    "CATEGORY": {
        "field": "category",
        "column": offers_models.Offer.subcategoryId,
        "special": lambda l: [
            subcategory.id for subcategory in subcategories_v2.ALL_SUBCATEGORIES if subcategory.category.id in l
        ],
    },
    "CREATION_DATE": {
        "field": "date",
        "column": offers_models.Offer.dateCreated,
        "special": partial(date_utils.date_to_localized_datetime, time_=datetime.datetime.min.time()),
    },
    "DEPARTMENT": {
        "field": "department",
        "column": offerers_models.Venue.departementCode,
        "inner_join": "venue",
    },
    "EAN": {
        "field": "string",
        "column": offers_models.Offer.extraData["ean"].astext,
        "special": utils.format_ean_or_visa,
    },
    "EVENT_DATE": {
        "field": "date",
        "column": aliased_stock.beginningDatetime,
        "special": partial(date_utils.date_to_localized_datetime, time_=datetime.datetime.min.time()),
        "inner_join": "stock",
    },
    "BOOKING_LIMIT_DATE": {
        "field": "date",
        "column": aliased_stock.bookingLimitDatetime,
        "special": partial(date_utils.date_to_localized_datetime, time_=datetime.datetime.min.time()),
        "inner_join": "stock",
    },
    "ID": {
        "field": "integer",
        "column": offers_models.Offer.id,
    },
    "NAME": {
        "field": "string",
        "column": offers_models.Offer.name,
    },
    "OFFERER": {
        "field": "offerer",
        "column": offerers_models.Venue.managingOffererId,
        "inner_join": "venue",
    },
    "TAG": {
        "field": "criteria",
        "column": criteria_models.Criterion.id,
        "inner_join": "criterion",
        "outer_join": "offer_criterion",
        "outer_join_column": criteria_models.OfferCriterion.offerId,
    },
    "STATUS": {
        "field": "status",
        "column": offers_models.Offer.status,
    },
    "SUBCATEGORY": {
        "field": "subcategory",
        "column": offers_models.Offer.subcategoryId,
    },
    "VENUE": {
        "field": "venue",
        "column": offers_models.Offer.venueId,
    },
    "VALIDATION": {"field": "validation", "column": offers_models.Offer.validation},
    "VISA": {
        "field": "string",
        "column": offers_models.Offer.extraData["visa"].astext,
        "special": utils.format_ean_or_visa,
    },
}

JOIN_DICT: dict[str, list[dict[str, typing.Any]]] = {
    "criterion": [
        {
            "name": "criterion",
            "args": (criteria_models.Criterion, offers_models.Offer.criteria),
        }
    ],
    "offer_criterion": [
        {
            "name": "offer_criterion",
            "args": (criteria_models.OfferCriterion, offers_models.Offer.id == criteria_models.OfferCriterion.offerId),
        }
    ],
    "stock": [
        {
            "name": "stock",
            "args": (
                aliased_stock,
                sa.and_(
                    aliased_stock.offerId == offers_models.Offer.id,
                    aliased_stock.isSoftDeleted.is_(False),
                ),
            ),
        }
    ],
    "venue": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, offers_models.Offer.venue),
        }
    ],
}

OPERATOR_DICT: typing.Dict[str, typing.Dict[str, typing.Any]] = {
    **utils.OPERATOR_DICT,
    "NAME_EQUALS": {"function": lambda x, y: x.ilike(y)},
    "NAME_NOT_EQUALS": {"function": lambda x, y: ~x.ilike(y)},
}


def _get_offer_ids_query(form: forms.InternalSearchForm) -> BaseQuery:
    query = offers_models.Offer.query

    if not forms.GetOfferAdvancedSearchForm.is_search_empty(form.search.data):
        query, inner_joins, _, warnings = utils.generate_search_query(
            query=query,
            search_parameters=form.search.data,
            fields_definition=SEARCH_FIELD_TO_PYTHON,
            joins_definition=JOIN_DICT,
            operators_definition=OPERATOR_DICT,
        )
        for warning in warnings:
            flash(warning, "warning")

        if form.only_validated_offerers.data:
            if "venue" not in inner_joins:
                query = query.join(offerers_models.Venue, offers_models.Offer.venue)
            if "offerer" not in inner_joins:
                query = query.join(offerers_models.Offerer, offerers_models.Venue.managingOfferer)
            query = query.filter(offerers_models.Offerer.isValidated)
    else:
        if form.category.data:
            query = query.filter(
                offers_models.Offer.subcategoryId.in_(
                    subcategory.id
                    for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                    if subcategory.category.id in form.category.data
                )
            )

        if form.offerer.data:
            query = query.join(offers_models.Offer.venue).filter(
                offerers_models.Venue.managingOffererId.in_(form.offerer.data)
            )

        if form.q.data:
            search_query = form.q.data
            or_filters = []

            if utils.is_ean_valid(search_query):
                or_filters.append(offers_models.Offer.extraData["ean"].astext == utils.format_ean_or_visa(search_query))

            if utils.is_visa_valid(search_query):
                or_filters.append(
                    offers_models.Offer.extraData["visa"].astext == utils.format_ean_or_visa(search_query)
                )

            if search_query.isnumeric():
                or_filters.append(offers_models.Offer.id == int(search_query))
            else:
                terms = search_utils.split_terms(search_query)
                if all(term.isnumeric() for term in terms):
                    or_filters.append(offers_models.Offer.id.in_([int(term) for term in terms]))

            if not or_filters:
                name_query = "%{}%".format(search_query)
                or_filters.append(offers_models.Offer.name.ilike(name_query))

            if or_filters:
                main_query = query.filter(or_filters[0])
                if len(or_filters) > 1:
                    # Same as for bookings, where union has better performance than or_
                    query = main_query.union(*(query.filter(f) for f in or_filters[1:]))
                else:
                    query = main_query

    # +1 to check if there are more results than requested
    return query.with_entities(offers_models.Offer.id).distinct().limit(form.limit.data + 1)


def _get_offers(form: forms.InternalSearchForm) -> list[offers_models.Offer]:
    # Compute displayed information in remaining stock column directly, don't joinedload/fetch huge stock data
    remaining_stocks_subquery = (
        sa.select(
            sa.case(
                [
                    (
                        sa.func.coalesce(
                            sa.func.max(sa.case([(offers_models.Stock.remainingStock.is_(None), 1)], else_=0)), 0  # type: ignore [attr-defined]
                        )
                        == 0,
                        sa.func.concat(
                            sa.func.coalesce(sa.func.sum(offers_models.Stock.remainingStock), 0).cast(sa.String),
                            " / ",
                            sa.func.coalesce(sa.func.sum(offers_models.Stock.totalStock), 0).cast(sa.String),
                        ),
                    )
                ],
                else_="Illimité",
            )
        )
        .select_from(offers_models.Stock)
        .filter(offers_models.Stock.offerId == offers_models.Offer.id)
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )

    # Aggregate tags as an array of names returned in a single row (joinedload would fetch 1 result row per tag)
    tags_subquery = (
        sa.select(sa.func.array_agg(criteria_models.Criterion.name))
        .select_from(criteria_models.Criterion)
        .join(criteria_models.OfferCriterion)
        .filter(criteria_models.OfferCriterion.offerId == offers_models.Offer.id)
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )

    # Aggregate validation rules as an array of names returned in a single row
    rules_subquery = (
        sa.select(sa.func.array_agg(offers_models.OfferValidationRule.name))
        .select_from(offers_models.OfferValidationRule)
        .join(offers_models.ValidationRuleOfferLink)
        .filter(offers_models.ValidationRuleOfferLink.offerId == offers_models.Offer.id)
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )

    query = (
        db.session.query(
            offers_models.Offer,
            sa.case(
                [
                    (
                        # Same as Offer.isReleased which is not an hybrid property
                        sa.and_(  # type: ignore [type-var]
                            offers_models.Offer._released,
                            offerers_models.Offerer.isActive,
                            offerers_models.Offerer.isValidated,
                        ),
                        remaining_stocks_subquery,
                    )
                ],
                else_="-",
            ).label("remaining_stocks"),
            tags_subquery.label("tags"),
            rules_subquery.label("rules"),
        )
        .filter(offers_models.Offer.id.in_(_get_offer_ids_query(form).subquery()))
        # 1-1 relationships so join will not increase the number of SQL rows
        .join(offers_models.Offer.venue)
        .join(offerers_models.Venue.managingOfferer)
        .options(
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
                offers_models.Offer.extraData,
            ),
            sa.orm.contains_eager(offers_models.Offer.venue)
            .load_only(offerers_models.Venue.id, offerers_models.Venue.name, offerers_models.Venue.departementCode)
            .contains_eager(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.id, offerers_models.Offerer.name),
        )
    )

    if form.sort.data:
        order = form.order.data or "desc"
        query = query.order_by(getattr(getattr(offers_models.Offer, form.sort.data), order)())

    return query.all()


def _get_advanced_search_args(form: forms.InternalSearchForm) -> dict[str, typing.Any]:
    advanced_query = ""
    search_data_tags = set()
    if form.search.data:
        advanced_query = f"?{request.query_string.decode()}"

        for data in form.search.data:
            if data.get("operator"):
                if search_field := data.get("search_field"):
                    if search_field_attr := getattr(forms.SearchAttributes, search_field, None):
                        search_data_tags.add(search_field_attr.value)

    return {
        "advanced_query": advanced_query,
        "search_data_tags": search_data_tags,
    }


@list_offers_blueprint.route("", methods=["GET"])
def list_offers() -> utils.BackofficeResponse:
    display_form = forms.GetOffersSearchForm(formdata=utils.get_query_params())
    form = forms.InternalSearchForm(formdata=utils.get_query_params())
    if not form.validate():
        return render_template("offer/list.html", rows=[], form=display_form, **_get_advanced_search_args(form)), 400

    if form.is_empty():
        return render_template("offer/list.html", rows=[], form=display_form)

    offers = _get_offers(form)
    offers = utils.limit_rows(offers, form.limit.data)

    return render_template(
        "offer/list.html",
        rows=offers,
        form=display_form,
        date_created_sort_url=form.get_sort_link_with_search_data(".list_offers") if form.sort.data else None,
        **_get_advanced_search_args(form),
    )


@list_offers_blueprint.route("get-advanced-search-form", methods=["GET"])
def get_advanced_search_form() -> utils.BackofficeResponse:
    form = forms.GetOfferAdvancedSearchForm(formdata=utils.get_query_params())

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.list_offers"),
        div_id="advanced-offer-search",  # must be consistent with parameter passed to build_lazy_modal
        title="Recherche avancée d'offres individuelles",
        button_text="Appliquer",
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

    form = forms.EditOfferForm()
    form.criteria.choices = [(criterion.id, criterion.name) for criterion in offer.criteria]
    if offer.rankingWeight:
        form.rankingWeight.data = offer.rankingWeight

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.edit_offer", offer_id=offer.id),
        div_id=f"edit-offer-modal-{offer.id}",
        title=f"Édition de l'offre {offer.name}",
        button_text="Enregistrer les modifications",
    )


@list_offers_blueprint.route("/batch/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.batch_validate_offers"),
        div_id="batch-validate-offer-modal",
        title="Voulez-vous valider les offres sélectionnées ?",
        button_text="Valider",
    )


@list_offers_blueprint.route("/batch-validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_validate_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_validate_offers(form.object_ids_list)
    flash("Les offres ont été validées avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/batch/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.batch_reject_offers"),
        div_id="batch-reject-offer-modal",
        title="Voulez-vous rejeter les offres sélectionnées ?",
        button_text="Rejeter",
    )


@list_offers_blueprint.route("/batch-reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_offers() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    _batch_reject_offers(form.object_ids_list)
    flash("Les offres ont été rejetées avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/batch/edit", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_batch_edit_offer_form() -> utils.BackofficeResponse:
    form = forms.BatchEditOfferForm()
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
        criteria = list(reduce(set.intersection, [set(offer.criteria) for offer in offers]))  # type: ignore [arg-type]

        if len(criteria) > 0:
            form.criteria.choices = [(criterion.id, criterion.name) for criterion in criteria]

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.batch_edit_offer"),
        div_id="batch-edit-offer-modal",
        title="Édition des offres",
        button_text="Enregistrer les modifications",
    )


@list_offers_blueprint.route("/batch-edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def batch_edit_offer() -> utils.BackofficeResponse:
    form = forms.BatchEditOfferForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 400)

    offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(form.object_ids_list)).all()
    criteria = criteria_models.Criterion.query.filter(criteria_models.Criterion.id.in_(form.criteria.data)).all()

    previous_criteria = list(
        reduce(set.intersection, [set(offer.criteria) for offer in offers])  # type: ignore [arg-type]
    )
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
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def edit_offer(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.get_or_404(offer_id)
    form = forms.EditOfferForm()

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
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_validate_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.validate_offer", offer_id=offer.id),
        div_id=f"validate-offer-modal-{offer.id}",
        title=f"Validation de l'offre {offer.name}",
        button_text="Valider l'offre",
    )


@list_offers_blueprint.route("/<int:offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_offers([offer_id])
    flash("L'offre a été validée avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_reject_offer_form(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.filter_by(id=offer_id).one_or_none()

    if not offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.reject_offer", offer_id=offer.id),
        div_id=f"reject-offer-modal-{offer.id}",
        title=f"Rejet de l'offre {offer.name}",
        button_text="Rejeter l'offre",
    )


@list_offers_blueprint.route("/<int:offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_offer(offer_id: int) -> utils.BackofficeResponse:
    _batch_reject_offers([offer_id])
    flash("L'offre a été rejetée avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


def _batch_validate_offers(offer_ids: list[int]) -> None:
    new_validation = offers_models.OfferValidationStatus.APPROVED
    offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids)).all()

    for offer in offers:
        if offer.validation != new_validation:
            old_validation = offer.validation
            offer.validation = new_validation
            offer.lastValidationDate = datetime.datetime.utcnow()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.lastValidationAuthorUserId = current_user.id
            offer.isActive = True

            repository.save(offer)

            recipients = (
                [offer.venue.bookingEmail]
                if offer.venue.bookingEmail
                else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
            )
            transactional_mails.send_offer_validation_status_update_email(
                offer, old_validation, new_validation, recipients
            )

    search.async_index_offer_ids(offer_ids)


def _batch_reject_offers(offer_ids: list[int]) -> None:
    new_validation = offers_models.OfferValidationStatus.REJECTED
    offers = offers_models.Offer.query.filter(offers_models.Offer.id.in_(offer_ids)).all()

    for offer in offers:
        if offer.validation != new_validation:
            old_validation = offer.validation
            offer.validation = new_validation
            offer.lastValidationDate = datetime.datetime.utcnow()
            offer.lastValidationType = OfferValidationType.MANUAL
            offer.lastValidationAuthorUserId = current_user.id
            offer.isActive = False

            # cancel_bookings_from_rejected_offer can raise handled exceptions that drop the
            # modifications of the offer; we save them here first
            repository.save(offer)

            cancelled_bookings = bookings_api.cancel_bookings_from_rejected_offer(offer)

            if cancelled_bookings:
                # FIXME: La notification indique que l'offreur a annulé alors que c'est la fraude
                # TODO(PC-23550): SPIKE avec marketing https://passculture.atlassian.net/browse/PC-23550
                # Il faudrait utiliser send_booking_cancellation_emails_to_user_and_offerer et retirer cette notification soit la déplacer dedans, mais un mail est mieux (TBD)
                push_notification_job.send_cancel_booking_notification.delay(
                    [booking.id for booking in cancelled_bookings]
                )

            repository.save(offer)

            recipients = (
                [offer.venue.bookingEmail]
                if offer.venue.bookingEmail
                else [recipient.user.email for recipient in offer.venue.managingOfferer.UserOfferers]
            )
            transactional_mails.send_offer_validation_status_update_email(
                offer, old_validation, new_validation, recipients
            )

    if len(offer_ids) > 0:
        favorites = users_models.Favorite.query.filter(users_models.Favorite.offerId.in_(offer_ids)).all()
        repository.delete(*favorites)
        search.async_index_offer_ids(offer_ids)


@list_offers_blueprint.route("/<int:offer_id>/details", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_OFFERS)
def get_offer_details(offer_id: int) -> utils.BackofficeResponse:
    offer_query = offers_models.Offer.query.filter(offers_models.Offer.id == offer_id).options(
        sa.orm.joinedload(offers_models.Offer.venue)
        .load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
        )
        .joinedload(offerers_models.Venue.managingOfferer)
        .load_only(
            offerers_models.Offerer.id,
            offerers_models.Offerer.name,
            offerers_models.Offerer.isActive,
            offerers_models.Offerer.validationStatus,
        ),
        sa.orm.joinedload(offers_models.Offer.stocks),
        sa.orm.joinedload(offers_models.Offer.lastValidationAuthor).load_only(
            users_models.User.firstName, users_models.User.lastName
        ),
    )
    offer = offer_query.one_or_none()
    if not offer:
        raise NotFound()

    return render_template(
        "offer/details.html",
        offer=offer,
        active_tab=request.args.get("active_tab", "stock"),
        reindex_offer_form=empty_forms.EmptyForm(),
    )


@list_offers_blueprint.route("/<int:offer_id>/reindex", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def reindex(offer_id: int) -> utils.BackofficeResponse:
    search.async_index_offer_ids({offer_id})

    flash("La resynchronisation de l'offre a été demandée.", "success")

    if request.referrer:
        return redirect(request.referrer)

    return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id))
