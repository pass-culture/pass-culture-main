import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from pcapi.core.categories import subcategories_v2
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api
from pcapi.core.offers import repository
from pcapi.core.offers.exceptions import OfferReportError
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Reason
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import Provider
import pcapi.core.providers.repository as providers_repository
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.workers import push_notification_job

from .. import blueprint
from .serialization import offers as serializers
from .serialization import subcategories_v2 as subcategories_v2_serializers


# WebApp v2 proxy expects endpoint to be at "/offer/<int:offer_id>". This path MUST NOT be changed. Its reponse can be changed, though.
@blueprint.native_route("/offer/<int:offer_id>", methods=["GET"])
@blueprint.api.validate(deprecated=True)
@spectree_serialize(response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404])
def get_offer(offer_id: str) -> serializers.OfferResponse:
    offer: Offer = (
        Offer.query.options(
            joinedload(Offer.stocks).joinedload(Stock.priceCategory).joinedload(PriceCategory.priceCategoryLabel)
        )
        .options(
            joinedload(Offer.venue)
            .joinedload(Venue.managingOfferer)
            .load_only(Offerer.name, Offerer.validationStatus, Offerer.isActive)
        )
        .options(joinedload(Offer.venue).joinedload(Venue.googlePlacesInfo))
        .options(joinedload(Offer.mediations))
        .options(
            joinedload(Offer.product)
            .load_only(Product.id, Product.last_30_days_booking, Product.thumbCount)
            .joinedload(Product.productMediations)
        )
        .outerjoin(Offer.lastProvider)
        .options(sa.orm.contains_eager(Offer.lastProvider).load_only(Provider.localClass))
        .filter(Offer.id == offer_id, Offer.validation == OfferValidationStatus.APPROVED)
        .first_or_404()
    )

    if offer.isActive and providers_repository.is_cinema_external_ticket_applicable(offer):
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

    return serializers.OfferResponse.from_orm(offer)


@blueprint.native_route("/offer/<int:offer_id>", version="v2", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferResponseV2, api=blueprint.api, on_error_statuses=[404])
def get_offer_v2(offer_id: int) -> serializers.OfferResponseV2:
    query = repository.get_offers_details([int(offer_id)])
    offer = query.first_or_404()

    if offer.isActive and providers_repository.is_cinema_external_ticket_applicable(offer):
        api.update_stock_quantity_to_match_cinema_venue_provider_remaining_places(offer)

    return serializers.OfferResponseV2.from_orm(offer)


@blueprint.native_route("/offers/stocks", methods=["POST"])
@spectree_serialize(deprecated=True, response_model=serializers.OffersStocksResponse, api=blueprint.api)
def get_offers_showtimes(body: serializers.OffersStocksRequest) -> serializers.OffersStocksResponse:
    offer_ids = body.offer_ids
    offers = (
        Offer.query.filter(Offer.id.in_(offer_ids))
        .options(joinedload(Offer.stocks).joinedload(Stock.priceCategory).joinedload(PriceCategory.priceCategoryLabel))
        .options(joinedload(Offer.mediations))
        .options(joinedload(Offer.venue).joinedload(Venue.managingOfferer))
        .all()
    )
    serialized_offers = [serializers.OfferPreviewResponse.from_orm(offer) for offer in offers]
    offers_response = serializers.OffersStocksResponse(offers=serialized_offers)
    return offers_response


@blueprint.native_route("/offers/stocks", methods=["POST"], version="v2")
@spectree_serialize(response_model=serializers.OffersStocksResponseV2, api=blueprint.api)
def get_offers_and_stocks(body: serializers.OffersStocksRequest) -> serializers.OffersStocksResponseV2:
    offer_ids = body.offer_ids
    query = repository.get_offers_details(offer_ids)
    serialized_offers = [serializers.OfferResponseV2.from_orm(offer) for offer in query]
    offers_response = serializers.OffersStocksResponseV2(offers=serialized_offers)
    return offers_response


@blueprint.native_route("/offer/<int:offer_id>/report", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def report_offer(user: User, offer_id: int, body: serializers.OfferReportRequest) -> None:
    offer = Offer.query.get_or_404(offer_id)
    # filter in the query above would cause one more db query reported by assert_num_queries
    if offer.validation != OfferValidationStatus.APPROVED:
        raise ResourceNotFoundError()

    try:
        api.report_offer(user, offer, body.reason, body.custom_reason)
    except OfferReportError as error:
        raise ApiErrors({"code": error.code}, status_code=400)


@blueprint.native_route("/offer/report/reasons", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.OfferReportReasons)
@authenticated_and_active_user_required
def report_offer_reasons(user: User) -> serializers.OfferReportReasons:
    return serializers.OfferReportReasons(reasons=Reason.get_full_meta())


@blueprint.native_route("/offers/reports", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.UserReportedOffersResponse)
@authenticated_and_active_user_required
def user_reported_offers(user: User) -> serializers.UserReportedOffersResponse:
    return serializers.UserReportedOffersResponse(reportedOffers=user.reported_offers)  # type: ignore [call-arg]


@blueprint.native_route("/send_offer_webapp_link_by_email/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def send_offer_app_link(user: User, offer_id: int) -> None:
    """
    On iOS native app, users cannot book numeric offers with price > 0, so
    give them webapp link.
    """
    offer = (
        Offer.query.options(joinedload(Offer.venue))
        .filter(Offer.id == offer_id, Offer.validation == OfferValidationStatus.APPROVED)
        .first_or_404()
    )
    transactional_mails.send_offer_link_to_ios_user_email(user, offer)


@blueprint.native_route("/send_offer_link_by_push/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def send_offer_link_by_push(user: User, offer_id: int) -> None:
    offer = Offer.query.get_or_404(offer_id)
    if offer.validation != OfferValidationStatus.APPROVED:
        raise ResourceNotFoundError()
    push_notification_job.send_offer_link_by_push_job.delay(user.id, offer_id)


@blueprint.native_route("/subcategories/v2", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=subcategories_v2_serializers.SubcategoriesResponseModelv2)
def get_subcategories_v2() -> subcategories_v2_serializers.SubcategoriesResponseModelv2:
    return subcategories_v2_serializers.SubcategoriesResponseModelv2(
        subcategories=[
            subcategories_v2_serializers.SubcategoryResponseModelv2.from_orm(subcategory)
            for subcategory in subcategories_v2.ALL_SUBCATEGORIES
        ],
        searchGroups=[
            subcategories_v2_serializers.SearchGroupResponseModelv2.from_orm(search_group_name)
            for search_group_name in subcategories_v2.SearchGroups
        ],
        homepageLabels=[
            subcategories_v2_serializers.HomepageLabelResponseModelv2.from_orm(homepage_label_name)
            for homepage_label_name in subcategories_v2.HomepageLabels
        ],
        nativeCategories=[
            subcategories_v2_serializers.NativeCategoryResponseModelv2.from_orm(native_category)
            for native_category in subcategories_v2.NativeCategory
        ],
        genreTypes=[
            subcategories_v2_serializers.GenreTypeModel.from_orm(genre_type)
            for genre_type in subcategories_v2.GenreType
        ],
    )
