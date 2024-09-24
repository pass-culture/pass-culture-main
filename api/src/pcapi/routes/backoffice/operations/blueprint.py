from functools import partial
import re

from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from markupsafe import Markup
import sqlalchemy as sa

from pcapi.connectors import typeform
from pcapi.core.operations import api as operations_api
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
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
