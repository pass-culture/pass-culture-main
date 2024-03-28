from flask import abort

from pcapi.core.offerers.models import Venue
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import offerers as serializers


# It will break the WebApp v2 proxy in case of endpoint modification. Read https://github.com/pass-culture/pass-culture-app-native/pull/2808/files#r844891000
@blueprint.native_route("/venue/<int:venue_id>", methods=["GET"])
@spectree_serialize(response_model=serializers.VenueResponse, api=blueprint.api, on_error_statuses=[404])
def get_venue(venue_id: int) -> serializers.VenueResponse:
    venue = Venue.query.get_or_404(venue_id)
    if not venue.isPermanent:
        abort(404)

    return serializers.VenueResponse(
        id=venue.id,
        name=venue.name,
        latitude=venue.latitude,
        longitude=venue.longitude,
        city=venue.city,
        publicName=venue.publicName,
        isVirtual=venue.isVirtual,
        isPermanent=venue.isPermanent,
        withdrawalDetails=venue.withdrawalDetails,
        address=venue.address,
        postalCode=venue.postalCode,
        venueTypeCode=venue.venueTypeCode.name,
        description=venue.description,
        contact=venue.contact,
        accessibility={  # type: ignore [arg-type]
            "audioDisability": venue.audioDisabilityCompliant,
            "mentalDisability": venue.mentalDisabilityCompliant,
            "motorDisability": venue.motorDisabilityCompliant,
            "visualDisability": venue.visualDisabilityCompliant,
        },
        bannerUrl=venue.bannerUrl,
        bannerMeta=venue.bannerMeta,
        openingHours=venue.opening_days,
    )
