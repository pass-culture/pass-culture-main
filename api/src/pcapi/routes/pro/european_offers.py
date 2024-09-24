import logging

from flask_login import login_required

from pcapi import repository
from pcapi.core.european_offers import api as european_offers_api
from pcapi.routes.apis import private_api
from pcapi.routes.native.v1.serialization.european_offers import EuropeanOfferResponse
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/european_offers", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=EuropeanOfferResponse,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
def post_european_offer(body: european_offers_api.EuropeanOfferData) -> EuropeanOfferResponse:
    with repository.transaction():
        offer = european_offers_api.create_offer(body)

    return EuropeanOfferResponse.from_orm(offer)
