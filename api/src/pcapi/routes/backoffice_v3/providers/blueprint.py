from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa

from pcapi.core.external import zendesk_sell
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus

from . import forms
from .. import utils


providers_blueprint = utils.child_backoffice_blueprint(
    "providers",
    __name__,
    url_prefix="/pro/providers",
    permission=perm_models.Permissions.ADVANCED_PRO_SUPPORT,
)


@providers_blueprint.route("", methods=["GET"])
def get_providers() -> utils.BackofficeResponse:
    providers = (
        providers_models.Provider.query.options(
            sa.orm.joinedload(providers_models.Provider.offererProvider)
            .joinedload(offerers_models.OffererProvider.offerer)
            .load_only(offerers_models.Offerer.city, offerers_models.Offerer.postalCode, offerers_models.Offerer.siren)
        )
        .options(sa.orm.joinedload(providers_models.Provider.apiKeys).load_only(offerers_models.ApiKey.id))
        .all()
    )
    return render_template("providers/get.html", providers=providers)


@providers_blueprint.route("/new", methods=["GET"])
def get_create_provider_form() -> utils.BackofficeResponse:
    form = forms.CreateProviderForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.providers.create_provider"),
        div_id="create-provider",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un prestataire qui se synchronisera avec le pass Culture",
        button_text="Créer le prestataire",
    )


@providers_blueprint.route("/", methods=["POST"])
def create_provider() -> utils.BackofficeResponse:
    form = forms.CreateProviderForm()

    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.providers.get_providers"), code=303)

    try:
        provider = providers_models.Provider(
            name=form.name.data,
            logoUrl=form.logo_url.data,
            enabledForPro=form.enabled_for_pro.data,
            isActive=form.is_active.data,
        )
        offerer, is_offerer_new = _get_or_create_offerer(form)
        offerer_provider = offerers_models.OffererProvider(offerer=offerer, provider=provider)
        api_key, clear_secret = offerers_api.generate_provider_api_key(provider)

        action_history = history_api.log_action(
            history_models.ActionType.OFFERER_NEW,
            current_user,
            offerer=offerer,
            comment="Création automatique via création de prestataire",
            save=False,
        )

        db.session.add_all([provider, offerer, offerer_provider, api_key, action_history])
        db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce prestataire existe déjà", "warning")
    else:
        if is_offerer_new:
            zendesk_sell.create_offerer(offerer)
        flash(
            f"Le prestataire {provider.name} a été créé. La Clé API ne peut être régénérée ni ré-affichée, veillez à la sauvegarder immédiatement : {clear_secret}",
            "success",
        )

    return redirect(url_for("backoffice_v3_web.providers.get_providers"), code=303)


def _get_or_create_offerer(form: forms.CreateProviderForm) -> tuple[offerers_models.Offerer, bool]:
    offerer = offerers_repository.find_offerer_by_siren(form.siren.data)
    if is_offerer_new := offerer is None:
        offerer = offerers_models.Offerer(
            name=form.name.data,
            siren=form.siren.data,
            city=form.city.data,
            postalCode=form.postal_code.data,
            validationStatus=ValidationStatus.VALIDATED,
        )
    return offerer, is_offerer_new


@providers_blueprint.route("/<int:provider_id>/update", methods=["GET"])
def get_update_provider_form(provider_id: int) -> utils.BackofficeResponse:
    provider = providers_models.Provider.query.get(provider_id)
    form = forms.EditProviderForm(
        name=provider.name,
        logo_url=provider.logoUrl,
        enabled_for_pro=provider.enabledForPro,
        is_active=provider.isActive,
    )

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_v3_web.providers.update_provider", provider_id=provider_id),
        div_id=f"update-provider-{provider_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier un prestataire synchronisé avec le pass Culture",
        button_text="Modifier le prestataire",
    )


@providers_blueprint.route("/<int:provider_id>/update", methods=["POST"])
def update_provider(provider_id: int) -> utils.BackofficeResponse:
    provider = providers_models.Provider.query.get(provider_id)

    form = forms.EditProviderForm()
    if not form.validate():
        error_msg = utils.build_form_error_msg(form)
        flash(error_msg, "warning")
        return redirect(url_for("backoffice_v3_web.providers.get_providers"), code=303)

    provider.name = form.name.data
    provider.logoUrl = form.logo_url.data
    provider.enabledForPro = form.enabled_for_pro.data
    provider.isActive = form.is_active.data

    try:
        db.session.add(provider)
        db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce prestataire existe déjà", "warning")
    else:
        flash(f"Le prestataire {provider.name} a été modifié.", "success")

    return redirect(url_for("backoffice_v3_web.providers.get_providers"), code=303)
