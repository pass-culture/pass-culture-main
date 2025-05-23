import sqlalchemy.orm as sa_orm

from pcapi.core.criteria import models as criteria_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.routes.institutional.blueprint import api
from pcapi.routes.institutional.blueprint import institutional
from pcapi.routes.institutional.security import institutional_api_key_required
from pcapi.serialization.decorator import spectree_serialize

from . import serializers


PLAYLIST_MAX_SIZE = 10


@institutional.route("/playlist/<tag_name>", methods=["GET"])
@spectree_serialize(response_model=serializers.OffersResponse, api=api)
@institutional_api_key_required
def get_offers_by_tag(tag_name: str) -> serializers.OffersResponse:
    offers = (
        db.session.query(offers_models.Offer)
        .join(offers_models.Offer.criteria)
        .join(offers_models.Offer.stocks)
        .filter(
            criteria_models.Criterion.name == tag_name,
            offers_models.Offer.is_released_and_bookable,
        )
        .options(
            sa_orm.joinedload(offers_models.Offer.stocks),
            sa_orm.joinedload(offers_models.Offer.venue).joinedload(offerers_models.Venue.managingOfferer),
            sa_orm.joinedload(offers_models.Offer.mediations),
        )
        .limit(PLAYLIST_MAX_SIZE)
        .all()
    )
    return serializers.OffersResponse(__root__=[serializers.OfferResponse.from_orm(offer) for offer in offers])
