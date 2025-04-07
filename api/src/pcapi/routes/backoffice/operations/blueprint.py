from functools import partial
import re

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.connectors import typeform
from pcapi.core.finance import models as finance_models
from pcapi.core.operations import api as operations_api
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.utils.clean_accents import clean_accents

from . import forms as operations_forms


operations_blueprint = utils.child_backoffice_blueprint(
    "operations",
    __name__,
    url_prefix="/operations/",
    permission=perm_models.Permissions.READ_SPECIAL_EVENTS,
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

    query = operations_models.SpecialEvent.query
    if form.q.data:
        search_query = f"%{clean_accents(form.q.data.replace(' ', '%').replace('-', '%'))}%"
        query_filter = sa.func.immutable_unaccent(operations_models.SpecialEvent.title).ilike(search_query)

        if re.match(operations_forms.RE_TYPEFORM_ID, form.q.data):
            query_filter = sa.or_(query_filter, operations_models.SpecialEvent.externalId == form.q.data)

        query = query.filter(query_filter)

    paginated_rows = query.order_by(operations_models.SpecialEvent.dateCreated.desc()).paginate(
        page=int(form.page.data),
        per_page=int(form.per_page.data),
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


@operations_blueprint.route("/<int:special_event_id>", methods=["GET"])
def get_event_details(special_event_id: int) -> utils.BackofficeResponse:
    response_form = operations_forms.OperationResponseForm(formdata=utils.get_query_params())
    if not response_form.validate():
        flash(utils.build_form_error_msg(response_form), "warning")
        return redirect(url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id), 303)

    response_rows_filters = [operations_models.SpecialEventResponse.eventId == special_event_id]
    if response_status_data := response_form.response_status.data:
        response_rows_filters.append(operations_models.SpecialEventResponse.status.in_(response_status_data))

    special_event_query = operations_models.SpecialEvent.query.filter(
        operations_models.SpecialEvent.id == special_event_id
    ).options(
        sa.orm.joinedload(operations_models.SpecialEvent.questions).load_only(
            operations_models.SpecialEventQuestion.id,
            operations_models.SpecialEventQuestion.externalId,
            operations_models.SpecialEventQuestion.title,
        )
    )
    special_event = special_event_query.one_or_none()

    if not special_event:
        raise NotFound()

    full_answers_subquery = (
        db.session.query(
            sa.func.jsonb_object_agg(
                operations_models.SpecialEventAnswer.questionId, operations_models.SpecialEventAnswer.text
            )
        )
        .filter(operations_models.SpecialEventAnswer.responseId == operations_models.SpecialEventResponse.id)
        .correlate(operations_models.SpecialEventResponse)
        .scalar_subquery()
    )

    response_rows_query = (
        db.session.query(
            operations_models.SpecialEventResponse,
            full_answers_subquery.label("full_answers"),
        )
        .filter(*response_rows_filters)
        .outerjoin(operations_models.SpecialEventResponse.user)
    )
    response_rows_query = search_utils.apply_filter_on_beneficiary_status(
        response_rows_query, response_form.eligibility.data
    )
    response_rows = (
        response_rows_query.options(
            sa.orm.contains_eager(operations_models.SpecialEventResponse.user)
            .load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.phoneNumber,
                users_models.User.email,
                users_models.User.roles,
            )
            .contains_eager(users_models.User.deposits)
            .load_only(
                finance_models.Deposit.expirationDate,
                finance_models.Deposit.type,
                finance_models.Deposit.version,
            ),
        )
        .order_by(operations_models.SpecialEventResponse.dateSubmitted.desc())
        .all()
    )

    return render_template(
        "operations/details.html",
        special_event=special_event,
        response_rows=response_rows,
        response_form=response_form,
        active_tab=request.args.get("active_tab", "responses"),
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def validate_response(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    response = operations_models.SpecialEventResponse.query.filter_by(id=response_id).one_or_none()
    if not response:
        raise NotFound()

    response.status = operations_models.SpecialEventResponseStatus.VALIDATED
    db.session.add(response)

    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/preselect", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def preselect_response(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    response = operations_models.SpecialEventResponse.query.filter_by(id=response_id).one_or_none()
    if not response:
        raise NotFound()

    response.status = operations_models.SpecialEventResponseStatus.PRESELECTED
    db.session.add(response)

    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def reject_response(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    response = operations_models.SpecialEventResponse.query.filter_by(id=response_id).one_or_none()
    if not response:
        raise NotFound()

    response.status = operations_models.SpecialEventResponseStatus.REJECTED
    db.session.add(response)

    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/batch/validate", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_batch_validate_responses_form(special_event_id: int) -> utils.BackofficeResponse:
    event = (
        operations_models.SpecialEvent.query.filter_by(id=special_event_id)
        .with_entities(operations_models.SpecialEvent.id)
        .one_or_none()
    )
    if not event:
        raise NotFound()

    alert = None
    form: empty_forms.BatchForm | None = empty_forms.BatchForm()
    if form and (response_ids := form.object_ids_list):
        responses = (
            operations_models.SpecialEventResponse.query.filter(
                operations_models.SpecialEventResponse.id.in_(response_ids),
            )
            .with_entities(operations_models.SpecialEventResponse.id, operations_models.SpecialEventResponse.status)
            .all()
        )
        if len(responses) != len(response_ids) or len(responses) == 0:
            alert = "Certaines candidatures selectionnées sont introuvables."
            form = None
        if all(response.status == operations_models.SpecialEventResponseStatus.VALIDATED for response in responses):
            alert = "Toutes les candidatures séléctionnées ont déjà été retenues. L'action n'aura aucun effet."
            form = None

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.operations.batch_validate_responses", special_event_id=special_event_id),
        div_id="batch-validate-response-modal",
        title="Voulez-vous retenir les candidatures sélectionnées ?",
        button_text="Valider" if form else None,
        alert=alert,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/batch-validate", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def batch_validate_responses(special_event_id: int) -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    responses = operations_models.SpecialEventResponse.query.filter(
        operations_models.SpecialEventResponse.id.in_(form.object_ids_list)
    ).all()
    for response in responses:
        response.status = operations_models.SpecialEventResponseStatus.VALIDATED
        db.session.add(response)
    flash("Les candidatures ont été retenues.", "success")
    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/batch/preselect", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_batch_preselect_responses_form(special_event_id: int) -> utils.BackofficeResponse:
    event = operations_models.SpecialEvent.query.filter_by(id=special_event_id).one_or_none()
    if not event:
        raise NotFound()

    alert = None
    form: empty_forms.BatchForm | None = empty_forms.BatchForm()
    if form and (response_ids := form.object_ids_list):
        responses = operations_models.SpecialEventResponse.query.filter(
            operations_models.SpecialEventResponse.id.in_(response_ids)
        ).all()
        if len(responses) != len(response_ids) or len(responses) == 0:
            alert = "Certaines candidatures selectionnées sont introuvables."
            form = None
        if all(response.status == operations_models.SpecialEventResponseStatus.PRESELECTED for response in responses):
            alert = (
                'Toutes les candidatures séléctionnées sont déjà à l\'état "préselectionné". '
                "L'action n'aura aucun effet."
            )
            form = None

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.operations.batch_preselect_responses", special_event_id=special_event_id),
        div_id="batch-preselect-response-modal",
        title='Voulez-vous passer l\'état les candidatures sélectionnées en "présélectionné" ?',
        button_text="Valider" if form else None,
        alert=alert,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/batch-preselect", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def batch_preselect_responses(special_event_id: int) -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    responses = operations_models.SpecialEventResponse.query.filter(
        operations_models.SpecialEventResponse.id.in_(form.object_ids_list),
        operations_models.SpecialEventResponse.status != operations_models.SpecialEventResponseStatus.PRESELECTED,
    ).all()
    for response in responses:
        response.status = operations_models.SpecialEventResponseStatus.PRESELECTED
        db.session.add(response)
    flash("Les candidatures ont été préselectionnées.", "success")
    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/batch/reject", methods=["GET", "POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def get_batch_reject_responses_form(special_event_id: int) -> utils.BackofficeResponse:
    event = operations_models.SpecialEvent.query.filter_by(id=special_event_id).one_or_none()
    if not event:
        raise NotFound()

    alert = None
    form: empty_forms.BatchForm | None = empty_forms.BatchForm()
    if form and (response_ids := form.object_ids_list):
        responses = operations_models.SpecialEventResponse.query.filter(
            operations_models.SpecialEventResponse.id.in_(response_ids)
        ).all()
        if len(responses) != len(response_ids) or len(responses) == 0:
            alert = "Certaines candidatures selectionnées sont introuvables."
            form = None
        if all(response.status == operations_models.SpecialEventResponseStatus.REJECTED for response in responses):
            alert = "Toutes les candidatures séléctionnées ont déjà été rejetées. L'action n'aura aucun effet."
            form = None

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.operations.batch_reject_responses", special_event_id=special_event_id),
        div_id="batch-reject-response-modal",
        title="Voulez-vous rejeter les candidatures sélectionnées ?",
        button_text="Valider" if form else None,
        alert=alert,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/batch-reject", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_SPECIAL_EVENTS)
def batch_reject_responses(special_event_id: int) -> utils.BackofficeResponse:
    form = empty_forms.BatchForm()
    if not form.validate():
        mark_transaction_as_invalid()
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(request.referrer, 303)

    responses = operations_models.SpecialEventResponse.query.filter(
        operations_models.SpecialEventResponse.id.in_(form.object_ids_list)
    ).all()
    for response in responses:
        response.status = operations_models.SpecialEventResponseStatus.REJECTED
        db.session.add(response)
    flash("Les candidatures ont été rejetées.", "success")
    return redirect(
        request.referrer or url_for("backoffice_web.operations.get_event_details", special_event_id=special_event_id),
        303,
    )
