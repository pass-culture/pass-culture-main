import argparse
import datetime
import json
import os
import time
import typing
import uuid

from pcapi.utils import requests


API_KEY = os.environ.get("PUBLIC_API_KEY")
CIPHER_KEY = os.environ.get("PUBLIC_CIPHER_KEY")
ENV = os.environ.get("PUBLIC_API_ENV", "testing")
BASE_URL = f"https://backend.{ENV}.passculture.team"


def post_to_endpoint(path: str, payload: dict) -> requests.Response:
    headers = {"Content-type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    response = requests.post(f"{BASE_URL}/{path}", json=payload, headers=headers)
    handle_response(response)
    return response


def handle_response(response: requests.Response) -> None:
    if not response.ok:
        print(response)
        print(json.dumps(response.headers.__dict__, indent=4))
        print(json.dumps(response.json(), indent=4))
        raise RuntimeError("Request failed")


def create_event(
    booking_allowed_datetime: datetime.datetime,
    publication_datetime: datetime.datetime,
    my_event_id: str,
    venue_id: int,
) -> dict[str, typing.Any]:
    event_payload = {
        "accessibility": {
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        },
        "bookingContact": "my.email@domain.com",
        "bookingAllowedDatetime": booking_allowed_datetime.isoformat(),
        "categoryRelatedFields": {"category": "CONCERT", "musicType": "RAP-HIP HOP"},
        "eventDuration": 60,
        "hasTicket": True,
        "idAtProvider": my_event_id,
        "location": {"type": "address", "addressId": 1, "venueId": venue_id},
        "name": f"Le Petit Prince {datetime.datetime.now(None).replace(microsecond=0).isoformat()}",
        "priceCategories": [{"idAtProvider": f"{my_event_id}-cat-carre-or", "label": "Carré or", "price": 1000}],
        "publicationDatetime": publication_datetime.isoformat(),
    }
    response = post_to_endpoint("public/offers/v1/events", event_payload)
    return response.json()


def create_stocks(pc_event_id: int, price_category_id: int, my_event_id: str) -> dict:
    def at_3pm_in_n_days(n: int) -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc).replace(
            hour=15, minute=0, second=0, microsecond=0
        ) + datetime.timedelta(days=n)

    stocks_payload = {
        "dates": [
            {
                "beginningDatetime": at_3pm_in_n_days(days_delta).isoformat(),
                "bookingLimitDatetime": at_3pm_in_n_days(days_delta).isoformat(),
                "idAtProvider": f"{my_event_id}-{uuid.uuid4()}",
                "priceCategoryId": price_category_id,
                "quantity": 10,
            }
            for days_delta in range(7, 10)
        ]
    }
    response = post_to_endpoint(f"public/offers/v1/events/{pc_event_id}/dates", stocks_payload)
    return response.json()


def _patch_booking(verb: str, token: str) -> requests.Response:
    headers = {"Content-type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    with requests.Session() as session:
        response = session.patch(f"{BASE_URL}/public/bookings/v1/{verb}/token/{token}", headers=headers)

    print(response.status_code)
    return response


def cancel_booking(token: str) -> None:
    _patch_booking("cancel", token)


def keep_booking(token: str) -> None:
    _patch_booking("keep", token)


def use_booking(token: str) -> None:
    _patch_booking("use", token)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage events, stocks, and bookings.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--create",
        action="store_true",
        help="Create a new event and associated stocks.",
    )
    group.add_argument(
        "--use-booking",
        metavar="TOKEN",
        help="Use booking with the specified token.",
    )
    group.add_argument(
        "--keep-booking",
        metavar="TOKEN",
        help="Keep a booking using the specified token.",
    )
    group.add_argument(
        "--cancel-booking",
        metavar="TOKEN",
        help="Cancel a booking using the specified token.",
    )

    args = parser.parse_args()

    if args.create:
        in_a_minute = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)
        booking_allowed_datetime = in_a_minute
        publication_datetime = in_a_minute
        my_event_id = f"test-id-{int(time.time())}"
        venue_id = 1111
        try:
            event = create_event(booking_allowed_datetime, publication_datetime, my_event_id, venue_id)
        except RuntimeError as exc:
            print(f"Error: {exc}")
            return
        else:
            print(f"Event {event['id']} successfully created")

        pc_event_id = event["id"]
        price_category_id = event["priceCategories"][0]["id"]
        try:
            stocks = create_stocks(pc_event_id, price_category_id, my_event_id)
        except RuntimeError as exc:
            print(f"Error: {exc}")
        else:
            print(f"Stocks {[stock['id'] for stock in stocks['dates']]} successfully created")

    elif args.use_booking:
        use_booking(args.use_booking)

    elif args.keep_booking:
        keep_booking(args.keep_booking)

    elif args.cancel_booking:
        cancel_booking(args.cancel_booking)


if __name__ == "__main__":
    main()
