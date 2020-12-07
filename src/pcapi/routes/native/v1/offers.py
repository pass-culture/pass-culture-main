from pcapi.core.offers.models import Offer
from pcapi.models.api_errors import ApiErrors
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import offers as serializers


@blueprint.native_v1.route("/offer/<offer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.GetOfferResponse, api=blueprint.api, on_error_statuses=[404]
)  # type: ignore
def get_offer(offer_id: str) -> serializers.GetOfferResponse:
    offer = Offer.query.get(offer_id)

    if not offer:
        raise ApiErrors({"offre": ["L'offre cherchée est introuvable"]}, status_code=404)

    return serializers.GetOfferResponse.from_orm(offer)
