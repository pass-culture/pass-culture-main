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
from pcapi.core.operations import api as operations_api
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice import search_utils
from pcapi.routes.backoffice import utils
from pcapi.utils.clean_accents import clean_accents

from . import forms as operations_forms


operations_blueprint = utils.child_backoffice_blueprint(
    "operations",
    __name__,
    url_prefix="/operations/",
    permission=perm_models.Permissions.MANAGE_SPECIAL_EVENTS,
)


@operations_blueprint.route("", methods=["GET"])
@atomic()
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
@atomic()
def create_event() -> utils.BackofficeResponse:
    form = operations_forms.CreateSpecialEventForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for(".list_events"), code=303)

    try:
        special_event = operations_api.create_special_event_from_typeform(form.typeform_id.data)
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
@atomic()
def get_event_details(special_event_id: int) -> utils.BackofficeResponse:
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

    response_rows = (
        db.session.query(
            operations_models.SpecialEventResponse,
            full_answers_subquery.label("full_answers"),
        )
        .filter(operations_models.SpecialEventResponse.eventId == special_event_id)
        .options(
            sa.orm.joinedload(operations_models.SpecialEventResponse.user).load_only(
                users_models.User.id,
                users_models.User.firstName,
                users_models.User.lastName,
                users_models.User.phoneNumber,
                users_models.User.email,
                users_models.User.roles,
            ),
        )
        .order_by(operations_models.SpecialEventResponse.dateSubmitted.desc())
    ).all()

    return render_template(
        "operations/details.html",
        special_event=special_event,
        response_rows=response_rows,
        active_tab=request.args.get("active_tab", "responses"),
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/validate", methods=["POST"])
@atomic()
def validate_response(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    response = operations_models.SpecialEventResponse.query.filter_by(id=response_id).one_or_none()
    if not response:
        raise NotFound()

    response.status = operations_models.SpecialEventResponseStatus.VALIDATED
    db.session.add(response)

    return redirect(
        url_for(
            "backoffice_web.operations.get_event_details",
            special_event_id=special_event_id,
        ),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/preselect", methods=["POST"])
@atomic()
def preselect_response(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    response = operations_models.SpecialEventResponse.query.filter_by(id=response_id).one_or_none()
    if not response:
        raise NotFound()

    response.status = operations_models.SpecialEventResponseStatus.PRESELECTED
    db.session.add(response)

    return redirect(
        url_for(
            "backoffice_web.operations.get_event_details",
            special_event_id=special_event_id,
        ),
        303,
    )


@operations_blueprint.route("/<int:special_event_id>/responses/<int:response_id>/reject", methods=["POST"])
@atomic()
def reject_response(special_event_id: int, response_id: int) -> utils.BackofficeResponse:
    response = operations_models.SpecialEventResponse.query.filter_by(id=response_id).one_or_none()
    if not response:
        raise NotFound()

    response.status = operations_models.SpecialEventResponseStatus.REJECTED
    db.session.add(response)

    return redirect(
        url_for(
            "backoffice_web.operations.get_event_details",
            special_event_id=special_event_id,
        ),
        303,
    )
