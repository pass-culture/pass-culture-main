import pytest

from pcapi import settings
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


pytestmark = pytest.mark.usefixtures("db_session")


def test_send_notification_task(client, requests_mock):
    # Given
    data = {
        "action": "BOOK",
        "stock_id": 1,
        "booking_creation_date": "2021-10-01T00:00:00+00:00",
        "booking_confirmation_date": "2021-10-01T00:00:00+00:00",
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

    # When
    response = client.post(
        f"{settings.API_URL}/cloud-tasks/external_api/booking_notification",
        json={"notificationUrl": "https://example.com/notify", "data": data, "signature": "M0ckS1gn@TuR3"},
        headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
    )

    # Then
    assert response.status_code == 204
    assert requests_mock.last_request.headers["PassCulture-Signature"] == "M0ckS1gn@TuR3"
