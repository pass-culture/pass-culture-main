"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-functionnal-tests-for-celery \
  -f NAMESPACE=test-celery-things \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import tasks as bookings_tasks
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import tasks as offers_tasks
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def test_send_offer_link_by_push() -> None:
    offer = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.validation == offers_models.OfferValidationStatus.APPROVED)
        .first()
    )
    user = db.session.query(users_models.User).first()
    payload = offers_tasks.SendOfferLinkByPushPayload(user_id=user.id, offer_id=offer.id)
    offers_tasks.send_offer_link_by_push_task.delay(payload.model_dump())


def test_send_today_stock_notification() -> None:
    booking = (
        db.session.query(bookings_models.Booking)
        .filter(bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED)
        .first()
    )
    stock = booking.stock

    try:
        payload = bookings_tasks.SendTodayStockNotificationPayload(stock_id=stock.id)
        bookings_tasks.send_today_stock_notification.delay(payload.model_dump())
    except Exception:
        logger.exception("Could not send today stock notification", extra={"stock": stock.id})


if __name__ == "__main__":
    app.app_context().push()
    test_send_offer_link_by_push()
    test_send_today_stock_notification()
