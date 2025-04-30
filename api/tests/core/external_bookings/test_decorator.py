import logging
from unittest.mock import Mock

import pytest

from pcapi.core.bookings import models as bookings_models
from pcapi.core.external_bookings import models as external_bookings_models
from pcapi.core.external_bookings.decorators import ExternalBookingDecoratorException
from pcapi.core.external_bookings.decorators import catch_cinema_provider_request_timeout
from pcapi.core.external_bookings.exceptions import ExternalBookingTimeoutException
from pcapi.core.users import models as users_models
from pcapi.utils.requests import requests


class FakeExternalBookingClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(self, cinema_id: str, connector) -> None:
        super().__init__(cinema_id)
        self.connector = connector

    @catch_cinema_provider_request_timeout
    def get_film_showtimes_stocks(self, film_id):
        return self.connector.make_request(film_id)

    @catch_cinema_provider_request_timeout
    def book_ticket(self, show_id, booking, beneficiary):
        return self.connector.make_request(show_id, booking, beneficiary)

    def cancel_booking(self, barcodes):
        pass

    def get_shows_remaining_places(self, shows_id):
        return {}


class FakeClass:
    @catch_cinema_provider_request_timeout
    def function_that_cannot_be_decorated(self, a):
        pass


@catch_cinema_provider_request_timeout
def another_func_that_cannot_be_decorated():
    pass


class CatchCinemaProviderRequestTimeoutTest:
    def test_should_raise_error_because_wrapped_function_is_not_an_instance_method(self):
        fake_class = FakeClass()

        with pytest.raises(ExternalBookingDecoratorException):
            fake_class.function_that_cannot_be_decorated("coucou")

        with pytest.raises(ExternalBookingDecoratorException):
            another_func_that_cannot_be_decorated()

    def test_should_raise_understandable_error_if_the_decorated_func_is_called_with_incorrect_params(self):
        client = FakeExternalBookingClientAPI(cinema_id=1, connector=Mock())

        with pytest.raises(TypeError) as exception:
            # We ignore the pytest error because we test incorrect args here
            client.get_film_showtimes_stocks(12, show_id=1)
            assert (
                str(exception.value)
                == "TypeError: get_film_showtimes_stocks() got an unexpected keyword argument 'show_id'"
            )

        with pytest.raises(TypeError) as exception:
            client.get_film_showtimes_stocks(12, 13, 24)
            assert (
                str(exception.value)
                == "TypeError: get_film_showtimes_stocks() takes 1 positional arguments but 3 were given"
            )

    @pytest.mark.parametrize(
        "args_list,kwargs_dict,exception_class,request_mock,expected_extra",
        [
            (
                [12345],
                {"booking": bookings_models.Booking(id=1), "beneficiary": users_models.User(id=3)},
                requests.exceptions.ReadTimeout,
                Mock(url="https://provider.com/route/un/peu/instable", method="POST"),
                {
                    "cinema_id": 789,
                    "method": "book_ticket",
                    "client": "FakeExternalBookingClientAPI",
                    "method_params": {
                        "show_id": "12345",
                        "booking": "<Booking #1>",
                        "beneficiary": "<User #3>",
                    },
                    "request": {"url": "https://provider.com/route/un/peu/instable", "method": "POST"},
                },
            ),
            (
                [678, bookings_models.Booking(id=1), users_models.User(id=3)],
                {},
                requests.exceptions.Timeout,
                Mock(url="https://provider.com/route/qui/timeout", method="GET"),
                {
                    "cinema_id": 789,
                    "method": "book_ticket",
                    "client": "FakeExternalBookingClientAPI",
                    "method_params": {
                        "show_id": "678",
                        "booking": "<Booking #1>",
                        "beneficiary": "<User #3>",
                    },
                    "request": {"url": "https://provider.com/route/qui/timeout", "method": "GET"},
                },
            ),
            (
                [],
                {
                    "show_id": 562,
                    "booking": bookings_models.Booking(id=4567),
                    "beneficiary": users_models.User(id=12345767),
                },
                requests.exceptions.ReadTimeout,
                Mock(url="https://provider.com/oh/zut/encore/un/timeout", method="PUT"),
                {
                    "cinema_id": 789,
                    "method": "book_ticket",
                    "client": "FakeExternalBookingClientAPI",
                    "method_params": {
                        "show_id": "562",
                        "booking": "<Booking #4567>",
                        "beneficiary": "<User #12345767>",
                    },
                    "request": {"url": "https://provider.com/oh/zut/encore/un/timeout", "method": "PUT"},
                },
            ),
        ],
    )
    def test_should_log_error(self, args_list, kwargs_dict, exception_class, request_mock, expected_extra, caplog):
        connector = Mock()
        connector.make_request.side_effect = exception_class(request=request_mock)
        client = FakeExternalBookingClientAPI(cinema_id=789, connector=connector)

        with caplog.at_level(logging.WARNING):
            with pytest.raises(ExternalBookingTimeoutException):
                client.book_ticket(*args_list, **kwargs_dict)

        assert caplog.records[0].extra == expected_extra
        assert caplog.messages[0] == "Cinema Provider API Request Timeout"
