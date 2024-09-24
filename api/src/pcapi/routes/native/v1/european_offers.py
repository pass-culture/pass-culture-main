from pcapi.core.european_offers.models import EuropeanOffer
from pcapi.repository import atomic
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import european_offers as serializers


@blueprint.native_route("/european_offer/<int:offer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.EuropeanOfferResponse, api=blueprint.api, on_error_statuses=[404], deprecated=True
)
@atomic()
def get_european_offer(offer_id: str) -> serializers.EuropeanOfferResponse:
    offer = EuropeanOffer.query.filter(EuropeanOffer.id == offer_id).first_or_404()

    return serializers.EuropeanOfferResponse.from_orm(offer)
