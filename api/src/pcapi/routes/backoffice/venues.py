import datetime

import gql.transport.exceptions

from pcapi.connectors.dms.api import DMSGraphQLClient
from pcapi.core.offerers import api as offerers_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.permissions import utils as perm_utils
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize
import pcapi.utils.regions

from . import blueprint
from . import serialization


@blueprint.backoffice_blueprint.route("venues/<int:venue_id>", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_venue_basic_info(venue_id: int) -> serialization.Response:

    venue_basic_info = offerers_api.get_venue_basic_info(venue_id)

    if not venue_basic_info:
        raise ApiErrors(errors={"offerer_id": "Le lieu n'existe pas"}, status_code=404)

    serialized_dms_stats = None
    if venue_basic_info.dms_application_id:
        try:
            dms_stats = DMSGraphQLClient().get_bank_info_status(venue_basic_info.dms_application_id)
        except (gql.transport.exceptions.TransportError, gql.transport.exceptions.TransportQueryError):
            pass
        else:
            serialized_dms_stats = serialization.VenueDmsStats(
                status=dms_stats["dossier"]["state"],  # pylint: disable=unsubscriptable-object
                subscriptionDate=datetime.datetime.fromisoformat(
                    dms_stats["dossier"]["dateDepot"]  # pylint: disable=unsubscriptable-object
                ),
                url=f"www.demarches-simplifiees.fr/dossiers/{venue_basic_info.dms_application_id}",
            )

    return serialization.Response(
        data=serialization.VenueBasicInfo(
            id=venue_basic_info.id,
            name=venue_basic_info.publicName or venue_basic_info.name,
            siret=venue_basic_info.siret,
            email=venue_basic_info.email,
            phoneNumber=venue_basic_info.phone_number,
            region=pcapi.utils.regions.get_region_name_from_postal_code(venue_basic_info.postalCode),
            hasBankInformation=bool(venue_basic_info.has_bank_informations),
            isCollectiveEligible=venue_basic_info.venueEducationalStatusId is not None,
            dms=serialized_dms_stats,
        ),
    )


@blueprint.backoffice_blueprint.route("venues/<int:venue_id>/total_revenue", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_venue_total_revenue(venue_id: int) -> serialization.Response:
    total_revenue = offerers_api.get_venue_total_revenue(venue_id)

    return serialization.Response(data=total_revenue)


@blueprint.backoffice_blueprint.route("venues/<int:venue_id>/offers_stats", methods=["GET"])
@spectree_serialize(
    response_model=serialization.Response,
    on_success_status=200,
    api=blueprint.api,
)
@perm_utils.permission_required(perm_models.Permissions.READ_PRO_ENTITY)
def get_venue_offers_stats(venue_id: int) -> serialization.Response:
    # TODO: réduire de le timeout de requête SQL pour ce endpoint
    #  (peu d'intérêt pour des gro lieux pour qui le requête va prendre
    #  de toute façon trop de temps, alors autant ne pas bourriner la DB pour rien)
    offers_stats = offerers_api.get_venue_offers_stats(venue_id)

    if not offers_stats:
        raise ApiErrors(errors={"offerer_id": "Le lieu n'existe pas"}, status_code=404)

    return serialization.Response(
        data=serialization.VenueOffersStats(
            active=serialization.BaseOffersStats(
                individual=offers_stats.individual_offers["active"] if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers["active"] if offers_stats.collective_offers else 0,
            ),
            inactive=serialization.BaseOffersStats(
                individual=offers_stats.individual_offers["inactive"] if offers_stats.individual_offers else 0,
                collective=offers_stats.collective_offers["inactive"] if offers_stats.collective_offers else 0,
            ),
            lastSync=serialization.LastOfferSyncStats(
                date=offers_stats.lastSyncDate,
                provider=offers_stats.name,
            ),
        )
    )
