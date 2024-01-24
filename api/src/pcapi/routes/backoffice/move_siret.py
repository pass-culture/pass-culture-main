from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from markupsafe import escape

from pcapi.core.finance import siret_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models

from . import utils
from .forms import pro_support as pro_support_forms


move_siret_blueprint = utils.child_backoffice_blueprint(
    "move_siret",
    __name__,
    url_prefix="/pro/support/move_siret",
    permission=perm_models.Permissions.MOVE_SIRET,
)


def _validate_move_siret_form() -> (
    tuple[pro_support_forms.MoveSiretForm, offerers_models.Venue | None, offerers_models.Venue | None]
):
    form = pro_support_forms.MoveSiretForm()
    if not form.validate():
        return form, None, None

    if form.source_venue.data == form.target_venue.data:
        flash("Les lieux source et destination doivent être différents", "warning")
        return form, None, None

    source_venue = offerers_models.Venue.query.filter_by(id=form.source_venue.data).one_or_none()
    if not source_venue:
        flash(
            Markup("Aucun lieu n'a été trouvé avec l'ID <b>{venue_id}</b>").format(venue_id=form.source_venue.data),
            "warning",
        )
        return form, None, None

    target_venue = offerers_models.Venue.query.filter_by(id=form.target_venue.data).one_or_none()
    if not target_venue:
        flash(
            Markup("Aucun lieu n'a été trouvé avec l'ID <b>{venue_id}</b>").format(venue_id=form.target_venue.data),
            "warning",
        )
        return form, None, None

    if source_venue.siret != form.siret.data:
        flash(
            Markup("Le SIRET <b>{siret}</b> ne correspond pas au lieu <b>{venue_id}</b>").format(
                siret=form.siret.data, venue_id=form.source_venue.data
            ),
            "warning",
        )
        return form, None, None

    if target_venue.isVirtual:
        flash(
            Markup("Le lieu cible <b>{venue_name}</b> (ID {venue_id}) est un lieu virtuel").format(
                venue_name=target_venue.name, venue_id=target_venue.id
            ),
            "warning",
        )
        return form, None, None

    return form, source_venue, target_venue


def _render_form_page(form: pro_support_forms.MoveSiretForm, code: int = 200) -> utils.BackofficeResponse:
    return render_template("pro/move_siret.html", form=form, dst=url_for(".post_move_siret")), code


def _render_confirmation_page(
    form: pro_support_forms.MoveSiretForm,
    source_venue: offerers_models.Venue,
    target_venue: offerers_models.Venue,
    code: int = 200,
) -> utils.BackofficeResponse:
    return (
        render_template(
            "pro/move_siret_confirmation.html",
            form=form,
            dst=url_for(".apply_move_siret"),
            source_venue=source_venue,
            target_venue=target_venue,
            target_yearly_revenue=siret_api.get_yearly_revenue(target_venue.id),
        ),
        code,
    )


@move_siret_blueprint.route("", methods=["GET"])
def move_siret() -> utils.BackofficeResponse:
    form = pro_support_forms.MoveSiretForm()
    return _render_form_page(form)


@move_siret_blueprint.route("", methods=["POST"])
def post_move_siret() -> utils.BackofficeResponse:
    form, source_venue, target_venue = _validate_move_siret_form()
    if not source_venue or not target_venue:
        return _render_form_page(form, code=400)

    try:
        siret_api.check_can_move_siret(
            source_venue,
            target_venue,
            form.siret.data,
            bool(form.override_revenue_check.data),
        )
    except siret_api.CheckError as exc:
        flash(escape(str(exc)), "warning")
        return _render_form_page(form, code=400)

    return _render_confirmation_page(form, source_venue, target_venue)


@move_siret_blueprint.route("/apply", methods=["POST"])
def apply_move_siret() -> utils.BackofficeResponse:
    form, source_venue, target_venue = _validate_move_siret_form()
    if not source_venue or not target_venue:
        return _render_form_page(form, code=400)

    try:
        siret_api.move_siret(
            source_venue,
            target_venue,
            form.siret.data,
            form.comment.data,
            apply_changes=True,
            override_revenue_check=bool(form.override_revenue_check.data),
            author_user_id=current_user.id,
        )
    except siret_api.CheckError as exc:
        flash(Markup("La vérification a échoué : {message}").format(message=str(exc)), "warning")
        return _render_confirmation_page(form, source_venue, target_venue, code=400)
    except Exception as exc:  # pylint: disable=broad-except
        flash(Markup("Une erreur s'est produite : {message}").format(message=str(exc)), "warning")
        return _render_confirmation_page(form, source_venue, target_venue, code=400)

    flash(
        Markup(
            "Le SIRET <b>{siret}</b> a été déplacé de <b>{source_name}</b> ({source_id}) vers <b>{target_name}</b> ({target_id})",
        ).format(
            siret=form.siret.data,
            source_name=source_venue.name,
            source_id=source_venue.id,
            target_name=target_venue.name,
            target_id=target_venue.id,
        ),
        "success",
    )
    return redirect(url_for(".move_siret"), code=303)
