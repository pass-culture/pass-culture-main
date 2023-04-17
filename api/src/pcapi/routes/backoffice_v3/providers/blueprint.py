from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core.permissions import models as perm_models
from pcapi.models import db

from . import forms
from .. import autocomplete
from .. import utils
from ..forms import empty as empty_forms
from .contexts import get_context


providers_blueprint = utils.child_backoffice_blueprint(
    "providers",
    __name__,
    url_prefix="/pro/providers",
    permission=perm_models.Permissions.MANAGE_PROVIDERS,
)


@providers_blueprint.route("", methods=["GET"])
def get_providers() -> utils.BackofficeResponse:
    return render_template(
        "providers/get.html",
        active_tab=request.args.get("active_tab", "allocine"),
    )


@providers_blueprint.route("/<string:name>", methods=["GET"])
def list_providers(name: str) -> utils.BackofficeResponse:
    provider_context = get_context(name)

    form = forms.SearchProviderForm(formdata=utils.get_query_params())
    if not form.validate():
        return (
            render_template(
                f"providers/get/{name}.html", rows=[], form=form, dst=url_for(".list_providers", name=name)
            ),
            400,
        )

    rows = provider_context.list_providers(form.q.data)

    return render_template(
        f"providers/get/{name}.html", rows=rows, form=form, dst=url_for(".list_providers", name=name)
    )


@providers_blueprint.route("/<string:name>/create", methods=["GET"])
def get_create_provider_form(name: str) -> utils.BackofficeResponse:
    provider_context = get_context(name)

    form = provider_context.get_form()
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".create_provider", name=name),
        div_id=f"create-{name}",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un pivot",
        button_text="Créer le pivot",
    )


@providers_blueprint.route("/<string:name>/create", methods=["POST"])
def create_provider(name: str) -> utils.BackofficeResponse:
    provider_context = get_context(name)

    form = provider_context.get_form()
    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for(".get_providers", active_tab=name), code=303)

    try:
        provider_context.create_provider(form)
        db.session.commit()
    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {exc}", "warning")
    else:
        flash("Le pivot a été créé", "success")

    return redirect(url_for(".get_providers", active_tab=name), code=303)


@providers_blueprint.route("/<string:name>/<int:provider_id>/update", methods=["GET"])
def get_update_provider_form(name: str, provider_id: int) -> utils.BackofficeResponse:
    provider_context = get_context(name)

    form = provider_context.get_form(provider_id)
    autocomplete.prefill_venues_choices(form.venue_id)

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".update_provider", name=name, provider_id=provider_id),
        div_id=f"update-{name}-{provider_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Modifier le pivot {name}",
        button_text="Valider",
    )


@providers_blueprint.route("/<string:name>/<int:provider_id>/update", methods=["POST"])
def update_provider(name: str, provider_id: int) -> utils.BackofficeResponse:
    provider_context = get_context(name)

    form = provider_context.get_form()
    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for(".get_providers", active_tab=name), code=303)

    try:
        provider_context.update_provider(form, provider_id)
        db.session.commit()
    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {exc}", "warning")
    else:
        flash("Le pivot a été mis à jour", "success")

    return redirect(url_for(".get_providers", active_tab=name), code=303)


@providers_blueprint.route("/<string:name>/<int:provider_id>/delete", methods=["GET"])
def get_delete_provider_form(name: str, provider_id: int) -> utils.BackofficeResponse:
    return render_template(
        "components/turbo/modal_form.html",
        form=empty_forms.EmptyForm(),
        dst=url_for(".delete_provider", name=name, provider_id=provider_id),
        div_id=f"delete-{name}-{provider_id}",  # must be consistent with parameter passed to build_lazy_modal
        title=f"Supprimer le pivot {name}",
        button_text="Confirmer",
        information="Le pivot sera définitivement supprimé de la base de données. Veuillez confirmer ce choix.",
    )


@providers_blueprint.route("/<string:name>/<int:provider_id>/delete", methods=["POST"])
def delete_provider(name: str, provider_id: int) -> utils.BackofficeResponse:
    provider_context = get_context(name)

    try:
        provider_context.delete_provider(provider_id)
        db.session.commit()
    except sa.exc.IntegrityError as exc:
        db.session.rollback()
        flash(f"Une erreur s'est produite : {exc}", "warning")
    else:
        flash("Le pivot a été supprimé", "success")

    return redirect(url_for(".get_providers", active_tab=name), code=303)
