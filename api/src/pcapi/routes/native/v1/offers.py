from flask_login import current_user
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import BadRequest

import pcapi.core.chronicles.api as chronicles_api
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.categories import subcategories
from pcapi.core.categories.app_search_tree import NATIVE_CATEGORIES
from pcapi.core.categories.app_search_tree import SEARCH_GROUPS
from pcapi.core.categories.app_search_tree import SEARCH_NODES
from pcapi.core.categories.models import GenreType
from pcapi.core.offers import repository
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Reason
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.utils import first_or_404
from pcapi.models.utils import get_or_404
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic
from pcapi.workers import push_notification_job

from .. import blueprint
from .serialization import offers as serializers
from .serialization import subcategories_v2 as subcategories_v2_serializers


# WebApp v2 proxy expects endpoint to be at "/offer/<int:offer_id>". This path MUST NOT be changed. Its response can be changed, though.
@blueprint.native_route("/offer/<int:offer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404], deprecated=True
)
@atomic()
def get_offer(offer_id: str) -> serializers.OfferResponse:
    query = repository.get_offers_details([int(offer_id)])
    offer = first_or_404(query)

    return serializers.OfferResponse.from_orm(offer)


@blueprint.native_route("/offer/<int:offer_id>", version="v2", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferResponseV2, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_offer_v2(offer_id: int) -> serializers.OfferResponseV2:
    query = repository.get_offers_details([int(offer_id)])
    offer = first_or_404(query)

    return serializers.OfferResponseV2.from_orm(offer)


@blueprint.native_route("/offers/stocks", methods=["POST"], version="v2")
@spectree_serialize(response_model=serializers.OffersStocksResponseV2, api=blueprint.api)
def get_offers_and_stocks(body: serializers.OffersStocksRequest) -> serializers.OffersStocksResponseV2:
    offer_ids = body.offer_ids
    query = repository.get_offers_details(offer_ids)
    serialized_offers = [serializers.OfferResponseV2.from_orm(offer) for offer in query]
    offers_response = serializers.OffersStocksResponseV2(offers=serialized_offers)
    return offers_response


@blueprint.native_route("/movie/calendar", methods=["GET"])
@spectree_serialize(response_model=serializers.MovieCalendarResponse, api=blueprint.api, on_error_statuses=[400, 404])
def get_movie_screenings(query: serializers.MovieScreeningsRequest) -> serializers.MovieCalendarResponse:
    if query.allocine_id:
        product_query = db.session.query(Product).filter(Product.extraData.op("->")("allocineId") == query.allocine_id)
    elif query.visa:
        product_query = db.session.query(Product).filter(Product.extraData["visa"].astext == query.visa)
    else:
        raise BadRequest()  # shoud not happen

    product = first_or_404(product_query)

    results = repository.get_nearby_bookable_screenings_from_product(
        product,
        query.latitude,
        query.longitude,
        query.around_radius,
        query.from_datetime,
        query.to_datetime,
    )

    return serializers.MovieCalendarResponse.from_raw_screenings(
        [serializers.RawScreening(**row) for row in results], query.from_datetime, query.to_datetime
    )


@blueprint.native_route("/venue/<int:venue_id>/movie/calendar", methods=["GET"])
@spectree_serialize(response_model=serializers.VenueMovieCalendarResponse, api=blueprint.api, on_error_statuses=[400])
def get_movie_screenings_by_venue(
    venue_id: int, query: serializers.VenueMovieScreeningsRequest
) -> serializers.VenueMovieCalendarResponse:
    offers = repository.get_bookable_screenings_from_venue(
        venue_id,
        query.from_datetime,
        query.to_datetime,
    )

    return serializers.VenueMovieCalendarResponse.from_offers(offers, query.from_datetime, query.to_datetime)


@blueprint.native_route("/offer/report/reasons", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.OfferReportReasons)
@authenticated_and_active_user_required
def report_offer_reasons() -> serializers.OfferReportReasons:
    return serializers.OfferReportReasons(reasons=Reason.get_full_meta())


@blueprint.native_route("/offer/<int:offer_id>/chronicles", methods=["GET"])
@spectree_serialize(
    on_success_status=200, on_error_statuses=[404], api=blueprint.api, response_model=serializers.OfferChronicles
)
@atomic()
def offer_chronicles(offer_id: int) -> serializers.OfferChronicles:
    offer = get_or_404(Offer, offer_id)

    chronicles = chronicles_api.get_offer_published_chronicles(offer)

    return serializers.OfferChronicles(
        chronicles=[serializers.OfferChronicle.from_orm(chronicle) for chronicle in chronicles]
    )


@blueprint.native_route("/send_offer_webapp_link_by_email/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def send_offer_app_link(offer_id: int) -> None:
    """
    On iOS native app, users cannot book numeric offers with price > 0, so
    give them webapp link.
    """
    offer = first_or_404(
        db.session.query(Offer)
        .options(joinedload(Offer.venue))
        .filter(Offer.id == offer_id, Offer.validation == OfferValidationStatus.APPROVED)
    )
    transactional_mails.send_offer_link_to_ios_user_email(current_user, offer)


@blueprint.native_route("/send_offer_link_by_push/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def send_offer_link_by_push(offer_id: int) -> None:
    offer = get_or_404(Offer, offer_id)
    if offer.validation != OfferValidationStatus.APPROVED:
        raise ResourceNotFoundError()
    push_notification_job.send_offer_link_by_push_job.delay(current_user.id, offer_id)


@blueprint.native_route("/subcategories/v2", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=subcategories_v2_serializers.SubcategoriesResponseModelv2)
def get_subcategories_v2() -> subcategories_v2_serializers.SubcategoriesResponseModelv2:
    return subcategories_v2_serializers.SubcategoriesResponseModelv2(
        subcategories=[
            subcategories_v2_serializers.SubcategoryResponseModelv2.from_orm(subcategory)
            for subcategory in subcategories.ALL_SUBCATEGORIES
        ],
        searchGroups=[
            subcategories_v2_serializers.SearchGroupResponseModelv2.from_orm(search_group)
            for search_group in SEARCH_GROUPS
        ],
        homepageLabels=[
            subcategories_v2_serializers.HomepageLabelResponseModelv2.from_orm(homepage_label_name)
            for homepage_label_name in subcategories.HomepageLabels
        ],
        nativeCategories=[
            subcategories_v2_serializers.NativeCategoryResponseModelv2.from_orm(native_category)
            for native_category in NATIVE_CATEGORIES
        ],
        genreTypes=[subcategories_v2_serializers.GenreTypeModel.from_orm(genre_type) for genre_type in GenreType],
    )


@blueprint.native_route("/categories", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=subcategories_v2_serializers.CategoriesResponseModel)
def get_categories() -> subcategories_v2_serializers.CategoriesResponseModel:
    return subcategories_v2_serializers.CategoriesResponseModel(
        categories=[subcategories_v2_serializers.CategoryResponseModel.from_orm(node) for node in SEARCH_NODES]
    )
