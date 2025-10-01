import json
import logging
import typing
from dataclasses import dataclass
from functools import partial
from functools import wraps

import pcapi.core.bookings.models as bookings_models
import pcapi.core.users.models as users_models
from pcapi.utils import requests
from pcapi.utils.cache import get_from_cache


logger = logging.getLogger(__name__)


@dataclass
class Ticket:
    barcode: str
    seat_number: str | None
    additional_information: dict | None = None


@dataclass
class Movie:
    id: str
    title: str
    duration: int  # duration in minutes
    description: str
    poster_url: str | None
    visa: str | None
    allocine_id: str | None = None


class ExternalBookingsClientAPI:
    def __init__(self, cinema_id: str, request_timeout: None | int = None) -> None:
        self.cinema_id = cinema_id
        self.request_timeout = request_timeout

    def get_film_showtimes_stocks(self, film_id: str) -> dict[str, int]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def cancel_booking(self, barcodes: list[str]) -> None:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[Ticket]:
        raise NotImplementedError("Should be implemented in subclass (abstract method)")

    def get_movie_poster(self, image_url: str) -> bytes:
        """
        Try to fetch the image

        If the request fails (timeout or invalid response) this function logs a warning
        and returns an empty bytes object
        """
        try:
            api_response = requests.get(image_url)  # can timeout

            if api_response.status_code != 200:  # response is not a success
                raise Exception()
        except Exception:
            logger.warning(
                "Could not fetch movie poster",
                extra={
                    "client": self.__class__.__name__,
                    "url": image_url,
                },
            )
            return bytes()

        return api_response.content


def cache_external_call(key_template: str, expire: int | None = None) -> typing.Callable:
    """
    Cache the result of a external call to a provider.
    Uses the cinema_id of ClientAPI instance and the arguments pass to the function as key
    (similar to what `@lru_cache` is doing)

    The function cached should return a string using `json.dumps`
    """

    def decorator(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        def func_to_cache(instance: ExternalBookingsClientAPI, *args: typing.Any, **kwargs: typing.Any) -> list | dict:
            key_args = (instance.cinema_id, *args)
            retriever = partial(func, instance, *args, **kwargs)
            result_as_json = get_from_cache(
                key_template=key_template, key_args=key_args, expire=expire, retriever=retriever
            )
            if not isinstance(result_as_json, str):
                raise AssertionError("This function is meant to be used with functions returning data as JSON")
            return json.loads(result_as_json)

        return func_to_cache

    return decorator
