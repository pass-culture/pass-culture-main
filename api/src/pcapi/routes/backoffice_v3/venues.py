from datetime import datetime

from flask import render_template
import gql.transport.exceptions as gql_exceptions
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.connectors.dms.api import DMSGraphQLClient
from pcapi.core.offerers import api as offerers_api
import pcapi.core.offerers.models as offerers_models
import pcapi.core.permissions.models as perm_models
import pcapi.utils.regions as regions_utils

from . import utils
from .serialization import offerers as offerers_serialization
from .serialization import venues as serialization


venue_blueprint = utils.child_backoffice_blueprint(
    "venue",
    __name__,
    url_prefix="/pro/venue/<int:venue_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


def get_venue(venue_id: int) -> offerers_models.Venue:
    venue = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id)
        .options(
            sa.orm.joinedload(offerers_models.Venue.managingOfferer),
            sa.orm.joinedload(offerers_models.Venue.contact),
            sa.orm.joinedload(offerers_models.Venue.bankInformation),
            sa.orm.joinedload(offerers_models.Venue.reimbursement_point_links),
        )
        .one_or_none()
    )

    if not venue:
        raise NotFound()

    return venue


def get_dms_stats(dms_application_id: int | None) -> serialization.VenueDmsStats | None:
    if not dms_application_id:
        return None

    try:
        dms_stats = DMSGraphQLClient().get_bank_info_status(dms_application_id)
    except (gql_exceptions.TransportError, gql_exceptions.TransportQueryError):
        return None

    return serialization.VenueDmsStats(
        status=dms_stats["dossier"]["state"],  # pylint: disable=unsubscriptable-object
        subscriptionDate=datetime.fromisoformat(
            dms_stats["dossier"]["dateDepot"]  # pylint: disable=unsubscriptable-object
        ),
        url=f"https://www.demarches-simplifiees.fr/dossiers/{dms_application_id}",
    )


def has_reimbursement_point(
    venue: offerers_models.Venue,
) -> bool:
    now = datetime.utcnow()

    for link in venue.reimbursement_point_links:
        lower = link.timespan.lower
        upper = link.timespan.upper

        if lower <= now and (not upper or now <= upper):
            return True

    return False


@venue_blueprint.route("", methods=["GET"])
def get(venue_id: int) -> utils.BackofficeResponse:
    venue = get_venue(venue_id)

    dms_application_id = venue.bankInformation.applicationId if venue.bankInformation else None
    dms_stats = get_dms_stats(dms_application_id)
    region = regions_utils.get_region_name_from_postal_code(venue.postalCode) if venue.postalCode else ""

    return render_template(
        "venue/get.html",
        venue=venue,
        region=region,
        has_reimbursement_point=has_reimbursement_point(venue),
        dms_stats=dms_stats,
    )


def get_stats_data(venue_id: int) -> serialization.VenueStats:
    offers_stats = offerers_api.get_venue_offers_stats(venue_id)

    if not offers_stats:
        raise NotFound()

    stats = serialization.VenueOffersStats(
        active=offerers_serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("active", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("active", 0) if offers_stats.collective_offers else 0,
        ),
        inactive=offerers_serialization.BaseOffersStats(
            individual=offers_stats.individual_offers.get("inactive", 0) if offers_stats.individual_offers else 0,
            collective=offers_stats.collective_offers.get("inactive", 0) if offers_stats.collective_offers else 0,
        ),
        lastSync=serialization.LastOfferSyncStats(
            date=offers_stats.lastSyncDate,
            provider=offers_stats.name,
        ),
    )

    total_revenue = offerers_api.get_venue_total_revenue(venue_id)

    return serialization.VenueStats(stats=stats, total_revenue=total_revenue)


@venue_blueprint.route("/stats", methods=["GET"])
def get_stats(venue_id: int) -> utils.BackofficeResponse:
    venue = offerers_models.Venue.query.get_or_404(venue_id)
    data = get_stats_data(venue.id)

    return render_template(
        "venue/get/stats.html",
        venue=venue,
        stats=data.stats,
        total_revenue=data.total_revenue,
    )
