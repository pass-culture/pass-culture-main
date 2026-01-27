from pcapi.core.offers import repository
from pcapi.models.utils import first_or_404
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import offers as serializers


@blueprint.native_route("/offer/<int:offer_id>", version="v3", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_v3(offer_id: int) -> serializers.OfferResponse:
    query = repository.get_offers_details([int(offer_id)])
    offer = first_or_404(query)

    return serializers.OfferResponse.build(offer)
