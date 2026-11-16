import typing

from pcapi.core.offers import repository
from pcapi.models.feature import FeatureToggle
from pcapi.models.utils import first_or_404
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import native_cache
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import offers as serializers


@blueprint.native_route("/offer/<int:offer_id>", version="v3", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_v3(offer_id: int) -> serializers.OfferResponse:
    # Check the configuration first: reading feature flags costs a SQL query on every request
    if not native_cache.is_enabled() or not FeatureToggle.ENABLE_NATIVE_CACHE_GET_OFFER_V3.is_active():
        return _build_offer_response(offer_id)

    key = native_cache.build_key("get_offer_v3", "v3", serializers.OfferResponse, offer_id)
    body = native_cache.get_or_compute(
        "get_offer_v3",
        key,
        lambda: _build_offer_response(offer_id).json(exclude_none=False, by_alias=True),
    )
    # Hit and miss serve the same JSON: the decorator serializes it through `.json()` like a response model
    return typing.cast(serializers.OfferResponse, native_cache.CachedJsonBody(body))


def _build_offer_response(offer_id: int) -> serializers.OfferResponse:
    query = repository.get_offers_details([int(offer_id)])
    offer = first_or_404(query)

    return serializers.OfferResponse.build(offer)


@blueprint.native_route("/offers/stocks", version="v3", methods=["POST"])
@spectree_serialize(response_model=serializers.OffersStocksResponse, api=blueprint.api)
def get_offers_and_stocks(body: serializers.OffersStocksRequest) -> serializers.OffersStocksResponse:
    return serializers.OffersStocksResponse.build(repository.get_offers_details(body.offer_ids).all())
