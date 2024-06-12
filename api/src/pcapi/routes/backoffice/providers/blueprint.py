from secrets import token_urlsafe

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core.external import zendesk_sell
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.permissions import models as perm_models
from pcapi.core.providers import api as providers_api
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus

from . import forms
from .. import utils


providers_blueprint = utils.child_backoffice_blueprint(
    "providers",
    __name__,
    url_prefix="/pro/providers",
    permission=perm_models.Permissions.MANAGE_TECH_PARTNERS,
)


@providers_blueprint.route("", methods=["GET"])
def list_providers() -> utils.BackofficeResponse:
    is_active_count = (
        sa.select(sa.func.jsonb_object_agg(sa.text("status_group"), sa.text("number")))
        .select_from(
            sa.select(
                sa.case(
                    (providers_models.VenueProvider.isActive, "active"),
                    else_="inactive",
                ).label("status_group"),
                sa.func.count(providers_models.VenueProvider.id).label("number"),
            )
            .select_from(providers_models.VenueProvider)
            .correlate(providers_models.Provider)
            .filter(
                providers_models.VenueProvider.providerId == providers_models.Provider.id,
            )
            .group_by("status_group")
            .subquery()
        )
        .scalar_subquery()
    )

    rows = (
        db.session.query(providers_models.Provider, is_active_count.label("is_active_count"))
        .options(
            sa.orm.load_only(
                providers_models.Provider.id,
                providers_models.Provider.name,
                providers_models.Provider.logoUrl,
                providers_models.Provider.enabledForPro,
                providers_models.Provider.isActive,
            )
        )
        .options(
            sa.orm.joinedload(providers_models.Provider.offererProvider)
            .joinedload(offerers_models.OffererProvider.offerer)
            .load_only(offerers_models.Offerer.city, offerers_models.Offerer.postalCode, offerers_models.Offerer.siren)
        )
        .options(sa.orm.joinedload(providers_models.Provider.apiKeys).load_only(offerers_models.ApiKey.id))
        .order_by(sa.func.lower(sa.func.unaccent(providers_models.Provider.name)))
        .all()
    )

    return render_template("providers/list.html", rows=rows)


@providers_blueprint.route("/new", methods=["GET"])
def get_create_provider_form() -> utils.BackofficeResponse:
    form = forms.CreateProviderForm()

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.providers.create_provider"),
        div_id="create-provider",  # must be consistent with parameter passed to build_lazy_modal
        title="Créer un partenaire technique qui se synchronisera avec le pass Culture",
        button_text="Créer le partenaire",
    )


@providers_blueprint.route("/", methods=["POST"])
def create_provider() -> utils.BackofficeResponse:
    form = forms.CreateProviderForm()

    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.providers.list_providers"), code=303)

    def generate_hmac_key() -> str:
        return token_urlsafe(64)

    try:
        provider = providers_models.Provider(
            name=form.name.data,
            logoUrl=form.logo_url.data,
            enabledForPro=form.enabled_for_pro.data,
            isActive=form.is_active.data,
            bookingExternalUrl=form.booking_external_url.data,
            cancelExternalUrl=form.cancel_external_url.data,
            notificationExternalUrl=form.notification_external_url.data,
            hmacKey=generate_hmac_key(),
        )
        offerer, is_offerer_new = _get_or_create_offerer(form)
        offerer_provider = offerers_models.OffererProvider(offerer=offerer, provider=provider)
        api_key, clear_secret = offerers_api.generate_provider_api_key(provider)
        db.session.add_all([provider, offerer, offerer_provider, api_key])

        history_api.add_action(
            history_models.ActionType.OFFERER_NEW,
            current_user,
            offerer=offerer,
            comment="Création automatique via création de partenaire",
        )

        db.session.commit()
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce partenaire existe déjà", "warning")
    else:
        if is_offerer_new:
            zendesk_sell.create_offerer(offerer)
        flash(
            Markup(
                "Le nouveau partenaire <b>{name}</b> a été créé. "
                "La Clé API ne peut être régénérée ni ré-affichée, veillez à la sauvegarder immédiatement : <pre>{clear_secret}</pre>"
            ).format(name=provider.name, clear_secret=clear_secret),
            "success",
        )
        flash(
            Markup(
                "La clé de chiffrage des requêtes entre le partenaire et le pass Culture dans le cadre de l'API Charlie est : <pre>{key}</pre>"
            ).format(key=provider.hmacKey),
            "success",
        )

    return redirect(url_for("backoffice_web.providers.list_providers"), code=303)


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


def _render_provider_details(
    provider: providers_models.Provider, edit_form: forms.EditProviderForm | None = None
) -> str:
    if not edit_form:
        edit_form = forms.EditProviderForm(
            name=provider.name,
            logo_url=provider.logoUrl,
            enabled_for_pro=provider.enabledForPro,
            is_active=provider.isActive,
            booking_external_url=provider.bookingExternalUrl,
            cancel_external_url=provider.cancelExternalUrl,
            notification_external_url=provider.notificationExternalUrl,
            hmac_key=provider.hmacKey,
        )

    return render_template(
        "providers/get.html",
        provider=provider,
        active_tab=request.args.get("active_tab", "venues"),
        edit_form=edit_form,
    )


@providers_blueprint.route("/<int:provider_id>", methods=["GET"])
def get_provider(provider_id: int) -> utils.BackofficeResponse:
    provider = (
        providers_models.Provider.query.filter(providers_models.Provider.id == provider_id)
        .options(
            sa.orm.joinedload(providers_models.Provider.offererProvider)
            .joinedload(offerers_models.OffererProvider.offerer)
            .load_only(offerers_models.Offerer.city, offerers_models.Offerer.postalCode, offerers_models.Offerer.siren)
        )
        .options(sa.orm.joinedload(providers_models.Provider.apiKeys).load_only(offerers_models.ApiKey.id))
        .one_or_none()
    )

    if not provider:
        raise NotFound()

    return _render_provider_details(provider)


def _get_active_venue_providers_stats(provider_id: int) -> dict[str, int]:
    query = sa.select(sa.func.jsonb_object_agg(sa.text("status_group"), sa.text("number"))).select_from(
        sa.select(
            sa.case(
                (providers_models.VenueProvider.isActive, "active"),
                else_="inactive",
            ).label("status_group"),
            sa.func.count(providers_models.VenueProvider.id).label("number"),
        )
        .filter(providers_models.VenueProvider.providerId == provider_id)
        .group_by("status_group")
        .subquery()
    )
    (data,) = db.session.execute(query).one()

    return {
        "active": data.get("active", 0) if data else 0,
        "inactive": data.get("inactive", 0) if data else 0,
    }


@providers_blueprint.route("/<int:provider_id>/stats", methods=["GET"])
def get_stats(provider_id: int) -> utils.BackofficeResponse:
    stats = _get_active_venue_providers_stats(provider_id)
    return render_template(
        "providers/get/stats.html",
        stats=stats,
        provider_id=provider_id,
    )


@providers_blueprint.route("/<int:provider_id>/venues", methods=["GET"])
def get_venues(provider_id: int) -> utils.BackofficeResponse:
    venues = (
        offerers_models.Venue.query.join(
            providers_models.VenueProvider,
            sa.and_(
                providers_models.VenueProvider.venueId == offerers_models.Venue.id,
                providers_models.VenueProvider.providerId == provider_id,
            ),
        )
        .options(
            sa.orm.load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.siret,
            ),
            sa.orm.contains_eager(offerers_models.Venue.venueProviders).load_only(
                providers_models.VenueProvider.isActive, providers_models.VenueProvider.lastSyncDate
            ),
        )
        .order_by(sa.func.lower(sa.func.unaccent(offerers_models.Venue.common_name)), offerers_models.Venue.id)
        .all()
    )

    return render_template("providers/get/venues.html", venues=venues, provider_id=provider_id)


@providers_blueprint.route("/<int:provider_id>/update", methods=["GET"])
def get_update_provider_form(provider_id: int) -> utils.BackofficeResponse:
    provider = providers_models.Provider.query.filter_by(id=provider_id).one_or_none()
    if not provider:
        raise NotFound()

    form = forms.EditProviderForm(
        name=provider.name,
        logo_url=provider.logoUrl,
        enabled_for_pro=provider.enabledForPro,
        is_active=provider.isActive,
        booking_external_url=provider.bookingExternalUrl,
        cancel_external_url=provider.cancelExternalUrl,
        notification_external_url=provider.notificationExternalUrl,
        provider_hmac_key=provider.hmacKey,
    )

    form.provider_hmac_key.flags.copy_button = provider.hmacKey is not None

    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for("backoffice_web.providers.update_provider", provider_id=provider_id),
        div_id=f"update-provider-{provider_id}",  # must be consistent with parameter passed to build_lazy_modal
        title="Modifier un partenaire technique synchronisé avec le pass Culture",
        button_text="Modifier le partenaire",
    )


@providers_blueprint.route("/<int:provider_id>/update", methods=["POST"])
def update_provider(provider_id: int) -> utils.BackofficeResponse:
    provider = providers_models.Provider.query.filter_by(id=provider_id).one_or_none()
    if not provider:
        raise NotFound()

    form = forms.EditProviderForm()
    if not form.validate():
        msg = Markup(
            """
            <button type="button"
                    class="btn"
                    data-bs-toggle="modal"
                    data-bs-target="#edit-provider-modal">
                Les données envoyées comportent des erreurs. Afficher
            </button>
            """
        ).format()
        flash(msg, "warning")
        return _render_provider_details(provider, edit_form=form), 400

    provider.name = form.name.data
    provider.logoUrl = form.logo_url.data
    provider.enabledForPro = form.enabled_for_pro.data
    provider.isActive = form.is_active.data
    provider.bookingExternalUrl = form.booking_external_url.data
    provider.cancelExternalUrl = form.cancel_external_url.data
    provider.notificationExternalUrl = form.notification_external_url.data

    try:
        db.session.add(provider)
        db.session.commit()
        if not form.is_active.data:
            providers_api.disable_offers_linked_to_provider(provider_id, current_user)
    except sa.exc.IntegrityError:
        db.session.rollback()
        flash("Ce partenaire existe déjà", "warning")
    else:
        flash("Les informations ont été mises à jour", "success")

    return redirect(url_for("backoffice_web.providers.get_provider", provider_id=provider_id), code=303)
