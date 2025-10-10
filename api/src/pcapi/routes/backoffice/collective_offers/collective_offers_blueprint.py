import re
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from markupsafe import escape
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import NotFound

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.api import offer as collective_offer_api
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import exceptions as finance_exceptions
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import models as geography_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.collective_offers import forms
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.pro.utils import get_connect_as
from pcapi.utils import date as date_utils
from pcapi.utils import regions as regions_utils
from pcapi.utils import urls
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


blueprint = utils.child_backoffice_blueprint(
    "collective_offer",
    __name__,
    url_prefix="/pro/collective-offer",
    permission=perm_models.Permissions.READ_OFFERS,
)


aliased_stock = sa_orm.aliased(educational_models.CollectiveStock)


def _filter_collective_offer_status_query_modifier(query: sa_orm.Query, statuses: typing.Iterable[str]) -> sa_orm.Query:
    # as a collective offer status is a computed property (without a hybrid expression), we cannot simply filter on this field
    # instead we modify the query to apply filters depending on the required status values, as in PC Pro
    return educational_repository.filter_collective_offers_by_statuses(
        query=query,
        statuses=[educational_models.CollectiveOfferDisplayedStatus(s) for s in statuses],
    )


# this should be in sync with the status field in forms
collective_offer_status_choices = [
    status.name
    for status in educational_models.CollectiveOfferDisplayedStatus
    if status != educational_models.CollectiveOfferDisplayedStatus.HIDDEN
]

SEARCH_FIELD_TO_PYTHON: dict[str, dict[str, typing.Any]] = {
    "FORMATS": {
        "field": "formats",
        "column": educational_models.CollectiveOffer.formats,
    },
    "INSTITUTION": {
        "field": "institution",
        "column": educational_models.CollectiveOffer.institutionId,
    },
    "INSTITUTION_DEPT": {
        "field": "department",
        "inner_join": "institution",
        "column": sa.func.postal_code_to_department_code(educational_models.EducationalInstitution.postalCode),
    },
    "CREATION_DATE": {
        "field": "date",
        "column": educational_models.CollectiveOffer.dateCreated,
    },
    "DEPARTMENT": {
        "field": "department",
        "column": geography_models.Address.departmentCode,
        "inner_join": "address",
    },
    "REGION": {
        "field": "region",
        "column": geography_models.Address.departmentCode,
        "inner_join": "address",
        "special": regions_utils.get_department_codes_for_regions,
    },
    "EVENT_DATE": {
        "field": "date",
        "column": aliased_stock.startDatetime,
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
        "query_modifier": {
            "function": _filter_collective_offer_status_query_modifier,
            "choices": collective_offer_status_choices,
        },
    },
    "VENUE": {
        "field": "venue",
        "column": educational_models.CollectiveOffer.venueId,
    },
    "VALIDATED_OFFERER": {
        "field": "boolean",
        "special": lambda x: x == "true",
        "column": offerers_models.Offerer.isValidated,
        "inner_join": "offerer",
    },
    "VALIDATION": {"field": "validation", "column": educational_models.CollectiveOffer.validation},
    "PRICE": {
        "field": "price",
        "column": aliased_stock.price,
        "inner_join": "stock",
    },
    "SYNCHRONIZED": {
        "field": "boolean",
        "special": lambda x: x != "true",
        "column": educational_models.CollectiveOffer.providerId,
    },
    "MINISTRY": {
        "field": "ministry",
        "column": educational_models.EducationalDeposit.ministry,
        "inner_join": "deposit",
    },
    "MEG": {
        "field": "boolean",
        "special": lambda x: x == "true",
        "custom_filters_inner_joins": {  # "inner_join" would not be applied with custom filter
            "NULLABLE": ["institution", "stock"]
        },
        "custom_filters": {
            "NULLABLE": lambda value: (
                sa.exists()
                .where(
                    sa.and_(
                        educational_models.EducationalInstitutionProgramAssociation.institutionId
                        == educational_models.EducationalInstitution.id,
                        educational_models.EducationalInstitutionProgram.id
                        == educational_models.EducationalInstitutionProgramAssociation.programId,
                        educational_models.EducationalInstitutionProgramAssociation.timespan.contains(
                            educational_models.CollectiveStock.startDatetime
                        ),
                        educational_models.EducationalInstitutionProgram.name
                        == educational_models.PROGRAM_MARSEILLE_EN_GRAND,
                    )
                )
                .correlate(educational_models.EducationalInstitution)
                .is_(value)
            )
        },
    },
    "TOP_ACTEUR": {
        "field": "boolean",
        "special": lambda x: x == "true",
        "custom_filters_inner_joins": {  # "inner_join" would not be applied with custom filter
            "NULLABLE": ["venue"]
        },
        "custom_filters": {
            "NULLABLE": lambda value: (
                sa.exists()
                .where(
                    sa.and_(
                        offerers_models.OffererTagMapping.offererId == offerers_models.Venue.managingOffererId,
                        offerers_models.OffererTagMapping.tagId == offerers_models.OffererTag.id,
                        offerers_models.OffererTag.name == offerers_constants.TOP_ACTEUR_TAG_NAME,
                    )
                )
                .correlate(offerers_models.Venue)
                .is_(value)
            )
        },
    },
}


def _get_educational_year_subquery(
    stock_class: type[educational_models.CollectiveStock],
) -> sa.sql.selectable.ScalarSelect:
    return (
        sa.select(educational_models.EducationalYear.adageId)
        .filter(
            stock_class.startDatetime.between(
                educational_models.EducationalYear.beginningDate,
                educational_models.EducationalYear.expirationDate,
            )
        )
        # Final deposit when set, temporary deposit otherwise
        .order_by(sa.desc(educational_models.EducationalDeposit.isFinal))
        .limit(1)
        .correlate(stock_class)
        .scalar_subquery()
    )


JOIN_DICT: dict[str, list[dict[str, typing.Any]]] = {
    "stock": [
        {
            "name": "stock",
            "args": (
                aliased_stock,
                educational_models.CollectiveOffer.collectiveStock,
            ),
        },
    ],
    "address": [
        {
            "name": "offerer_address",
            "args": (offerers_models.OffererAddress, educational_models.CollectiveOffer.offererAddress),
        },
        {
            "name": "address",
            "args": (geography_models.Address, offerers_models.OffererAddress.address),
        },
    ],
    "venue": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, educational_models.CollectiveOffer.venue),
        },
    ],
    "offerer": [
        {
            "name": "venue",
            "args": (offerers_models.Venue, educational_models.CollectiveOffer.venue),
        },
        {
            "name": "offerer",
            "args": (offerers_models.Offerer, offerers_models.Venue.managingOfferer),
        },
    ],
    "institution": [
        {
            "name": "institution",
            "args": (educational_models.EducationalInstitution, educational_models.CollectiveOffer.institution),
        },
    ],
    "deposit": [
        {
            "name": "stock",
            "args": (
                aliased_stock,
                educational_models.CollectiveOffer.collectiveStock,
            ),
        },
        {
            "name": "institution",
            "args": (educational_models.EducationalInstitution, educational_models.CollectiveOffer.institution),
        },
        {
            "name": "deposit",
            "args": (
                educational_models.EducationalDeposit,
                sa.and_(
                    educational_models.EducationalDeposit.educationalInstitutionId
                    == educational_models.EducationalInstitution.id,
                    educational_models.EducationalDeposit.educationalYearId
                    == _get_educational_year_subquery(aliased_stock),
                ),
            ),
        },
    ],
}


def _render_collective_offers(collective_offers_ids: list[int] | None = None) -> utils.BackofficeResponse:
    rows = []
    if collective_offers_ids:
        rows = _get_collective_offers(collective_offers_ids).all()

    connect_as = {}
    for row in rows:
        connect_as[row.CollectiveOffer.id] = get_connect_as(
            object_type="collective_offer",
            object_id=row.CollectiveOffer.id,
            pc_pro_path=urls.build_pc_pro_offer_path(row.CollectiveOffer),
        )

    return render_template(
        "collective_offer/list_rows.html",
        connect_as=connect_as,
        rows=rows,
    )


def _get_collective_offer_ids_query(form: forms.GetCollectiveOfferAdvancedSearchForm) -> sa_orm.Query:
    base_query, _, _, warnings = utils.generate_search_query(
        query=db.session.query(educational_models.CollectiveOffer.id),
        search_parameters=form.search.data,
        fields_definition=SEARCH_FIELD_TO_PYTHON,
        joins_definition=JOIN_DICT,
        subqueries_definition={},
    )
    for warning in warnings:
        flash(escape(warning), "warning")

    if form.sort.data:
        base_query = base_query.order_by(
            getattr(getattr(educational_models.CollectiveOffer, form.sort.data), form.order.data)()
        )

    # +1 to check if there are more results than requested
    return base_query.limit(form.limit.data + 1)


def _get_collective_offers(
    collective_offers_ids: list[int] | sa_orm.Query,
) -> sa_orm.Query:
    if utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
        # Subqueries avoid too many joins, which would make the query planner decide to seq scan tables.

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

        institution_info_subquery = (
            sa.select(
                sa.func.jsonb_build_object(
                    "ministry",
                    educational_models.EducationalDeposit.ministry,
                    "educational_programs",
                    sa.func.array_agg(educational_models.EducationalInstitutionProgram.label),
                    "educational_year",
                    educational_models.EducationalYear.displayed_year,
                )
            )
            .select_from(educational_models.EducationalDeposit)
            .filter(
                educational_models.EducationalDeposit.educationalInstitutionId
                == educational_models.EducationalInstitution.id,
                educational_models.EducationalDeposit.educationalYearId
                == _get_educational_year_subquery(educational_models.CollectiveStock),
            )
            .outerjoin(
                educational_models.EducationalYear,
                educational_models.EducationalYear.adageId == educational_models.EducationalDeposit.educationalYearId,
            )
            .outerjoin(
                educational_models.EducationalInstitutionProgramAssociation,
                sa.and_(
                    educational_models.EducationalInstitutionProgramAssociation.institutionId
                    == educational_models.EducationalInstitution.id,
                    educational_models.EducationalInstitutionProgramAssociation.timespan.contains(
                        educational_models.CollectiveStock.startDatetime
                    ),
                ),
            )
            .outerjoin(educational_models.EducationalInstitutionProgramAssociation.program)
            .group_by(educational_models.EducationalDeposit.ministry, educational_models.EducationalYear.displayed_year)
            .correlate(educational_models.EducationalInstitution, educational_models.CollectiveStock)
            .scalar_subquery()
        )

        # build an object which can be read by jinja macro as if it was the Offerer
        aliased_offerer = sa_orm.aliased(offerers_models.Offerer)
        offerer_badges_subquery = (
            sa.select(
                sa.func.jsonb_build_object(
                    "confidenceLevel",
                    offerers_models.OffererConfidenceRule.confidenceLevel,
                    "isTopActeur",
                    aliased_offerer.is_top_acteur,
                )
            )
            .select_from(aliased_offerer)
            .outerjoin(offerers_models.OffererConfidenceRule)
            .filter(aliased_offerer.id == offerers_models.Offerer.id)
            .correlate(offerers_models.Offerer)
        )

        # build an object which can be read by jinja macro as if it was the Venue
        venue_badges_subquery = (
            sa.select(
                sa.func.jsonb_build_object("confidenceLevel", offerers_models.OffererConfidenceRule.confidenceLevel)
            )
            .select_from(offerers_models.OffererConfidenceRule)
            .filter(offerers_models.OffererConfidenceRule.venueId == offerers_models.Venue.id)
            .correlate(offerers_models.Venue)
        )

        entities: tuple = (
            educational_models.CollectiveOffer,
            rules_subquery.label("rules"),
            institution_info_subquery.label("institution_info"),
            offerer_badges_subquery.label("offerer_badges"),
            venue_badges_subquery.label("venue_badges"),
        )
    else:
        entities = (
            educational_models.CollectiveOffer,
            sa.null(),  # otherwise row is the CollectiveOffer itself
        )

    query = (
        db.session.query(*entities)
        .filter(educational_models.CollectiveOffer.id.in_(collective_offers_ids))
        .join(offerers_models.Venue)
        .join(offerers_models.Offerer)
        .outerjoin(educational_models.CollectiveOffer.collectiveStock)
        .outerjoin(educational_models.CollectiveOffer.institution)
        .options(
            sa_orm.load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.name,
                educational_models.CollectiveOffer.dateCreated,
                educational_models.CollectiveOffer.validation,
                educational_models.CollectiveOffer.formats,
                educational_models.CollectiveOffer.authorId,
                educational_models.CollectiveOffer.rejectionReason,
                educational_models.CollectiveOffer.providerId,
                educational_models.CollectiveOffer.isActive,
                educational_models.CollectiveOffer.dateArchived,
            ),
            sa_orm.contains_eager(educational_models.CollectiveOffer.collectiveStock).options(
                sa_orm.load_only(
                    educational_models.CollectiveStock.startDatetime,
                    educational_models.CollectiveStock.endDatetime,
                    educational_models.CollectiveStock.bookingLimitDatetime,
                    educational_models.CollectiveStock.price,
                ),
                # bookings are needed to compute displayedStatus
                sa_orm.selectinload(educational_models.CollectiveStock.collectiveBookings).load_only(
                    educational_models.CollectiveBooking.dateCreated,
                    educational_models.CollectiveBooking.status,
                    educational_models.CollectiveBooking.cancellationReason,
                ),
            ),
            sa_orm.contains_eager(educational_models.CollectiveOffer.venue).options(
                sa_orm.load_only(
                    offerers_models.Venue.managingOffererId,
                    offerers_models.Venue.name,
                    offerers_models.Venue.publicName,
                ),
                sa_orm.contains_eager(offerers_models.Venue.managingOfferer).options(
                    sa_orm.load_only(
                        offerers_models.Offerer.name,
                        # needed to check if stock is bookable and compute initial/remaining stock:
                        offerers_models.Offerer.isActive,
                        offerers_models.Offerer.validationStatus,
                    ),
                ),
            ),
            sa_orm.contains_eager(educational_models.CollectiveOffer.institution).load_only(
                educational_models.EducationalInstitution.name,
                educational_models.EducationalInstitution.institutionId,
                educational_models.EducationalInstitution.institutionType,
                educational_models.EducationalInstitution.city,
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.author).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
            ),
            sa_orm.selectinload(educational_models.CollectiveOffer.provider).load_only(
                providers_models.Provider.name,
            ),
        )
    )

    return query


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

    query = _get_collective_offers(_get_collective_offer_ids_query(form))
    if form.sort.data:
        order = form.order.data or "desc"
        query = query.order_by(getattr(getattr(educational_models.CollectiveOffer, form.sort.data), order)())
    rows = utils.limit_rows(query.all(), form.limit.data)

    connect_as = {}
    for row in rows:
        connect_as[row.CollectiveOffer.id] = get_connect_as(
            object_type="collective_offer",
            object_id=row.CollectiveOffer.id,
            pc_pro_path=urls.build_pc_pro_offer_path(row.CollectiveOffer),
        )

    return render_template(
        "collective_offer/list.html",
        connect_as=connect_as,
        rows=rows,
        form=form,
        date_created_sort_url=(
            form.get_sort_link_with_search_data(".list_collective_offers") if form.sort.data else None
        ),
    )


@blueprint.route("/<int:collective_offer_id>/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_validate_collective_offer_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer).filter_by(id=collective_offer_id).one_or_none()
    )
    if not collective_offer:
        raise NotFound()

    form = empty_forms.EmptyForm()

    kwargs = {
        "form": form,
        "dst": url_for(
            "backoffice_web.collective_offer.validate_collective_offer",
            collective_offer_id=collective_offer.id,
        ),
        "div_id": f"validate-collective-offer-modal-{collective_offer.id}",
        "title": f"Validation de l'offre {collective_offer.name}",
        "button_text": "Valider l'offre",
    }

    if utils.is_request_from_htmx():
        return render_template(
            "components/dynamic/modal_form.html",
            target_id=f"#collective-offer-row-{collective_offer_id}",
            **kwargs,
        )

    return render_template("components/turbo/modal_form.html", **kwargs)


@blueprint.route("/<int:collective_offer_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def validate_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.APPROVED, [collective_offer_id])
    if utils.is_request_from_htmx():
        return _render_collective_offers([collective_offer_id])
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)


def _batch_validate_or_reject_collective_offers(
    validation: offer_mixin.OfferValidationStatus,
    collective_offer_ids: list[int],
    reason: educational_models.CollectiveOfferRejectionReason | None = None,
) -> bool:
    collective_offers = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(
            educational_models.CollectiveOffer.id.in_(collective_offer_ids),
            educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
        )
        .all()
    )

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
        with atomic():
            collective_offer_id = collective_offer.id
            old_validation_status = collective_offer.validation
            new_validation_status = validation
            collective_offer.validation = new_validation_status
            collective_offer.lastValidationDate = date_utils.get_naive_utc_now()
            collective_offer.lastValidationType = offer_mixin.OfferValidationType.MANUAL
            collective_offer.lastValidationAuthorUserId = current_user.id

            if validation is offer_mixin.OfferValidationStatus.APPROVED:
                collective_offer.isActive = True
                collective_offer.rejectionReason = None
            else:
                collective_offer.rejectionReason = reason

            try:
                db.session.flush()
            except Exception:
                mark_transaction_as_invalid()
                collective_offer_update_failed_ids.append(collective_offer_id)
                continue

            collective_offer_update_succeed_ids.append(collective_offer.id)

            recipients = (
                [collective_offer.venue.bookingEmail]
                if collective_offer.venue.bookingEmail
                else [recipient.user.email for recipient in collective_offer.venue.managingOfferer.UserOfferers]
            )

            offer_data = transactional_mails.get_email_data_from_offer(
                collective_offer, old_validation_status, new_validation_status
            )
            transactional_mails.send_offer_validation_status_update_email(offer_data, recipients)

            if validation is offer_mixin.OfferValidationStatus.APPROVED and collective_offer.institutionId is not None:
                try:
                    adage_client.notify_institution_association(serialize_collective_offer(collective_offer))
                except educational_exceptions.AdageInvalidEmailException:
                    # in the case of an invalid institution email, adage is not notified but we still want to validate of reject the offer
                    flash(
                        Markup("Email invalide pour l'offre <b>{offer_id}</b>, ADAGE n'a pas été notifié").format(
                            offer_id=collective_offer.id
                        ),
                        "warning",
                    )
                except educational_exceptions.AdageException as exp:
                    flash(
                        Markup(
                            "Erreur lors de la notification à ADAGE pour l'offre <b>{offer_id}</b> : {message}"
                        ).format(offer_id=collective_offer.id, message=exp.message),
                        "warning",
                    )

                    mark_transaction_as_invalid()

                    if collective_offer.id in collective_offer_update_succeed_ids:
                        collective_offer_update_succeed_ids.remove(collective_offer.id)

                    collective_offer_update_failed_ids.append(collective_offer.id)

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
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer).filter_by(id=collective_offer_id).one_or_none()
    )
    if not collective_offer:
        raise NotFound()

    form = forms.RejectCollectiveOfferForm()

    kwargs = {
        "form": form,
        "dst": url_for(
            "backoffice_web.collective_offer.reject_collective_offer", collective_offer_id=collective_offer.id
        ),
        "div_id": f"reject-collective-offer-modal-{collective_offer.id}",
        "title": f"Rejet de l'offre {collective_offer.name}",
        "button_text": "Rejeter l'offre",
    }

    if utils.is_request_from_htmx():
        return render_template(
            "components/dynamic/modal_form.html",
            target_id=f"#collective-offer-row-{collective_offer_id}",
            **kwargs,
        )

    return render_template("components/turbo/modal_form.html", **kwargs)


@blueprint.route("/<int:collective_offer_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def reject_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    form = forms.RejectCollectiveOfferForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        if utils.is_request_from_htmx():
            return _render_collective_offers()
        return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)

    _batch_validate_or_reject_collective_offers(
        offer_mixin.OfferValidationStatus.REJECTED,
        [collective_offer_id],
        educational_models.CollectiveOfferRejectionReason(form.reason.data),
    )
    if utils.is_request_from_htmx():
        return _render_collective_offers([collective_offer_id])
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)


@blueprint.route("/batch/validate", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_validate_collective_offers_form() -> utils.BackofficeResponse:
    form = empty_forms.BatchForm(request.args)
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#collective-offer-table",
        form=form,
        dst=url_for("backoffice_web.collective_offer.batch_validate_collective_offers"),
        div_id="batch-validate-modal",
        title="Voulez-vous valider les offres collectives sélectionnées ?",
        button_text="Valider",
    )


@blueprint.route("/batch/reject", methods=["GET"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def get_batch_reject_collective_offers_form() -> utils.BackofficeResponse:
    form = forms.BatchRejectCollectiveOfferForm(request.args)
    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#collective-offer-table",
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
        return _render_collective_offers()

    _batch_validate_or_reject_collective_offers(offer_mixin.OfferValidationStatus.APPROVED, form.object_ids_list)

    return _render_collective_offers(form.object_ids_list)


@blueprint.route("/batch/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.PRO_FRAUD_ACTIONS)
def batch_reject_collective_offers() -> utils.BackofficeResponse:
    form = forms.BatchRejectCollectiveOfferForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return _render_collective_offers()

    _batch_validate_or_reject_collective_offers(
        offer_mixin.OfferValidationStatus.REJECTED,
        form.object_ids_list,
        educational_models.CollectiveOfferRejectionReason(form.reason.data),
    )
    return _render_collective_offers(form.object_ids_list)


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
    collective_offer_query = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == collective_offer_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
            sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.venue).options(
                sa_orm.joinedload(offerers_models.Venue.confidenceRule).load_only(
                    offerers_models.OffererConfidenceRule.confidenceLevel
                ),
                sa_orm.joinedload(offerers_models.Venue.managingOfferer).options(
                    sa_orm.joinedload(offerers_models.Offerer.confidenceRule).load_only(
                        offerers_models.OffererConfidenceRule.confidenceLevel
                    ),
                    sa_orm.with_expression(
                        offerers_models.Offerer.isTopActeur,
                        offerers_models.Offerer.is_top_acteur.expression,
                    ),
                ),
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.lastValidationAuthor).load_only(
                users_models.User.firstName, users_models.User.lastName
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.teacher).load_only(
                educational_models.EducationalRedactor.firstName,
                educational_models.EducationalRedactor.lastName,
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.institution).load_only(
                educational_models.EducationalInstitution.name,
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.template).load_only(
                educational_models.CollectiveOfferTemplate.name,
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.provider).load_only(
                providers_models.Provider.name,
            ),
            sa_orm.joinedload(
                educational_models.CollectiveOffer.offererAddress,
            )
            .joinedload(
                offerers_models.OffererAddress.address,
            )
            .load_only(
                geography_models.Address.city,
                geography_models.Address.postalCode,
                geography_models.Address.street,
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.domains).load_only(
                educational_models.EducationalDomain.name,
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.nationalProgram).load_only(
                educational_models.NationalProgram.name,
            ),
        )
    )
    collective_offer = collective_offer_query.one_or_none()
    if not collective_offer:
        flash("Cette offre collective n'existe pas", "warning")
        return redirect(url_for("backoffice_web.collective_offer.list_collective_offers"), code=303)

    is_collective_offer_price_editable = _is_collective_offer_price_editable(collective_offer)

    connect_as = get_connect_as(
        object_id=collective_offer.id,
        object_type="collective_offer",
        pc_pro_path=urls.build_pc_pro_offer_path(collective_offer),
    )

    return render_template(
        "collective_offer/details.html",
        collective_offer=collective_offer,
        is_collective_offer_price_editable=is_collective_offer_price_editable,
        connect_as=connect_as,
    )


@blueprint.route("/<int:collective_offer_id>/update-price", methods=["POST"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def edit_collective_offer_price(collective_offer_id: int) -> utils.BackofficeResponse:
    redirect_url = request.referrer or url_for(
        "backoffice_web.collective_offer.get_collective_offer_details", collective_offer_id=collective_offer_id
    )
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == collective_offer_id)
        .options(
            sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock),
            sa_orm.joinedload(educational_models.CollectiveOffer.collectiveStock).joinedload(
                educational_models.CollectiveStock.collectiveBookings
            ),
            sa_orm.joinedload(educational_models.CollectiveOffer.venue),
            sa_orm.joinedload(educational_models.CollectiveOffer.venue).joinedload(
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
        db.session.query(educational_models.CollectiveBooking)
        .join(educational_models.CollectiveStock, educational_models.CollectiveBooking.collectiveStock)
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
            db.session.flush()
        except finance_exceptions.NonCancellablePricingError:
            flash("Impossible, réservation est déjà remboursée (ou en cours de remboursement)", "warning")
            mark_transaction_as_invalid()
            return redirect(redirect_url, code=303)

    collective_offer.collectiveStock.price = price
    collective_offer.collectiveStock.numberOfTickets = number_of_tickets

    flash("L'offre collective a été mise à jour", "success")
    return redirect(redirect_url, code=303)


@blueprint.route("/<int:collective_offer_id>/update-price", methods=["GET"])
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_collective_offer_price_form(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer).filter_by(id=collective_offer_id).one_or_none()
    )
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


@blueprint.route("/<int:collective_offer_id>/move", methods=["GET"])
@atomic()
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def get_move_collective_offer_form(collective_offer_id: int) -> utils.BackofficeResponse:
    if not feature.FeatureToggle.VENUE_REGULARIZATION.is_active():
        raise feature.DisabledFeatureError("VENUE_REGULARIZATION is inactive")

    collective_offer = (
        db.session.query(educational_models.CollectiveOffer).filter_by(id=collective_offer_id).one_or_none()
    )
    if not collective_offer:
        raise NotFound()

    venue_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        collective_offer.venue,
        include_without_pricing_points=True,
        only_similar_pricing_points=True,
        filter_same_bank_account=True,
    )
    move_offer_form = forms.MoveCollectiveOfferForm()
    move_offer_form.set_venue_choices(venue_choices)

    return render_template(
        "components/turbo/modal_form.html",
        form=move_offer_form,
        dst=url_for("backoffice_web.collective_offer.move_collective_offer", collective_offer_id=collective_offer_id),
        div_id=f"move-collective-offer-modal-{collective_offer.id}",
        title=f"Changer le partenaire culturel de l'offre collective {collective_offer_id}",
        button_text="Changer le partenaire",
    )


@blueprint.route("/<int:collective_offer_id>/move", methods=["POST"])
@atomic()
@utils.permission_required(perm_models.Permissions.ADVANCED_PRO_SUPPORT)
def move_collective_offer(collective_offer_id: int) -> utils.BackofficeResponse:
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer).filter_by(id=collective_offer_id).one_or_none()
    )
    if not collective_offer:
        raise NotFound()

    form = forms.MoveCollectiveOfferForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)

    destination_venue = (
        db.session.query(offerers_models.Venue)
        .filter_by(id=int(form.venue.data))
        .outerjoin(
            offerers_models.VenuePricingPointLink,
            sa.and_(
                offerers_models.VenuePricingPointLink.venueId == offerers_models.Venue.id,
                offerers_models.VenuePricingPointLink.timespan.contains(date_utils.get_naive_utc_now()),
            ),
        )
        .options(
            sa_orm.contains_eager(offerers_models.Venue.pricing_point_links).load_only(
                offerers_models.VenuePricingPointLink.pricingPointId, offerers_models.VenuePricingPointLink.timespan
            ),
        )
        .options(sa_orm.joinedload(offerers_models.Venue.offererAddress))
    ).one()

    collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)
    return redirect(request.referrer or url_for("backoffice_web.collective_offer.list_collective_offers"), 303)
