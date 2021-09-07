from sqlalchemy.orm import joinedload

from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api
from pcapi.core.offers.exceptions import OfferReportError
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Reason
from pcapi.core.users.models import User
from pcapi.domain.user_emails import send_user_webapp_offer_link_email
from pcapi.models import ApiErrors
from pcapi.models.product import Product
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize
from pcapi.workers.push_notification_job import send_offer_link_by_push_job

from . import blueprint
from .serialization import offers as serializers


@blueprint.native_v1.route("/offer/<int:offer_id>", methods=["GET"])
@spectree_serialize(
    response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404]
)  # type: ignore
def get_offer(offer_id: str) -> serializers.OfferResponse:
    offer = (
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

    return serializers.OfferResponse.from_orm(offer)


@blueprint.native_v1.route("/offer/<int:offer_id>/report", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)  # type: ignore
@authenticated_user_required
def report_offer(user: User, offer_id: int, body: serializers.OfferReportRequest) -> None:
    offer = Offer.query.get_or_404(offer_id)

    try:
        api.report_offer(user, offer, body.reason, body.custom_reason)
    except OfferReportError as error:
        raise ApiErrors({"code": error.code}, status_code=400)


@blueprint.native_v1.route("/offer/report/reasons", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.OfferReportReasons)  # type: ignore
@authenticated_user_required
def report_offer_reasons(user: User) -> serializers.OfferReportReasons:
    return serializers.OfferReportReasons(reasons=Reason.get_full_meta())


@blueprint.native_v1.route("/offers/reports", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=serializers.UserReportedOffersResponse)
@authenticated_user_required
def user_reported_offers(user: User) -> serializers.UserReportedOffersResponse:
    return serializers.UserReportedOffersResponse(reportedOffers=user.reported_offers)


@blueprint.native_v1.route("/send_offer_webapp_link_by_email/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)  # type: ignore
@authenticated_user_required
def send_offer_webapp_link(user: User, offer_id: int) -> None:
    """
    On iOS native app, users cannot book numeric offers with price > 0, so
    give them webapp link.
    """
    offer = Offer.query.options(joinedload(Offer.venue)).filter(Offer.id == offer_id).first_or_404()
    send_user_webapp_offer_link_email(user, offer)


@blueprint.native_v1.route("/send_offer_link_by_push/<int:offer_id>", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)  # type: ignore
@authenticated_user_required
def send_offer_link_by_push(user: User, offer_id: int) -> None:
    Offer.query.get_or_404(offer_id)
    send_offer_link_by_push_job.delay(user.id, offer_id)


@blueprint.native_v1.route("/subcategories", methods=["GET"])
@spectree_serialize(response_model=serializers.SubcategoriesResponseModel)
def get_subcategories() -> serializers.SubcategoriesResponseModel:
    return serializers.SubcategoriesResponseModel(
        subcategories=[
            serializers.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in subcategories.ALL_SUBCATEGORIES
        ],
    )
