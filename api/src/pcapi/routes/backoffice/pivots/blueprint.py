from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerer_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db

from . import forms
from .. import autocomplete
from .. import utils
from ..forms import empty as empty_forms
from .contexts import get_context


pivots_blueprint = utils.child_backoffice_blueprint(
    "pivots",
    __name__,
    url_prefix="/pro/pivots",
    permission=perm_models.Permissions.MANAGE_TECH_PARTNERS,
)


@pivots_blueprint.route("", methods=["GET"])
def get_pivots() -> utils.BackofficeResponse:
    return render_template(
        "pivots/get.html",
        active_tab=request.args.get("active_tab", "allocine"),
    )


@pivots_blueprint.route("/<string:name>", methods=["GET"])
def list_pivots(name: str) -> utils.BackofficeResponse:
    pivot_context = get_context(name)

    form = forms.SearchPivotForm(formdata=utils.get_query_params())
    if not form.validate():
        return (
            render_template(f"pivots/get/{name}.html", rows=[], form=form, dst=url_for(".list_pivots", name=name)),
            400,
        )

    rows = pivot_context.list_pivots(form.q.data)

    return render_template(f"pivots/get/{name}.html", rows=rows, form=form, dst=url_for(".list_pivots", name=name))


@pivots_blueprint.route("/<string:name>/create", methods=["GET"])
def get_create_pivot_form(name: str) -> utils.BackofficeResponse:
    pivot_context = get_context(name)

    form = pivot_context.get_form()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".create_pivot", name=name),
        div_id=f"create-{name}",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un pivot",
        button_text="Créer le pivot",
    )


@pivots_blueprint.route("/<string:name>/create", methods=["POST"])
def create_pivot(name: str) -> utils.BackofficeResponse:
    pivot_context = get_context(name)

    form = pivot_context.get_form()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for(".get_pivots", active_tab=name), code=303)

    venue = offerer_models.Venue.query.filter_by(id=form.venue_id.data[0]).one_or_none()
    if not venue:
        flash(Markup("Le lieu id={venue_id} n'existe pas").format(venue_id=form.venue_id.data[0]), "warning")
        return redirect(url_for(".get_pivots", active_tab=name), code=303)

    try:
        can_create_pivot = pivot_context.create_pivot(form)
        if can_create_pivot:
            history_api.add_action(
                action_type=history_models.ActionType.PIVOT_CREATED,
                author=current_user,
                venue=venue,
                cinema_id=pivot_context.get_cinema_id(form),
                pivot_name=name,
            )
            db.session.commit()
    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        if can_create_pivot:
            flash("Le nouveau pivot a été créé", "success")

    return redirect(url_for(".get_pivots", active_tab=name), code=303)


@pivots_blueprint.route("/<string:name>/<int:pivot_id>/update", methods=["GET"])
def get_update_pivot_form(name: str, pivot_id: int) -> utils.BackofficeResponse:
    pivot_context = get_context(name)

    form = pivot_context.get_edit_form(pivot_id)
    autocomplete.prefill_venues_choices(form.venue_id)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".update_pivot", name=name, pivot_id=pivot_id),
        div_id=f"update-{name}-{pivot_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Modifier le pivot {name}",
        button_text="Valider",
    )


@pivots_blueprint.route("/<string:name>/<int:pivot_id>/update", methods=["POST"])
def update_pivot(name: str, pivot_id: int) -> utils.BackofficeResponse:
    pivot_context = get_context(name)

    form = pivot_context.get_edit_form(pivot_id)
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for(".get_pivots", active_tab=name), code=303)

    try:
        can_update_pivot = pivot_context.update_pivot(form, pivot_id)
        if can_update_pivot:
            db.session.commit()
    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        if can_update_pivot:
            flash("Le pivot a été mis à jour", "success")

    return redirect(url_for(".get_pivots", active_tab=name), code=303)


@pivots_blueprint.route("/<string:name>/<int:pivot_id>/delete", methods=["GET"])
def get_delete_pivot_form(name: str, pivot_id: int) -> utils.BackofficeResponse:
    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for(".delete_pivot", name=name, pivot_id=pivot_id),
        div_id=f"delete-{name}-{pivot_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Supprimer le pivot {name}",
        button_text="Confirmer",
        information="Le pivot sera définitivement supprimé de la base de données. Veuillez confirmer ce choix.",
    )


@pivots_blueprint.route("/<string:name>/<int:pivot_id>/delete", methods=["POST"])
def delete_pivot(name: str, pivot_id: int) -> utils.BackofficeResponse:
    pivot_context = get_context(name)

    try:
        can_delete_pivot = pivot_context.delete_pivot(pivot_id)
        if can_delete_pivot:
            db.session.commit()
    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
    else:
        if can_delete_pivot:
            flash("Le pivot a été supprimé", "success")
        else:
            flash(
                (
                    "Le pivot ne peut pas être supprimé si la synchronisation de ce cinéma est active. "
                    "Supprimez la synchronisation et vous pourrez supprimer le pivot."
                ),
                "warning",
            )

    return redirect(url_for(".get_pivots", active_tab=name), code=303)
