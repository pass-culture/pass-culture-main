from sqlalchemy.orm import joinedload

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.domain.user_emails import send_user_webapp_offer_link_email
from pcapi.models.product import Product
from pcapi.routes.native.security import authenticated_user_required
from pcapi.serialization.decorator import spectree_serialize

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
