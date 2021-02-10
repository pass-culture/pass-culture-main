import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as exceptions
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.security import authenticated_user_required
from pcapi.routes.native.v1.serialization.booking import BookOfferRequest
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@blueprint.native_v1.route("/book_offer", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def book_offer(user: User, body: BookOfferRequest) -> None:
    stock = Stock.query.get(body.stock_id)
    if not stock:
        raise ApiErrors({"stock": "stock introuvable"}, status_code=404)

    try:
        bookings_api.book_offer(
            beneficiary=user,
            stock=stock,
            quantity=body.quantity,
        )

    except (
        exceptions.UserHasInsufficientFunds,
        exceptions.DigitalExpenseLimitHasBeenReached,
        exceptions.PhysicalExpenseLimitHasBeenReached,
    ):
        raise ApiErrors({"code": "INSUFFICIENT_CREDIT"})

    except exceptions.OfferIsAlreadyBooked:
        raise ApiErrors({"code": "ALREADY_BOOKED"})

    except exceptions.StockIsNotBookable:
        raise ApiErrors({"code": "STOCK_NOT_BOOKABLE"})
