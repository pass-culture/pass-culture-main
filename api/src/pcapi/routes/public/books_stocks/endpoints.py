import logging

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.workers.synchronize_stocks_job import synchronize_stocks_job

from . import blueprint
from . import serialization


logger = logging.getLogger(__name__)


# This api allow to update stocks for a venue
# DEPRECATED: use individual offer api instead
@blueprint.deprecated_books_stocks_blueprint.route("/venue/<int:venue_id>/stocks", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[401, 404],
    api=spectree_schemas.deprecated_public_api_schema,
    tags=[tags.DEPRECATED_VENUES_STOCK_TAG],
    deprecated=True,
)
@api_key_required
def update_stocks(venue_id: int, body: serialization.UpdateVenueStocksBodyModel) -> None:
    offerer_id = current_api_key.offererId
    venue = Venue.query.join(Offerer).filter(Venue.id == venue_id, Offerer.id == offerer_id).first_or_404()

    stock_details = _build_stock_details_from_body(body.stocks, venue.id)
    synchronize_stocks_job.delay(stock_details, venue.id)


def _build_stock_details_from_body(raw_stocks: list[serialization.UpdateVenueStockBodyModel], venue_id: int) -> list:
    stock_details = {}
    for stock in raw_stocks:
        stock_details[stock.ref] = {
            "products_provider_reference": stock.ref,
            "offers_provider_reference": stock.ref,
            "stocks_provider_reference": f"{stock.ref}@{str(venue_id)}",
            "available_quantity": stock.available,
            "price": stock.price,
        }

    return list(stock_details.values())
