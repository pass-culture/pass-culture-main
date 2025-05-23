import sqlalchemy.orm as sa_orm
from flask import flash
from flask import url_for
from markupsafe import Markup
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect

from pcapi import settings
from pcapi.core.external import zendesk_sell
from pcapi.core.external.zendesk_sell_backends import BaseBackend
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.utils import requests
from pcapi.utils.module_loading import import_string


zendesk_sell_blueprint = utils.child_backoffice_blueprint(
    "zendesk_sell",
    __name__,
    url_prefix="/zendesk-sell",
    permission=perm_models.Permissions.MANAGE_PRO_ENTITY,
)
zendesk_sell_backend: BaseBackend = import_string(settings.ZENDESK_SELL_BACKEND)()


def _get_parent_organization_id(venue: offerers_models.Venue) -> int | None:
    offerer = venue.managingOfferer
    try:
        zendesk_offerer_data = zendesk_sell_backend.get_offerer_by_id(offerer)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        message = Markup(
            "Attention : Plusieurs entités juridiques parentes possibles ont été trouvées pour ce partenaire culturel dans Zendesk Sell. <br/> <ul>"
        )
        for item in e.items:
            message += Markup(
                "<li>Identifiant Zendesk Sell : <b>{item_id}</b>, "
                "Produit Offerer ID : <b>{product_offerer_id}</b>, "
                "SIREN : <b>{siren}</b> </li>"
            ).format(
                item_id=item["id"],
                product_offerer_id=item["custom_fields"][
                    zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value
                ],
                siren=item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIREN.value],
            )
        message += Markup("</ul>")
        flash(message, "info")
        return None
    except zendesk_sell.ContactNotFoundError:
        # no parent: ignore, nothing to update
        return None
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup(
                "Une erreur {status_code} s'est produite lors de la recherche de l'entité juridique parente : {error}"
            ).format(status_code=str(http_error.response.status_code), error=str(http_error)),
            "warning",
        )
        return None

    return zendesk_offerer_data["id"]


@zendesk_sell_blueprint.route("/offerer/<int:offerer_id>/update", methods=["POST"])
def update_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        db.session.query(offerers_models.Offerer)
        .filter_by(id=offerer_id)
        .options(sa_orm.joinedload(offerers_models.Offerer.managedVenues))
        .one()
    )
    url = url_for("backoffice_web.offerer.get", offerer_id=offerer_id)

    if zendesk_sell.is_offerer_only_virtual(offerer):
        flash("Cette entité juridique ne gère que des partenaires culturels virtuels", "warning")
        return redirect(url, code=303)

    try:
        zendesk_offerer_data = zendesk_sell_backend.get_offerer_by_id(offerer)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        message = Markup(
            "Plusieurs entités juridiques ont été trouvées dans Zendesk Sell, aucune ne peut donc être mise à jour : <br/> <ul>"
        )
        for item in e.items:
            message += Markup(
                "<li>Identifiant Zendesk Sell : <b>{item_id}</b>, "
                "Produit Offerer ID : <b>{product_offerer_id}</b>, "
                "SIREN : <b>{siren}</b> </li>"
            ).format(
                item_id=item["id"],
                product_offerer_id=item["custom_fields"][
                    zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value
                ],
                siren=item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIREN.value],
            )
        message += Markup("</ul>")
        flash(Markup(message), "warning")  # noqa: S704
        return redirect(url, code=303)
    except zendesk_sell.ContactNotFoundError:
        flash("L'entité juridique n'a pas été trouvée dans Zendesk Sell", "warning")
        return redirect(url, code=303)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {status_code} s'est produite : {error}").format(
                status_code=str(http_error.response.status_code), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    try:
        offerer_zendesk_id = zendesk_offerer_data["id"]
        zendesk_sell_backend.update_offerer(offerer_zendesk_id, offerer)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {status_code} s'est produite : {error}").format(
                status_code=str(http_error.response.status_code), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    flash("L'entité juridique a été mise à jour sur Zendesk Sell", "success")
    return redirect(url, code=303)


@zendesk_sell_blueprint.route("/venue/<int:venue_id>/update", methods=["POST"])
def update_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
    if not venue:
        raise NotFound()

    url = url_for("backoffice_web.venue.get", venue_id=venue_id)

    if venue.isVirtual or not venue.isOpenToPublic:
        flash("Ce partenaire culturel est virtuel ou n'est pas ouvert au public", "warning")
        return redirect(url, code=303)

    try:
        zendesk_venue_data = zendesk_sell_backend.get_venue_by_id(venue)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        message = Markup(
            "Plusieurs partenaires culturels ont été trouvés dans Zendesk Sell, aucun ne peut donc être mis à jour : <br/> <ul>"
        )
        for item in e.items:
            message += Markup(
                "<li>Identifiant Zendesk Sell : <b>{item_id}</b>, "
                "Produit Venue ID : <b>{product_venue_id}</b>, "
                "SIRET : <b>{siret}</b> </li>"
            ).format(
                item_id=item["id"],
                product_venue_id=item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value],
                siret=item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIRET.value],
            )
        message += Markup("</ul>")
        flash(message, "warning")
        return redirect(url, code=303)
    except zendesk_sell.ContactNotFoundError:
        flash("Le partenaire culturel n'a pas été trouvé dans Zendesk Sell", "warning")
        return redirect(url, code=303)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {status_code} s'est produite : {error}").format(
                status_code=str(http_error.response.status_code), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    try:
        zendesk_venue_id = zendesk_venue_data["id"]
        parent_organization_id = _get_parent_organization_id(venue)
        zendesk_sell_backend.update_venue(zendesk_venue_id, venue, parent_organization_id)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {status_code} s'est produite : {error}").format(
                status_code=str(http_error.response.status_code), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    flash("Le partenaire culturel a été mis à jour sur Zendesk Sell", "success")
    return redirect(url, code=303)
