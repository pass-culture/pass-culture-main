from sqlalchemy.orm import joinedload

from pcapi.core.booking_providers.models import BookingProviderName
from pcapi.core.booking_providers.models import VenueBookingProvider
from pcapi.core.categories import subcategories
from pcapi.core.categories import subcategories_v2
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api
from pcapi.core.offers.exceptions import OfferReportError
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Reason
import pcapi.core.providers.models as providers_models
from pcapi.core.users.models import User
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.workers import push_notification_job

from . import blueprint
from .serialization import offers as serializers
from .serialization import subcategories_v2 as subcategories_v2_serializers


# It will break the WebApp v2 proxy in case of endpoint modification. Read https://github.com/pass-culture/pass-culture-app-native/pull/2808/files#r844891000
@blueprint.native_v1.route("/offer/<int:offer_id>", methods=["GET"])
@spectree_serialize(response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404])
def get_offer(offer_id: str) -> serializers.OfferResponse:
    offer: Offer = (
        Offer.query.options(joinedload(Offer.stocks))
        .options(
            joinedload(Offer.venue)
            .joinedload(Venue.managingOfferer)
            .load_only(Offerer.name, Offerer.validationToken, Offerer.isActive)
        )
        .options(joinedload(Offer.mediations))
        .options(joinedload(Offer.product).load_only(Product.id, Product.thumbCount))
        .filter(Offer.id == offer_id)
        .first_or_404()
    )

    if (
        feature.FeatureToggle.ENABLE_CDS_IMPLEMENTATION.is_active()
        and offer.subcategory.id == subcategories.SEANCE_CINE.id
    ):
        venue_booking_provider = (
            VenueBookingProvider.query.filter(
                VenueBookingProvider.venueId == offer.venueId,
                VenueBookingProvider.isActive,
            )
            .options(joinedload(VenueBookingProvider.bookingProvider, innerjoin=True))
            .one_or_none()
        )
        venue_cinema_pivot = providers_models.CinemaProviderPivot.query.filter_by(venueId=offer.venueId).one_or_none()
        if (
            venue_booking_provider
            and venue_booking_provider.bookingProvider.name == BookingProviderName.CINE_DIGITAL_SERVICE
            and venue_cinema_pivot
            and offer.lastProviderId == venue_cinema_pivot.providerId
        ):
            api.update_stock_quantity_to_match_booking_provider_remaining_place(offer, venue_booking_provider)

    return serializers.OfferResponse.from_orm(offer)


@blueprint.native_v1.route("/offer/<int:offer_id>/report", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def report_offer(user: User, offer_id: int, body: serializers.OfferReportRequest) -> None:
    offer = Offer.query.get_or_404(offer_id)

    try:
        api.report_offer(user, offer, body.reason, body.custom_reason)
    except OfferReportError as error:
        raise ApiErrors({"code": error.code}, status_code=400)


@blueprint.native_v1.route("/offer/report/reasons", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.OfferReportReasons)
@authenticated_and_active_user_required
def report_offer_reasons(user: User) -> serializers.OfferReportReasons:
    return serializers.OfferReportReasons(reasons=Reason.get_full_meta())


@blueprint.native_v1.route("/offers/reports", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.UserReportedOffersResponse)
@authenticated_and_active_user_required
def user_reported_offers(user: User) -> serializers.UserReportedOffersResponse:
    return serializers.UserReportedOffersResponse(reportedOffers=user.reported_offers)


@blueprint.native_v1.route("/send_offer_webapp_link_by_email/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def send_offer_app_link(user: User, offer_id: int) -> None:
    """
    On iOS native app, users cannot book numeric offers with price > 0, so
    give them webapp link.
    """
    offer = Offer.query.options(joinedload(Offer.venue)).filter(Offer.id == offer_id).first_or_404()
    transactional_mails.send_offer_link_to_ios_user_email(user, offer)


@blueprint.native_v1.route("/send_offer_link_by_push/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def send_offer_link_by_push(user: User, offer_id: int) -> None:
    Offer.query.get_or_404(offer_id)
    push_notification_job.send_offer_link_by_push_job.delay(user.id, offer_id)


@blueprint.native_v1.route("/subcategories", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SubcategoriesResponseModel)
def get_subcategories() -> serializers.SubcategoriesResponseModel:
    return serializers.SubcategoriesResponseModel(
        subcategories=[
            serializers.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in subcategories.ALL_SUBCATEGORIES
        ],
        searchGroups=[
            serializers.SearchGroupResponseModel.from_orm(search_group_name)
            for search_group_name in subcategories.SearchGroups
        ],
        homepageLabels=[
            serializers.HomepageLabelResponseModel.from_orm(homepage_label_name)
            for homepage_label_name in subcategories.HomepageLabels
        ],
    )


@blueprint.native_v1.route("/subcategories/v2", methods=["GET"])
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
    )
