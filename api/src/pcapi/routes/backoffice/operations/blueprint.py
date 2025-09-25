import re
import typing
from datetime import date
from functools import partial

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from dateutil.relativedelta import relativedelta
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from werkzeug.exceptions import NotFound

from pcapi.connectors import typeform
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.operations import api as operations_api
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.filters import format_special_event_response_status_str
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.search_utils import paginate
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import mark_transaction_as_invalid

from . import forms as operations_forms


operations_blueprint = utils.child_backoffice_blueprint(
    "operations",
    __name__,
    url_prefix="/operations/",
    permission=perm_models.Permissions.READ_SPECIAL_EVENTS,
)


def _render_responses_rows(special_event_id: int, responses_ids: list[int]) -> utils.BackofficeResponse:
    if not responses_ids:
        return render_template("operations/details/rows.html", items=[])

    if responses_ids:
        query = _get_response_rows_query()
        query = search_utils.apply_filter_on_beneficiary_status(query, [])
        if len(responses_ids) == 1:
            query = query.filter(operations_models.SpecialEventResponse.id == responses_ids[0])
        else:
            query = query.filter(operations_models.SpecialEventResponse.id.in_(responses_ids))

    special_event = (
        db.session.query(operations_models.SpecialEvent)
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .first()
    )
    stats = _get_special_event_stats(special_event_id)

    return render_template(
        "operations/details/partial_response_container.html",
        items=query.all(),
        special_event=special_event,
        stats=stats,
    )


@operations_blueprint.route("", methods=["GET"])
def list_events() -> utils.BackofficeResponse:
    form = operations_forms.SearchSpecialEventForm(formdata=utils.get_query_params())
    if not form.validate():
        return (
            render_template(
                "operations/list_events.html",
                form=form,
                dst=url_for(".list_events"),
                create_form=operations_forms.CreateSpecialEventForm(),
            ),
            400,
        )

    query = db.session.query(operations_models.SpecialEvent)
    if form.q.data:
        search_query = f"%{clean_accents(form.q.data.replace(' ', '%').replace('-', '%'))}%"
        query_filter: sa.sql.elements.ColumnElement[bool] = sa.func.immutable_unaccent(
            operations_models.SpecialEvent.title
        ).ilike(search_query)

        if re.match(operations_forms.RE_TYPEFORM_ID, form.q.data):
            query_filter = sa.or_(
                query_filter,
                operations_models.SpecialEvent.externalId == form.q.data,
            )

        query = query.filter(query_filter)

    paginated_rows = paginate(
        query=query.order_by(operations_models.SpecialEvent.dateCreated.desc()),
        page=int(form.page.data),
        per_page=int(form.limit.data),
    )

    form_url = partial(url_for, ".list_events", **form.raw_data)
    next_pages_urls = search_utils.pagination_links(form_url, int(form.page.data), paginated_rows.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    return render_template(
        "operations/list_events.html",
        form=form,
        dst=url_for(".list_events"),
        rows=paginated_rows,
        next_pages_urls=next_pages_urls,
        create_form=operations_forms.CreateSpecialEventForm(),
    )


@operations_blueprint.route("", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def create_event() -> utils.BackofficeResponse:
    form = operations_forms.CreateSpecialEventForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for(".list_events"), code=303)

    try:
        special_event = operations_api.create_special_event_from_typeform(
            form_id=form.typeform_id.data,
            event_date=form.event_date.data,
            end_import_date=form.end_import_date.data,
            venue_id=int(form.venue.data[0]) if (form.venue.data and form.venue.data[0]) else None,
        )
    except typeform.NotFoundException:
        mark_transaction_as_invalid()
        flash(
            Markup("Le formulaire <b>{form_id}</b> n'a pas été trouvé sur Typeform.").format(
                form_id=form.typeform_id.data
            ),
            "warning",
        )
    except typeform.TypeformException as exc:
        mark_transaction_as_invalid()
        flash(
            Markup("Une erreur s'est produite lors de la connexion à Typeform :<br/>{message}").format(
                message=str(exc)
            ),
            "warning",
        )
    except sa.exc.IntegrityError:
        mark_transaction_as_invalid()
        flash("Cette opération spéciale a déjà été importée.", "warning")
    else:
        flash(
            Markup("L'opération spéciale <b>{title}</b> a été importée.").format(title=special_event.title), "success"
        )

    return redirect(url_for(".list_events"), code=303)


def _get_special_event_stats(special_event_id: int) -> tuple[int]:
    base_query = db.session.query(
        sa.func.count(operations_models.SpecialEventResponse.id),
    ).filter(
        operations_models.SpecialEventResponse.eventId == special_event_id,
    )

    total_candidature_count_subquery = base_query.scalar_subquery()

    new_candidature_count_subquery = base_query.filter(
        operations_models.SpecialEventResponse.status == operations_models.SpecialEventResponseStatus.NEW,
    ).scalar_subquery()

    to_contact_candidature_count_subquery = base_query.filter(
        operations_models.SpecialEventResponse.status == operations_models.SpecialEventResponseStatus.PRESELECTED,
    ).scalar_subquery()

    waiting_candidature_count_subquery = base_query.filter(
        operations_models.SpecialEventResponse.status == operations_models.SpecialEventResponseStatus.WAITING,
    ).scalar_subquery()

    validated_candidature_count_subquery = base_query.filter(
        operations_models.SpecialEventResponse.status == operations_models.SpecialEventResponseStatus.VALIDATED,
    ).scalar_subquery()

    backup_candidature_count_subquery = base_query.filter(
        operations_models.SpecialEventResponse.status == operations_models.SpecialEventResponseStatus.BACKUP,
    ).scalar_subquery()

    return db.session.query(
        total_candidature_count_subquery.label("total"),
        new_candidature_count_subquery.label("new"),
        waiting_candidature_count_subquery.label("waiting"),
        to_contact_candidature_count_subquery.label("to_contact"),
        validated_candidature_count_subquery.label("validated"),
        backup_candidature_count_subquery.label("backup"),
    ).one()


def _get_response_rows_query() -> sa_orm.Query:
    full_answers_subquery = (
        db.session.query(
            sa.func.jsonb_object_agg(
                operations_models.SpecialEventAnswer.questionId, operations_models.SpecialEventAnswer.text
            )
        )
        .filter(
            operations_models.SpecialEventAnswer.responseId == operations_models.SpecialEventResponse.id,
        )
        .correlate(operations_models.SpecialEventResponse)
        .scalar_subquery()
    )

    aliased_response = sa_orm.aliased(operations_models.SpecialEventResponse)
    try_count_query = (
        db.session.query(sa.func.count(aliased_response.id))
        .filter(
            aliased_response.userId == operations_models.SpecialEventResponse.userId,
            aliased_response.userId.is_not(None),
        )
        .correlate(operations_models.SpecialEventResponse)
    )

    try_count_subquery = try_count_query.scalar_subquery()
    selected_count_subquery = try_count_query.filter(
        aliased_response.status == operations_models.SpecialEventResponseStatus.VALIDATED
    ).scalar_subquery()

    account_tags_subquery = (
        sa.select(sa.func.array_agg(sa.func.coalesce(users_models.UserTag.label, users_models.UserTag.name)))
        .select_from(users_models.UserTag)
        .join(users_models.UserTagMapping)
        .filter(users_models.UserTagMapping.userId == users_models.User.id)
        .correlate(users_models.User)
        .scalar_subquery()
    )

    response_rows_query = db.session.query(
        operations_models.SpecialEventResponse,
        full_answers_subquery.label("full_answers"),
        try_count_subquery.label("try_count"),
        selected_count_subquery.label("selected_count"),
        account_tags_subquery.label("account_tags"),
    ).outerjoin(operations_models.SpecialEventResponse.user)

    response_rows_query = response_rows_query.options(
        sa_orm.contains_eager(operations_models.SpecialEventResponse.user)
        .load_only(
            users_models.User.id,
            users_models.User.email,
            users_models.User.firstName,
            users_models.User.lastName,
            users_models.User.roles,
            users_models.User.departementCode,
        )
        .contains_eager(users_models.User.deposits)
        .load_only(
            finance_models.Deposit.expirationDate,
            finance_models.Deposit.type,
            finance_models.Deposit.version,
        ),
    ).order_by(operations_models.SpecialEventResponse.dateSubmitted.desc())
    return response_rows_query


def _get_special_event_responses(
    special_event_id: int,
    response_form: operations_forms.OperationResponseForm,
) -> typing.Any:
    response_rows_query = _get_response_rows_query()

    response_rows_filters = [operations_models.SpecialEventResponse.eventId == special_event_id]
    if response_status_data := response_form.response_status.data:
        response_rows_filters.append(operations_models.SpecialEventResponse.status.in_(response_status_data))

    if response_ages_data := response_form.age.data:
        age_filters = []
        for age in response_ages_data:
            start = date.today() - relativedelta(years=int(age) + 1)
            end = date.today() - relativedelta(years=int(age))
            age_filters.append(users_models.User.validatedBirthDate.between(start, end))
        response_rows_filters.append(sa.or_(*age_filters))

    if response_departments_data := response_form.department.data:
        response_rows_filters.append(users_models.User.departementCode.in_(response_departments_data))

    if response_form.response.data["question"] and response_form.response.data["response"]:
        response_rows_filters.append(
            operations_models.SpecialEventResponse.id.in_(
                db.session.query(operations_models.SpecialEventAnswer.responseId).filter(
                    operations_models.SpecialEventAnswer.questionId == response_form.response.data["question"],
                    sa.func.immutable_unaccent(operations_models.SpecialEventAnswer.text).ilike(
                        sa.func.immutable_unaccent(f"%{response_form.response.data['response']}%"),
                    ),
                ),
            )
        )

    response_rows_query = response_rows_query.filter(*response_rows_filters)
    response_rows_query = search_utils.apply_filter_on_beneficiary_status(
        response_rows_query,
        response_form.eligibility.data,
    )

    return paginate(
        query=response_rows_query,
        page=int(response_form.page.data),
        per_page=int(response_form.limit.data),
    )


@operations_blueprint.route("/<int:special_event_id>", methods=["GET"])
def get_event_details(special_event_id: int) -> utils.BackofficeResponse:
    special_event_query = (
        db.session.query(
            operations_models.SpecialEvent,
        )
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .options(
            sa_orm.joinedload(operations_models.SpecialEvent.questions).load_only(
                operations_models.SpecialEventQuestion.id,
                operations_models.SpecialEventQuestion.externalId,
                operations_models.SpecialEventQuestion.title,
            ),
            sa_orm.joinedload(operations_models.SpecialEvent.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
            ),
        )
    )
    special_event = special_event_query.one_or_none()

    if not special_event:
        raise NotFound()

    response_form = operations_forms.OperationResponseForm(
        formdata=utils.get_query_params(), questions=special_event.questions
    )
    if not response_form.validate():
        flash(utils.build_form_error_msg(response_form), "warning")
        return redirect(url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id), 303)

    stats = _get_special_event_stats(special_event_id)
    paginated_responses = _get_special_event_responses(
        special_event_id=special_event_id,
        response_form=response_form,
    )

    next_page = partial(url_for, ".get_event_details", special_event_id=special_event_id, **response_form.raw_data)
    next_pages_urls = search_utils.pagination_links(next_page, int(response_form.page.data), paginated_responses.pages)
    return render_template(
        "operations/details.html",
        special_event=special_event,
        stats=stats,
        rows=paginated_responses,
        response_form=response_form,
        next_pages_urls=next_pages_urls,
    )


def _set_responses_status(
    special_event_id: int,
    responses_ids: list[int],
    new_status: operations_models.SpecialEventResponseStatus,
) -> int:
    return (
        db.session.query(
            operations_models.SpecialEventResponse,
        )
        .filter(
            operations_models.SpecialEventResponse.eventId == special_event_id,
            operations_models.SpecialEventResponse.id.in_(responses_ids),
        )
        .update(
            {"status": new_status},
            synchronize_session=False,
        )
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/set-status", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def set_response_status(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    form = operations_forms.UpdateResponseStatusForm()

    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return _render_responses_rows(special_event_id, [])

    response_status = form.response_status.data
    if response_status == operations_models.SpecialEventResponseStatus.NEW:
        flash(
            'Une réponse ne pas pas être passée à l\'état "{format_special_event_response_status_str(response_status)}"',
            "warning",
        )
        return _render_responses_rows(special_event_id, [])

    updated = _set_responses_status(special_event_id, [response_id], response_status)

    if updated:
        flash(
            f'La réponse {response_id} est maintenant "{format_special_event_response_status_str(response_status)}"',
            "info",
        )
    else:
        flash(f"La réponse {response_id} n'existe pas", "warning")

    return _render_responses_rows(special_event_id, [response_id])


@operations_blueprint.route(
    "/<int:special_event_id>/responses/set-status/<string:response_status>/batch", methods=["GET"]
)
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_batch_update_responses_status_form(special_event_id: int, response_status: str) -> utils.BackofficeResponse:
    event = db.session.query(operations_models.SpecialEvent.id).filter_by(id=special_event_id).one_or_none()
    if not event:
        raise NotFound()

    new_status = getattr(operations_models.SpecialEventResponseStatus, response_status.upper(), None)
    if not new_status or new_status == operations_models.SpecialEventResponseStatus.NEW:
        raise NotFound()

    form = empty_forms.BatchForm(request.args)

    return render_template(
        "components/dynamic/modal_form.html",
        target_id="#operation-table",
        form=form,
        dst=url_for(
            "backoffice_web.operations.batch_validate_responses_status",
            special_event_id=special_event_id,
            response_status=new_status.value.lower(),
        ),
        div_id=f"batch-response-{new_status.value.lower()}-modal",
        title=f'Voulez-vous passer les candidatures sélectionnées  à "{format_special_event_response_status_str(new_status)}" ?',
        button_text="Valider",
    )


@operations_blueprint.route(
    "/<int:special_event_id>/responses/set-status/<string:response_status>/batch-validate", methods=["POST"]
)
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def batch_validate_responses_status(special_event_id: int, response_status: str) -> utils.BackofficeResponse:
    event = (
        db.session.query(operations_models.SpecialEvent.id)
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .one_or_none()
    )

    if not event:
        raise NotFound()

    new_status = getattr(operations_models.SpecialEventResponseStatus, response_status.upper(), None)
    if not new_status or new_status == operations_models.SpecialEventResponseStatus.NEW:
        raise NotFound()

    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return _render_responses_rows(special_event_id, [])

    _set_responses_status(
        special_event_id=special_event_id,
        responses_ids=form.object_ids_list,
        new_status=new_status,
    )

    flash(f'Les candidatures ont été passées à "{format_special_event_response_status_str(new_status)}".', "success")
    return _render_responses_rows(special_event_id, form.object_ids_list)


@operations_blueprint.route("/<int:special_event_id>/update-event-date", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_update_date_event(special_event_id: int) -> utils.BackofficeResponse:
    event = db.session.query(operations_models.SpecialEvent.eventDate).filter_by(id=special_event_id).one_or_none()
    if not event:
        raise NotFound()

    form = operations_forms.UpdateEventDateForm()
    form.date.data = event.eventDate

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.operations.update_date_event",
            special_event_id=special_event_id,
        ),
        div_id="update-event-date-modal",
        title="Modifier la date de l'évènement",
        button_text="Valider",
    )


@operations_blueprint.route("/<int:special_event_id>/update-event-date", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def update_date_event(special_event_id: int) -> utils.BackofficeResponse:
    event = (
        db.session.query(operations_models.SpecialEvent.id)
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .one_or_none()
    )
    if not event:
        raise NotFound()

    form = operations_forms.UpdateEventDateForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    db.session.query(operations_models.SpecialEvent).filter(
        operations_models.SpecialEvent.id == special_event_id
    ).update({"eventDate": form.date.data}, synchronize_session=False)

    flash("La date de l'évènement a été mise à jour", "success")
    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/update-end-import-date", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_update_end_import_date_event(special_event_id: int) -> utils.BackofficeResponse:
    event = db.session.query(operations_models.SpecialEvent.endImportDate).filter_by(id=special_event_id).one_or_none()
    if not event:
        raise NotFound()

    form = operations_forms.UpdateEventDateForm()
    form.date.data = event.endImportDate

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.operations.update_end_import_date",
            special_event_id=special_event_id,
        ),
        div_id="update-end-import-date-modal",
        title="Modifier la date de clôture des candidatures",
        button_text="Valider",
    )


@operations_blueprint.route("/<int:special_event_id>/update-end-import-date", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def update_end_import_date(special_event_id: int) -> utils.BackofficeResponse:
    event = (
        db.session.query(operations_models.SpecialEvent.id)
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .one_or_none()
    )
    if not event:
        raise NotFound()

    form = operations_forms.UpdateEventDateForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    db.session.query(operations_models.SpecialEvent).filter(
        operations_models.SpecialEvent.id == special_event_id
    ).update({"endImportDate": form.date.data}, synchronize_session=False)

    flash("La date de fin d'import des candidatures a été mise à jour", "success")
    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/update-venue", methods=["GET"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_update_venue_form(special_event_id: int) -> utils.BackofficeResponse:
    from pcapi.routes.backoffice.autocomplete import prefill_venues_choices

    event = (
        db.session.query(operations_models.SpecialEvent.venueId)
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .one_or_none()
    )
    if not event:
        raise NotFound()

    form = operations_forms.UpdateEventVenueForm()
    if event.venueId:
        form.venue.data = [str(event.venueId)]
        prefill_venues_choices(form.venue)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(
            "backoffice_web.operations.update_venue",
            special_event_id=special_event_id,
        ),
        div_id="update-venue-modal",
        title="Modifier le partenaire culturel",
        button_text="Valider",
    )


@operations_blueprint.route("/<int:special_event_id>/update-venue", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def update_venue(special_event_id: int) -> utils.BackofficeResponse:
    event = (
        db.session.query(operations_models.SpecialEvent.id)
        .filter(operations_models.SpecialEvent.id == special_event_id)
        .one_or_none()
    )
    if not event:
        raise NotFound()

    form = operations_forms.UpdateEventVenueForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(
            request.referrer
            or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
            303,
        )

    db.session.query(operations_models.SpecialEvent).filter(
        operations_models.SpecialEvent.id == special_event_id,
    ).update(
        {
            "venueId": form.venue.data,
        },
        synchronize_session=False,
    )

    flash("Le partenaire culturel a été mis à jour", "success")
    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )
