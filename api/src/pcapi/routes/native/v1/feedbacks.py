import logging

from flask_login import current_user
from sqlalchemy.orm import joinedload

from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users.young_status import young_status
from pcapi.models import db
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import feedbacks as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/feedback", methods=["POST"])
@spectree_serialize(on_success_status=204, api=blueprint.api)
@authenticated_and_active_user_required
def post_feedback(body: serializers.PostFeedbackBody) -> None:
    not_cancelled_bookings_query = (
        db.session.query(bookings_models.Booking)
        .options(
            joinedload(bookings_models.Booking.stock)
            .joinedload(offers_models.Stock.offer)
            .load_only(offers_models.Offer.id)
        )
        .filter(
            bookings_models.Booking.userId == current_user.id,
            bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED,
        )
    )

    young_status_type = getattr(young_status(current_user), "status_type", None)

    logger.info(
        "User feedback",
        extra={
            "feedback": body.feedback,
            "age": current_user.age,
            "status": young_status_type.value if young_status_type is not None else None,
            "firstDepositActivationDate": current_user.first_deposit_activation_date,
            "bookings_count": not_cancelled_bookings_query.count(),
            "analyticsSource": "app-native",
        },
        technical_message_id="user_feedback",
    )
