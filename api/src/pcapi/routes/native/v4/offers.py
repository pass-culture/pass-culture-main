from pcapi.core.offers import repository
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.utils import first_or_404
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint
from .serialization import offers as serializers


@blueprint.native_route("/offer/<int:offer_id>", version="v4", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer(offer_id: int) -> serializers.OfferResponse:
    query = repository.get_offer_main_data(offer_id)
    offer = first_or_404(query)
    return serializers.OfferResponse.build(offer)


@blueprint.native_route("/offer/<int:offer_id>/header", version="v4", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferHeaderResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_header(offer_id: int) -> serializers.OfferHeaderResponse:
    query = repository.get_offer_header(offer_id)
    offer = first_or_404(query)
    return serializers.OfferHeaderResponse.build(offer)


@blueprint.native_route("/offer/<int:offer_id>/offerer", version="v4", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferOffererResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_offerer(offer_id: int) -> serializers.OfferOffererResponse:
    query = repository.get_offer_offerer(offer_id)
    offer = first_or_404(query)
    return serializers.OfferOffererResponse.build(offer)


@blueprint.native_route("/offer/<int:offer_id>/chronicles", version="v4", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferChroniclesResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_chronicles(offer_id: int, query: serializers.OfferChroniclesQuery) -> serializers.OfferChroniclesResponse:
    result = repository.get_offer_chronicles_data(offer_id, page=query.page, limit=query.limit)
    if result is None:
        raise ResourceNotFoundError()
    chronicles, total = result
    return serializers.OfferChroniclesResponse.build(chronicles, total)


@blueprint.native_route("/offer/<int:offer_id>/stocks", version="v4", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferStocksResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_stocks(offer_id: int, query: serializers.OfferStocksQuery) -> serializers.OfferStocksResponse:
    result = repository.get_offer_stocks_data(offer_id, page=query.page, limit=query.limit)
    if result is None:
        raise ResourceNotFoundError()
    stocks, total = result
    return serializers.OfferStocksResponse(
        stocks=[serializers.v3_serializers.OfferStockResponse.build(stock) for stock in stocks],
        stocks_count=total,
    )


@blueprint.native_route("/offer/<int:offer_id>/pro_advices", version="v4", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferProAdvicesResponse, api=blueprint.api, on_error_statuses=[404])
def get_offer_pro_advices(
    offer_id: int, query: serializers.OfferProAdvicesQuery
) -> serializers.OfferProAdvicesResponse:
    result = repository.get_offer_pro_advices_data(
        offer_id=offer_id,
        latitude=query.latitude,
        longitude=query.longitude,
        page=query.page,
        limit=query.limit,
    )
    if result is None:
        raise ResourceNotFoundError()
    pro_advices, total = result
    return serializers.OfferProAdvicesResponse(
        pro_advices=[
            serializers.OfferProAdviceResponse.build(pro_advice, distance, query.max_content_length)
            for pro_advice, distance in pro_advices
        ],
        pro_advices_count=total,
    )
