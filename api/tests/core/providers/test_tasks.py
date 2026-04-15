import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.providers import tasks


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.features(WIP_ASYNCHRONOUS_CELERY_EXTERNAL_BOOKING=True)
def test_send_notification_task(requests_mock):
    data = {
        "action": "BOOK",
        "stock_id": 1,
        "booking_quantity": 1,
        "offer_ean": "1234567890123",
        "offer_id": 1,
        "offer_name": "Offer name",
        "offer_price": 100,
        "price_category_id": 1,
        "price_category_label": "Price category label",
        "user_birth_date": "1990-01-01",
        "user_email": "user@email.fr",
        "user_last_name": "Doe",
        "user_phone": "0123456789",
        "venue_id": 1,
        "venue_name": "Venue name",
        "venue_address": "Venue address",
        "venue_department_code": "75",
        "user_first_name": "John",
        "booking_id": 1,
    }
    requests_mock.post("https://example.com/notify", status_code=200, json=data)

    tasks.external_api_booking_notification_task.run(
        tasks.ExternalApiBookingNotificationTaskPayload(
            data=tasks.ExternalApiBookingNotificationRequest.build(
                action=tasks.BookingAction.BOOK, booking=BookingFactory()
            ),
            signature="M0ckS1gn@TuR3",
            notificationUrl="https://example.com/notify",
        )
    )

    assert requests_mock.last_request.headers["PassCulture-Signature"] == "M0ckS1gn@TuR3"
