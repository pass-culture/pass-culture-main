import functools
import inspect
import logging
from typing import Any
from typing import Callable
from typing import TypeVar

from pcapi.core.providers.clients import cinema_client
from pcapi.utils.requests import exceptions as requests_exception

from . import exceptions


logger = logging.getLogger(__name__)


class ExternalBookingDecoratorException(Exception):
    pass


def _extract_logging_information(client_func: Callable, *args: list[Any], **kwargs: Any) -> dict:
    """
    Return a dictionary to be passed to the `extra` parameter of the logging function.

    The returned dictionary contains the following keys:
        - "cinema_id" (int): The ID of the cinema from the pivot table.
        - "client" (str): The client used for the request (e.g., `EMSClientAPI`).
        - "method" (str): The instance method used for the request (e.g., `book_ticket`).
        - "method_params" (dict): The parameters passed to the method. Example:
            {
                "show_id": "12345",             # ID of the show
                "booking": "<Booking #1>",      # Stringified Booking instance
                "beneficiary": "<User #3>",     # Stringified User instance
            }
    """
    self = args[0]
    assert isinstance(self, cinema_client.CinemaAPIClient)  # to make mypy happy
    # as client_func is an instance method of `ExternalBookingsClientAPI`, self should have a `cinema_id`
    cinema_id = self.cinema_id

    func_arguments = inspect.signature(client_func).bind(*args, **kwargs).arguments
    # stringify argument values
    method_params = {argument_name: str(argument_value) for argument_name, argument_value in func_arguments.items()}
    method_params.pop("self")

    return {
        "client": self.__class__.__name__,  # class name
        "method": client_func.__name__,  # method name
        "cinema_id": cinema_id,
        "method_params": method_params,
    }


# typing to ensure that mypy understands the wrapped function signature has not changed
F = TypeVar("F", bound=Callable[..., Any])


def catch_cinema_provider_request_timeout(client_func: F) -> F:
    """
    Decorator that catches HTTP Timeout errors, logs them and then raises `ExternalBookingTimeoutException`.
    This decorator can only be applied to instance methods of classes inheriting from `ExternalBookingsClientAPI`
    """

    @functools.wraps(client_func)
    def wrapped_func(*args: Any, **kwargs: Any) -> Any:
        if len(args) == 0 or not isinstance(args[0], cinema_client.CinemaAPIClient):
            raise ExternalBookingDecoratorException(
                "`catch_request_timeout` can only be applied to an instance method of a class inheriting from `ExternalBookingsClientAPI`"
            )

        try:
            return client_func(*args, **kwargs)
        except (requests_exception.Timeout, requests_exception.ReadTimeout) as e:
            extra = _extract_logging_information(client_func, *args, **kwargs)
            if e.request:
                extra["request"] = {"method": e.request.method, "url": e.request.url}

            logger.warning("Cinema Provider API Request Timeout", extra=extra)
            raise exceptions.ExternalBookingTimeoutException()

    return wrapped_func  # type: ignore[return-value]
