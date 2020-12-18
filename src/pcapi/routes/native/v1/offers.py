from pcapi.core.offers.models import Offer
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import offers as serializers


@blueprint.native_v1.route("/offer/<int:offer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404]
)  # type: ignore
def get_offer(offer_id: str) -> serializers.OfferResponse:
    offer = Offer.query.filter_by(id=offer_id).first_or_404()

    return serializers.OfferResponse.from_orm(offer)
