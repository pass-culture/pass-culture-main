from sqlalchemy.orm import joinedload

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models.product import Product
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
