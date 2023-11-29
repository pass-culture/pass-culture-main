from flask import Markup
from flask import flash
from flask import url_for
import requests
import sqlalchemy as sa
from werkzeug.utils import redirect

from pcapi import settings
from pcapi.core.external import zendesk_sell
from pcapi.core.external.zendesk_sell_backends import BaseBackend
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.routes.backoffice import utils
from pcapi.utils.module_loading import import_string


zendesk_sell_blueprint = utils.child_backoffice_blueprint(
    "zendesk_sell",
    __name__,
    url_prefix="/zendesk-sell",
    permission=perm_models.Permissions.MANAGE_PRO_ENTITY,
)
zendesk_sell_backend: BaseBackend = import_string(settings.ZENDESK_SELL_BACKEND)()


def _get_parent_organization_id(venue: offerers_models.Venue) -> int:
    offerer = venue.managingOfferer
    try:
        zendesk_offerer_data = zendesk_sell_backend.get_offerer_by_id(offerer)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        message = "Il y a plusieurs structures trouvées avec cette structure parente. <br/> <ul>"
        for item in e.items:
            message += f"""<li>Identifiant Zendesk Sell : {item["id"]}, <br/>
                    PRODUCT_OFFERER_ID: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value]}, <br/>
                       SIREN: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIREN.value]}</li>"""
        message += "</ul>"
        flash(Markup(message), "warning")  # pylint: disable=markupsafe-uncontrolled-string
        return zendesk_sell.SEARCH_PARENT
    except zendesk_sell.ContactNotFoundError:
        flash("La structure parente n'a pas été trouvée dans Zendesk Sell", "warning")
        return zendesk_sell.SEARCH_PARENT
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {response} s'est produite : {error}").format(
                response=str(http_error.response), error=str(http_error)
            ),
            "warning",
        )
        return zendesk_sell.SEARCH_PARENT

    return zendesk_offerer_data["id"]


@zendesk_sell_blueprint.route("/offerer/<int:offerer_id>/update", methods=["POST"])
def update_offerer(offerer_id: int) -> utils.BackofficeResponse:
    offerer = (
        offerers_models.Offerer.query.filter_by(id=offerer_id)
        .options(sa.orm.joinedload(offerers_models.Offerer.managedVenues))
        .one()
    )
    url = url_for("backoffice_web.offerer.get", offerer_id=offerer_id)

    if zendesk_sell.is_offerer_only_virtual(offerer):
        return redirect(url, code=303)

    try:
        zendesk_offerer_data = zendesk_sell_backend.get_offerer_by_id(offerer)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        message = "Il y a plusieurs structures trouvées avec cette structure parente. <br/> <ul>"
        for item in e.items:
            message += f"""<li>Identifiant Zendesk Sell : {item["id"]}, <br/>
            PRODUCT_OFFERER_ID: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value]}, <br/>
               SIREN: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIREN.value]}</li>"""
        message += "</ul>"
        flash(Markup(message), "warning")  # pylint: disable=markupsafe-uncontrolled-string
        return redirect(url, code=303)
    except zendesk_sell.ContactNotFoundError:
        flash("La structure n'a pas été trouvée dans Zendesk Sell", "warning")
        return redirect(url, code=303)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {response} s'est produite : {error}").format(
                response=str(http_error.response), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    try:
        offerer_zendesk_id = zendesk_offerer_data["id"]
        zendesk_sell_backend.update_offerer(offerer_zendesk_id, offerer)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {response} s'est produite : {error}").format(
                response=str(http_error.response), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    flash("La mise a jour a été effectuée avec succès", "success")
    return redirect(url, code=303)


@zendesk_sell_blueprint.route("/venue/<int:venue_id>/update", methods=["POST"])
def update_venue(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)
    url = url_for("backoffice_web.venue.get", venue_id=venue_id)

    if venue.isVirtual or not venue.isPermanent:
        flash("Ce lieu est virtuel ou non permanent", "warning")
        return redirect(url, code=303)

    try:
        zendesk_venue_data = zendesk_sell_backend.get_venue_by_id(venue)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        message = "Il y a plusieurs lieux trouvées avec cette structure parente. <br/> <ul>"

        for item in e.items:
            message += f"""<li>Identifiant Zendesk Sell : {item["id"]}, <br/>
                    PRODUCT_VENUE_ID: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value]}, <br/>
                       SIRET: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIRET.value]}</li>"""

        message += "</ul>"

        flash(Markup(message), "warning")  # pylint: disable=markupsafe-uncontrolled-string
        return redirect(url, code=303)
    except zendesk_sell.ContactNotFoundError:
        flash("Le lieu n'a pas été trouvé dans Zendesk Sell", "warning")
        return redirect(url, code=303)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {response} s'est produite : {error}").format(
                response=str(http_error.response), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    try:
        zendesk_venue_id = zendesk_venue_data["id"]
        parent_organization_id = _get_parent_organization_id(venue)
        if parent_organization_id == zendesk_sell.SEARCH_PARENT:
            raise zendesk_sell.ContactNotFoundError
        zendesk_sell_backend.update_venue(zendesk_venue_id, venue, parent_organization_id)
    except zendesk_sell.ContactNotFoundError:
        flash("La structure parente n'a pas été trouvée dans Zendesk Sell", "warning")
        return redirect(url, code=303)
    except requests.exceptions.HTTPError as http_error:
        flash(
            Markup("Une erreur {response} s'est produite : {error}").format(
                response=str(http_error.response), error=str(http_error)
            ),
            "warning",
        )
        return redirect(url, code=303)

    flash("La mise a jour a été effectuée avec succès", "success")
    return redirect(url, code=303)
