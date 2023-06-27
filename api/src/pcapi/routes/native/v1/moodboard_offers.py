from pcapi.core.offers.models import Offer
from . import blueprint
from pcapi.serialization.decorator import spectree_serialize
from .serialization import moodboard_offers as serializers


@blueprint.native_v1.route("/moodboard_offers", methods=["POST"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.MoodboardOffersResponse)
def get_moodboard_offers(body: serializers.MoodboardOffersRequest) -> serializers.MoodboardOffersResponse:
    offers = Offer.query.limit(5).all()
    return serializers.MoodboardOffersResponse(offers=offers)
