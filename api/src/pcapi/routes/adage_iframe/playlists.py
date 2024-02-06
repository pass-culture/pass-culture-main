from decimal import Decimal
import logging
import random
import typing

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository
import pcapi.core.educational.api.favorites as favorites_api
import pcapi.core.offerers.api as offerers_api
from pcapi.core.offerers.repository import get_venue_by_id
from pcapi.models import Model
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serializers
from pcapi.routes.adage_iframe.serialization import playlists as playlists_serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import (
    get_redactor_information_from_adage_authentication,
)
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


def get_random_results(cls: type[Model]) -> dict[str, float]:
    offer_ids = [row[0] for row in cls.query.with_entities(cls.id)]
    offer_ids = random.choices(offer_ids, k=min(len(offer_ids), 10))
    return {str(offer_id): random.uniform(1.0, 60.0) for offer_id in offer_ids}


@blueprint.adage_iframe.route("/playlists/classroom", methods=["GET"])
@spectree_serialize(response_model=serializers.ListCollectiveOfferTemplateResponseModel, api=blueprint.api)
@adage_jwt_required
def get_classroom_playlist(
    authenticated_information: AuthenticatedInformation,
) -> serializers.ListCollectiveOfferTemplateResponseModel:
    if not authenticated_information.uai:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    institution = repository.get_educational_institution_public(institution_id=None, uai=authenticated_information.uai)
    if not institution:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    try:
        informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except educational_exceptions.MissingRequiredRedactorInformation:
        raise ApiErrors(errors={"auth": "unknown redactor"}, status_code=403)

    redactor = repository.find_redactor_by_email(informations.email)
    if not redactor:
        raise ApiErrors(errors={"auth": "unknown redactor"}, status_code=403)

    playlist_items = (
        repository.get_collective_offer_templates_for_playlist_query(
            institution_id=institution.id, playlist_type=educational_models.PlaylistType.CLASSROOM
        )
        .limit(10)
        .all()
    )
    favorite_ids = favorites_api.get_redactors_favorite_templates_subset(
        redactor, [item.collective_offer_template.id for item in playlist_items]
    )

    return serializers.ListCollectiveOfferTemplateResponseModel(
        collectiveOffers=[
            typing.cast(
                serializers.CollectiveOfferTemplateResponseModel,
                serialize_collective_offer(
                    offer=item.collective_offer_template,
                    serializer=serializers.CollectiveOfferTemplateResponseModel,
                    is_favorite=item.collective_offer_template.id in favorite_ids,
                    venue_distance=item.distanceInKm,
                ),
            )
            for item in playlist_items
        ]
    )


def format_distance(distance: float | None) -> Decimal | None:
    if not distance:
        return None
    return Decimal.from_float(distance).quantize(Decimal("1.0"))


def serialize_collective_offer(
    offer: educational_models.CollectiveOffer,
    serializer: type[serializers.CollectiveOfferResponseModel] | type[serializers.CollectiveOfferTemplateResponseModel],
    is_favorite: bool,
    venue_distance: float | None = None,
    event_distance: float | None = None,
) -> serializers.CollectiveOfferResponseModel | serializers.CollectiveOfferTemplateResponseModel:
    offer_venue_id = offer.offerVenue.get("venueId")
    if offer_venue_id:
        offer_venue = get_venue_by_id(offer_venue_id)
    else:
        offer_venue = None

    serialized_offer = serializer.build(offer=offer, offerVenue=offer_venue, is_favorite=is_favorite)

    serialized_offer.venue.distance = format_distance(venue_distance)
    serialized_offer.offerVenue.distance = format_distance(event_distance)

    return serialized_offer


@blueprint.adage_iframe.route("/playlists/new_template_offers", methods=["GET"])
@spectree_serialize(
    response_model=serializers.ListCollectiveOfferTemplateResponseModel,
    api=blueprint.api,
    on_error_statuses=[404],
)
@adage_jwt_required
def new_template_offers_playlist(
    authenticated_information: AuthenticatedInformation,
) -> serializers.ListCollectiveOfferTemplateResponseModel:
    if authenticated_information.uai is None:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    institution = repository.find_educational_institution_by_uai_code(authenticated_information.uai)
    if not institution:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    try:
        informations = get_redactor_information_from_adage_authentication(authenticated_information)
    except educational_exceptions.MissingRequiredRedactorInformation:
        raise ApiErrors(errors={"auth": "unknown redactor"}, status_code=403)

    redactor = repository.find_redactor_by_email(informations.email)
    if not redactor:
        raise ApiErrors(errors={"auth": "unknown redactor"}, status_code=403)

    playlist_items = (
        repository.get_collective_offer_templates_for_playlist_query(
            institution_id=institution.id, playlist_type=educational_models.PlaylistType.NEW_OFFER
        )
        .limit(10)
        .all()
    )
    favorite_ids = favorites_api.get_redactors_favorite_templates_subset(
        redactor, [item.collective_offer_template.id for item in playlist_items]
    )

    return serializers.ListCollectiveOfferTemplateResponseModel(
        collectiveOffers=[
            typing.cast(
                serializers.CollectiveOfferTemplateResponseModel,
                serialize_collective_offer(
                    offer=item.collective_offer_template,
                    serializer=serializers.CollectiveOfferTemplateResponseModel,
                    is_favorite=item.collective_offer_template.id in favorite_ids,
                    event_distance=(
                        item.distanceInKm
                        if item.collective_offer_template.offerVenue["addressType"]
                        == collective_offers_serialize.OfferAddressType.OFFERER_VENUE.value
                        else None
                    ),
                    venue_distance=item.distanceInKm,
                ),
            )
            for item in playlist_items
        ]
    )


@blueprint.adage_iframe.route("/playlists/local-offerers", methods=["GET"])
@spectree_serialize(response_model=playlists_serializers.LocalOfferersPlaylist, api=blueprint.api)
@adage_jwt_required
def get_local_offerers_playlist(
    authenticated_information: AuthenticatedInformation,
) -> playlists_serializers.LocalOfferersPlaylist:
    if not authenticated_information.uai:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    institution = repository.get_educational_institution_public(institution_id=None, uai=authenticated_information.uai)
    if not institution:
        raise ApiErrors({"message": "institutionId is mandatory"}, status_code=403)

    playlist_items = (
        repository.get_collective_offer_templates_for_playlist_query(
            institution_id=institution.id, playlist_type=educational_models.PlaylistType.LOCAL_OFFERER
        )
        .limit(10)
        .all()
    )

    distances = {item.venueId: item.distanceInKm for item in playlist_items}
    venues = offerers_api.get_venues_by_ids(distances.keys())

    return playlists_serializers.LocalOfferersPlaylist(
        venues=[
            playlists_serializers.LocalOfferersPlaylistOffer(
                img_url=venue.bannerUrl,
                public_name=venue.publicName,
                name=venue.name,
                distance=format_distance(distances[venue.id]),
                city=venue.city,
                id=venue.id,
            )
            for venue in venues
        ]
    )
