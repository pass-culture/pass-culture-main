from pcapi.core.offers import metrics
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
    metrics.offer_requests_counter.labels(api_version="v3", endpoint="get_offer_v3").inc()
    try:
        query = repository.get_offers_details([int(offer_id)])
        offer = first_or_404(query)
        serialized_offer = serializers.OfferResponse.build(offer)
    except Exception as exp:
        metrics.offer_requests_error_counter.labels(
            api_version="v3", endpoint="get_offer_v3", error_type=type(exp).__name__
        ).inc()
        raise
    return serialized_offer


@blueprint.native_route("/offers/stocks", version="v3", methods=["POST"])
@spectree_serialize(response_model=serializers.OffersStocksResponse, api=blueprint.api)
def get_offers_and_stocks(body: serializers.OffersStocksRequest) -> serializers.OffersStocksResponse:
    metrics.offer_requests_counter.labels(api_version="v3", endpoint="get_offers_and_stocks").inc(len(body.offer_ids))

    try:
        offers_response = serializers.OffersStocksResponse.build(repository.get_offers_details(body.offer_ids).all())
    except Exception as exp:
        metrics.offer_requests_error_counter.labels(
            api_version="v3", endpoint="get_offers_and_stocks", error_type=type(exp).__name__
        ).inc(len(body.offer_ids))
        raise
    return offers_response
