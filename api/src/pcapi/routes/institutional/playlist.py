from sqlalchemy import orm as sqla_orm

from pcapi.core.criteria import models as criteria_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize

from . import serializers


PLAYLIST_MAX_SIZE = 10


@public_api.route("/institutional/playlist/<tag_name>", methods=["GET"])
@spectree_serialize(response_model=serializers.OffersResponse)
def get_offers_by_tag(tag_name: str) -> serializers.OffersResponse:
    offers = (
        offers_models.Offer.query.join(offers_models.Offer.criteria)
        .join(offers_models.Offer.stocks)
        .filter(
            criteria_models.Criterion.name == tag_name,
            offers_models.Offer.is_released_and_bookable,
        )
        .options(
            sqla_orm.joinedload(offers_models.Offer.stocks),
            sqla_orm.joinedload(offers_models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer),
            sqla_orm.joinedload(offers_models.Offer.mediations),
        )
        .limit(PLAYLIST_MAX_SIZE)
        .all()
    )
    return serializers.OffersResponse(__root__=[serializers.OfferResponse.from_orm(offer) for offer in offers])
