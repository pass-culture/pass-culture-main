import datetime
from functools import partial
from io import BytesIO
import logging
import typing

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for
from flask_login import current_user
from flask_sqlalchemy import BaseQuery
from markupsafe import Markup
from markupsafe import escape
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core import search
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as booking_repository
from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import models as criteria_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.repository import repository
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils import date as date_utils
from pcapi.utils import regions as regions_utils
from pcapi.utils import string as string_utils
from pcapi.workers import push_notification_job

from . import forms


list_offers_blueprint = utils.child_backoffice_blueprint(
    "offer",
    __name__,
    url_prefix="/pro/offer",
    permission=perm_models.Permissions.READ_OFFERS,
)

logger = logging.getLogger(__name__)

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
    "REGION": {
        "field": "region",
        "column": offerers_models.Venue.departementCode,
        "inner_join": "venue",
        "special": regions_utils.get_department_codes_for_regions,
    },
    "EAN": {
        "field": "string",
        "column": offers_models.Offer.extraData["ean"].astext,
        "special": string_utils.format_ean_or_visa,
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
        "custom_filters": {
            "NOT_IN": lambda values: (
                sa.exists()
                .where(
                    sa.and_(
                        criteria_models.OfferCriterion.offerId == offers_models.Offer.id,
                        criteria_models.OfferCriterion.criterionId.in_(values),
                    )
                )
                .is_(False)
            )
        },
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
        "special": string_utils.format_ean_or_visa,
    },
    "MUSIC_TYPE": {
        "field": "music_type",
        "column": offers_models.Offer.extraData["musicType"].astext,
    },
    "MUSIC_SUB_TYPE": {
        "field": "music_sub_type",
        "column": offers_models.Offer.extraData["musicSubType"].astext,
    },
    "SHOW_TYPE": {
        "field": "show_type",
        "column": offers_models.Offer.extraData["showType"].astext,
    },
    "SHOW_SUB_TYPE": {
        "field": "show_sub_type",
        "column": offers_models.Offer.extraData["showSubType"].astext,
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

OPERATOR_DICT: dict[str, dict[str, typing.Any]] = {
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
            flash(escape(warning), "warning")

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

        if form.status.data:
            query = query.filter(offers_models.Offer.validation.in_(form.status.data))  # type: ignore [attr-defined]

        if form.q.data:
            search_query = form.q.data
            or_filters = []

            if string_utils.is_ean_valid(search_query):
                or_filters.append(
                    offers_models.Offer.extraData["ean"].astext == string_utils.format_ean_or_visa(search_query)
                )

            if utils.is_visa_valid(search_query):
                or_filters.append(
                    offers_models.Offer.extraData["visa"].astext == string_utils.format_ean_or_visa(search_query)
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
    # union() above may cause duplicates, but distinct() affects performance and causes timeout;
    # actually duplicate ids can be accepted since the current function is called inside .in_()
    return query.with_entities(offers_models.Offer.id).limit(form.limit.data + 1)


def _get_offers(form: forms.InternalSearchForm) -> list[offers_models.Offer]:
    # Compute displayed information in remaining stock column directly, don't joinedload/fetch huge stock data
    booked_quantity_subquery = (
        sa.select(sa.func.coalesce(sa.func.sum(offers_models.Stock.dnBookedQuantity), 0))
        .select_from(offers_models.Stock)
        .filter(offers_models.Stock.offerId == offers_models.Offer.id)
        .correlate(offers_models.Offer)
        .scalar_subquery()
    )
    remaining_quantity_subquery = (
        sa.select(
            sa.case(
                [
                    (
                        sa.func.coalesce(
                            sa.func.max(sa.case([(offers_models.Stock.remainingStock.is_(None), 1)], else_=0)), 0  # type: ignore [attr-defined]
                        )
                        == 0,
                        sa.func.coalesce(sa.func.sum(offers_models.Stock.remainingStock), 0).cast(sa.String),
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
            booked_quantity_subquery.label("booked_quantity"),
            sa.case(
                [
                    (
                        # Same as Offer.isReleased which is not an hybrid property
                        sa.and_(  # type: ignore [type-var]
                            offers_models.Offer._released,
                            offerers_models.Offerer.isActive,
                            offerers_models.Offerer.isValidated,
                        ),
                        remaining_quantity_subquery,
                    )
                ],
                else_="-",
            ).label("remaining_quantity"),
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
            .load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.departementCode,
            )
            .contains_eager(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.id, offerers_models.Offerer.name),
            sa.orm.joinedload(offers_models.Offer.author).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
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
        criteria = set.intersection(*[set(offer.criteria) for offer in offers])

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

    previous_criteria = set.intersection(*[set(offer.criteria) for offer in offers])
    deleted_criteria = previous_criteria.difference(criteria)

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

    search.async_index_offer_ids(
        form.object_ids_list,
        reason=search.IndexationReason.OFFER_BATCH_UPDATE,
    )

    flash("Les offres ont été modifiées avec succès", "success")
    return redirect(request.referrer or url_for("backoffice_web.offer.list_offers"), 303)


@list_offers_blueprint.route("/<int:offer_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def edit_offer(offer_id: int) -> utils.BackofficeResponse:
    offer = offers_models.Offer.query.get_or_404(offer_id)
    form = forms.EditOfferForm()

    if not form.validate():
        flash("Le formulaire n'est pas valide", "warning")
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

    search.async_index_offer_ids(
        offer_ids,
        reason=search.IndexationReason.OFFER_BATCH_VALIDATION,
    )


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
        search.async_index_offer_ids(
            offer_ids,
            reason=search.IndexationReason.OFFER_BATCH_VALIDATION,
        )


@list_offers_blueprint.route("/<int:offer_id>", methods=["GET"])
@utils.permission_required(perm_models.Permissions.READ_OFFERS)
def get_offer_details(offer_id: int) -> utils.BackofficeResponse:
    offer_query = offers_models.Offer.query.filter(offers_models.Offer.id == offer_id).options(
        sa.orm.joinedload(offers_models.Offer.venue)
        .load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.name,
            offerers_models.Venue.publicName,
            offerers_models.Venue.managingOffererId,
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
        sa.orm.joinedload(offers_models.Offer.criteria),
        sa.orm.joinedload(offers_models.Offer.flaggingValidationRules),
        sa.orm.joinedload(offers_models.Offer.mediations),
        sa.orm.joinedload(offers_models.Offer.lastProvider).load_only(providers_models.Provider.name),
    )
    offer = offer_query.one_or_none()

    if not offer:
        raise NotFound()

    editable_stock_ids = set()
    if offer.isEvent and not finance_api.are_cashflows_being_generated():
        # store the ids in a set as we will use multiple in on it
        editable_stock_ids = _get_editable_stock(offer_id)

    is_advanced_pro_support = utils.has_current_user_permission(perm_models.Permissions.ADVANCED_PRO_SUPPORT)

    edit_offer_venue_form = None
    if is_advanced_pro_support:
        try:
            venue_choices = offers_api.check_can_move_event_offer(offer)
            edit_offer_venue_form = forms.EditOfferVenueForm()
            edit_offer_venue_form.set_venue_choices(venue_choices)
        except offers_exceptions.MoveOfferBaseException:
            pass

    return render_template(
        "offer/details.html",
        offer=offer,
        active_tab=request.args.get("active_tab", "stock"),
        editable_stock_ids=editable_stock_ids,
        reindex_offer_form=empty_forms.EmptyForm() if is_advanced_pro_support else None,
        edit_offer_venue_form=edit_offer_venue_form,
    )


def _get_editable_stock(offer_id: int) -> set[int]:
    raw_stock_ids = (
        db.session.query(offers_models.Stock.id)
        .join(bookings_models.Booking, offers_models.Stock.bookings)
        .join(offers_models.Offer, offers_models.Stock.offer)
        .filter(
            offers_models.Offer.isEvent,
            offers_models.Stock.offerId == offer_id,
            bookings_models.Booking.status.in_(
                (
                    bookings_models.BookingStatus.CONFIRMED,
                    bookings_models.BookingStatus.USED,
                ),
            ),
            offers_models.Stock.id.not_in(
                db.session.query(offers_models.Stock.offerId)
                .join(bookings_models.Booking, offers_models.Stock.bookings)
                .join(finance_models.Pricing, bookings_models.Booking.pricings)
                .filter(
                    finance_models.Pricing.status.in_(
                        (
                            finance_models.PricingStatus.PROCESSED,
                            finance_models.PricingStatus.INVOICED,
                        )
                    ),
                    offers_models.Stock.offerId == offer_id,
                ),
            ),
        )
    )
    return set(stock_id for stock_id, in raw_stock_ids)


def _is_stock_editable(offer_id: int, stock_id: int) -> bool:
    return stock_id in _get_editable_stock(offer_id)


@list_offers_blueprint.route("/<int:offer_id>/stock/<int:stock_id>/edit", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def edit_offer_stock(offer_id: int, stock_id: int) -> utils.BackofficeResponse:
    stock = offers_models.Stock.query.filter_by(id=stock_id).one()

    if stock.offerId != offer_id:
        flash("L'offer_id et le stock_id ne sont pas cohérents.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)
    if finance_api.are_cashflows_being_generated():
        flash("Le script de génération des cashflows est en cours, veuillez réessayer plus tard.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)
    if not _is_stock_editable(offer_id, stock_id):
        flash("Ce stock n'est pas éditable.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)

    form = forms.EditStockForm()
    old_price = stock.price

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)

    if stock.price < form.price.data:
        flash("Le prix ne doit pas être supérieur au prix original du stock.", "warning")
        return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)

    offers_api.update_used_stock_price(stock=stock, new_price=form.price.data)

    logger.info(
        "Un administrateur a changé le prix d'un stock d'évènement passé",
        extra={
            "user_id": current_user.id,
            "stock_id": stock_id,
            "old_price": float(old_price),
            "new_price": float(form.price.data),
        },
    )
    flash(f"Le stock {stock_id} a bien été mis à jour.", "success")
    db.session.commit()
    return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)


@list_offers_blueprint.route("/<int:offer_id>/stock/<int:stock_id>/edit", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_OFFERS)
def get_offer_stock_edit_form(offer_id: int, stock_id: int) -> utils.BackofficeResponse:
    if finance_api.are_cashflows_being_generated():
        return render_template(
            "components/turbo/modal_form.html",
            div_id=f"edit-offer-modal-{stock_id}",
            title=f"Baisser le prix du stock {stock_id}",
            alert="Le script de génération des cashflows est en cours, veuillez réessayer plus tard.",
        )

    if not _is_stock_editable(offer_id, stock_id):
        return render_template(
            "components/turbo/modal_form.html",
            div_id=f"edit-offer-modal-{stock_id}",
            title=f"Baisser le prix du stock {stock_id}",
            alert="Ce stock n'est pas éditable.",
        )

    form = forms.EditStockForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.offer.edit_offer_stock", offer_id=offer_id, stock_id=stock_id),
        div_id=f"edit-offer-modal-{stock_id}",
        title=f"Baisser le prix du stock {stock_id}",
        button_text="Baisser le prix",
    )


@list_offers_blueprint.route("/<int:offer_id>/reindex", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def reindex(offer_id: int) -> utils.BackofficeResponse:
    search.async_index_offer_ids(
        {offer_id},
        reason=search.IndexationReason.OFFER_MANUAL_REINDEXATION,
    )

    flash("La resynchronisation de l'offre a été demandée.", "success")
    return redirect(url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id), 303)


@list_offers_blueprint.route("/<int:offer_id>/edit-venue", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def edit_offer_venue(offer_id: int) -> utils.BackofficeResponse:
    offer_url = url_for("backoffice_web.offer.get_offer_details", offer_id=offer_id)

    offer = (
        offers_models.Offer.query.filter_by(id=offer_id)
        .options(sa.orm.joinedload(offers_models.Offer.venue))
        .one_or_none()
    )
    if not offer:
        raise NotFound()

    try:
        form = forms.EditOfferVenueForm()
        if not form.validate():
            flash(utils.build_form_error_msg(form), "warning")
            return redirect(offer_url, 303)

        destination_venue = (
            offerers_models.Venue.query.filter_by(id=int(form.venue.data))
            .outerjoin(
                offerers_models.VenuePricingPointLink,
                sa.and_(
                    offerers_models.VenuePricingPointLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenuePricingPointLink.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .outerjoin(
                offerers_models.VenueReimbursementPointLink,
                sa.and_(
                    offerers_models.VenueReimbursementPointLink.venueId == offerers_models.Venue.id,
                    offerers_models.VenueReimbursementPointLink.timespan.contains(datetime.datetime.utcnow()),
                ),
            )
            .options(
                sa.orm.contains_eager(offerers_models.Venue.pricing_point_links).load_only(
                    offerers_models.VenuePricingPointLink.pricingPointId, offerers_models.VenuePricingPointLink.timespan
                ),
            )
        ).one()

        offers_api.move_event_offer(offer, destination_venue, notify_beneficiary=form.notify_beneficiary.data)

    except offers_exceptions.MoveOfferBaseException as exc:
        flash(Markup("Le lieu de cette offre ne peut pas être modifié : {reason}").format(reason=str(exc)), "warning")
        return redirect(offer_url, 303)

    flash(
        Markup("L'offre a été déplacée vers le lieu <b>{venue_name}</b>").format(
            venue_name=destination_venue.common_name
        ),
        "success",
    )
    return redirect(offer_url, 303)


@list_offers_blueprint.route("/<int:offer_id>/bookings.csv", methods=["GET"])
def download_bookings_csv(offer_id: int) -> utils.BackofficeResponse:
    export_data = booking_repository.get_export(
        user=current_user,
        offer_id=offer_id,
        export_type=bookings_models.BookingExportType.CSV,
    )
    buffer = BytesIO(typing.cast(str, export_data).encode("utf-8-sig"))
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reservations_offre_{offer_id}.csv",
        mimetype="text/csv",
    )


@list_offers_blueprint.route("/<int:offer_id>/bookings.xlsx", methods=["GET"])
def download_bookings_xlsx(offer_id: int) -> utils.BackofficeResponse:
    export_data = booking_repository.get_export(
        user=current_user,
        offer_id=offer_id,
        export_type=bookings_models.BookingExportType.EXCEL,
    )
    buffer = BytesIO(typing.cast(bytes, export_data))
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"reservations_offre_{offer_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
