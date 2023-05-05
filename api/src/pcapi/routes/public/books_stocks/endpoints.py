import logging

from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.routes.public import blueprints
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.workers.synchronize_stocks_job import synchronize_stocks_job

from . import serialization


logger = logging.getLogger(__name__)


@blueprints.v2_prefixed_public_api.route("/venue/<int:venue_id>/stocks", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[401, 404],
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API Stocks"],
)
@api_key_required
def update_stocks(venue_id: int, body: serialization.UpdateVenueStocksBodyModel) -> None:
    # in French, to be used by Swagger for the API documentation
    """Mise à jour des stocks d'un lieu enregistré auprès du pass Culture.

    Seuls les livres, préalablement présents dans le catalogue du pass Culture seront pris en compte, tous les autres stocks
    seront filtrés.

    Les stocks sont référencés par leur isbn au format EAN13.

    Le champ "available" représente la quantité de stocks disponible en librairie.
    Le champ "price" correspond au prix en euros.

    Le paramètre {venue_id} correspond à un lieu qui doit être attaché à la structure à laquelle la clé d'API utilisée est reliée.
    """
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
