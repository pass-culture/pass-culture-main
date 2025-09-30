import datetime
import json
import logging
import typing
from functools import wraps

import regex
from pydantic.v1 import parse_obj_as

import pcapi.core.bookings.constants as bookings_constants
import pcapi.core.bookings.models as bookings_models
import pcapi.core.external_bookings.boost.exceptions as boost_exceptions
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.external_bookings.models as external_bookings_models
import pcapi.core.providers.repository as providers_repository
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core.external_bookings.decorators import catch_cinema_provider_request_timeout
from pcapi.core.providers.models import BoostCinemaDetails
from pcapi.utils import repository
from pcapi.utils import requests
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.queue import add_to_queue

from . import constants
from . import serializers


logger = logging.getLogger(__name__)


_BOOST_NOT_ENOUGH_SEAT_ERROR_PATTERN = (
    r"Insufficient number of seats for the showtime \d+, remaining: (\d), required: \d"
)


def get_pcu_pricing_if_exists(
    showtime_pricing_list: list[serializers.ShowtimePricing],
) -> serializers.ShowtimePricing | None:
    pcu_pricings = [
        pricing
        for pricing in showtime_pricing_list
        if pricing.pricingCode in constants.BOOST_PASS_CULTURE_PRICING_CODES
    ]
    if len(pcu_pricings) == 0:
        return None

    pcu_pricings_sorted_by_code = sorted(
        pcu_pricings, key=lambda p: constants.BOOST_PASS_CULTURE_PRICING_CODES.index(p.pricingCode)
    )
    first_pcu_pricing = pcu_pricings_sorted_by_code[0]

    if len(pcu_pricings) > 1:
        logger.warning(
            "There are several pass Culture Pricings for this Showtime, we will use %s", first_pcu_pricing.pricingCode
        )

    return first_pcu_pricing


def _log_external_call(
    client: external_bookings_models.ExternalBookingsClientAPI,
    method: str,
    response: dict | list[dict] | list,
    query_params: dict | None = None,
) -> None:
    client_name = client.__class__.__name__
    cinema_id = client.cinema_id
    extra = {
        "api_client": client_name,
        "cinema_id": cinema_id,
        "method": method,
        "response": response,
    }

    if query_params:
        extra["query_params"] = query_params

    logger.debug("[CINEMA] Call to external API", extra=extra)


def _raise_for_status(response: requests.Response, cinema_api_token: str | None, request_detail: str) -> None:
    if response.status_code >= 400:
        reason = _extract_reason_from_response(response)
        message = _extract_message_from_response(response)
        if reason and cinema_api_token:
            error_message = reason.replace(cinema_api_token, "")

        logger.warning(
            "[Boost] Error calling API",
            extra={"message_content": message, "status_code": response.status_code, "request_detail": request_detail},
        )

        if response.status_code == 401:
            raise boost_exceptions.BoostInvalidTokenException(f"Boost: {message}")

        if regex.match(_BOOST_NOT_ENOUGH_SEAT_ERROR_PATTERN, message):
            remaining_seats = int(regex.findall(_BOOST_NOT_ENOUGH_SEAT_ERROR_PATTERN, message)[0])
            raise external_bookings_exceptions.ExternalBookingNotEnoughSeatsError(remaining_seats)

        if "No showtime found" in message:
            raise external_bookings_exceptions.ExternalBookingShowDoesNotExistError()

        raise boost_exceptions.BoostAPIException(
            f"Error on Boost API on {request_detail} : {error_message} - {message}"
        )


def _extract_reason_from_response(response: requests.Response) -> str:
    # from requests.Response.raise_for_status()
    reason = response.reason

    if isinstance(response.reason, bytes):
        try:
            reason = reason.decode("utf-8")
        except UnicodeDecodeError:
            reason = reason.decode("iso-8859-1")

    return reason


def _extract_message_from_response(response: requests.Response) -> str:
    try:
        content = response.json()
        message = content.get("message", "")
    except requests.exceptions.JSONDecodeError:
        message = response.content
    return message


# typing to ensure that mypy understands the wrapped function signature has not changed
F = typing.TypeVar("F", bound=typing.Callable[..., typing.Any])


def _retry_if_jwt_token_is_invalid(func: F) -> F:
    """
    If the first call to Boost API fails because of an invalid JWT token,
    this decorator forces re-authentication by unsetting the current token
    and retries the call.

    :func: Client method making an authenticated call to Boost API
    """

    @wraps(func)
    def decorated_func(client: "BoostClientAPI", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        try:
            return func(client, *args, **kwargs)
        except boost_exceptions.BoostInvalidTokenException:
            # if the token is invalid, we unset current token to force re-authentication
            client._unset_cinema_details_token()
            return func(client, *args, **kwargs)

    return decorated_func  # type: ignore[return-value]


class BoostClientAPI(external_bookings_models.ExternalBookingsClientAPI):
    def __init__(
        self,
        cinema_id: str,
        request_timeout: None | int = None,
        cinema_details: None | BoostCinemaDetails = None,
    ):
        super().__init__(cinema_id=cinema_id, request_timeout=request_timeout)
        self.cinema_details = cinema_details or providers_repository.get_boost_cinema_details(cinema_id)

    def _generate_jwt_token(self) -> tuple[str, datetime.datetime]:
        """
        Make POST request to generate JWT token

        The generated token is valid for 24H.

        :return: jwt token, token expiration datetime
        :raise: BoostLoginException
        """
        jwt_expiration_datetime = get_naive_utc_now() + datetime.timedelta(hours=24)
        url = f"{self.cinema_details.cinemaUrl}api/vendors/login"

        try:
            response = requests.post(
                url,
                json={
                    "username": settings.BOOST_API_USERNAME,
                    "password": settings.BOOST_API_PASSWORD,
                    "stationName": f"pcapi - {settings.ENV}",
                },
                params={"ignore_device": True},
            )
        except requests.exceptions.RequestException as exc:
            raise boost_exceptions.BoostLoginException(f"Network error on Boost API: {url}") from exc

        if response.status_code != 200:
            message = _extract_message_from_response(response)
            raise boost_exceptions.BoostLoginException(
                f"Unexpected {response.status_code} response from Boost login API on {response.request.url}: {message}"
            )

        content = response.json()
        login_info = parse_obj_as(serializers.LoginBoost, content)
        token = login_info.token
        if not token:
            raise boost_exceptions.BoostLoginException("No token received from Boost API")

        return token, jwt_expiration_datetime

    def _refresh_cinema_details_token(self) -> None:
        """
        Make call to generate JWT token & persist it in DB
        """
        jwt_token, jwt_expiration_datetime = self._generate_jwt_token()
        self.cinema_details.token = jwt_token
        self.cinema_details.tokenExpirationDate = jwt_expiration_datetime
        repository.save()

    def _unset_cinema_details_token(self) -> None:
        """
        Set cinema_details token information to `None` & persist it in DB
        """
        self.cinema_details.token = None
        self.cinema_details.tokenExpirationDate = None
        repository.save()

    def _get_authentication_header(self) -> dict:
        """
        Return headers dict to authenticate request
        """
        if (
            not self.cinema_details.token
            or not self.cinema_details.tokenExpirationDate
            or self.cinema_details.tokenExpirationDate < get_naive_utc_now()
        ):
            self._refresh_cinema_details_token()

        return {"Authorization": f"Bearer {self.cinema_details.token}"}

    @_retry_if_jwt_token_is_invalid
    def _authenticated_get(self, url: str, params: dict | None = None) -> dict:
        """
        Make an authenticated GET request on given URL
        """
        auth_headers = self._get_authentication_header()
        response = requests.get(url, headers=auth_headers, timeout=self.request_timeout, params=params)
        _raise_for_status(response, self.cinema_details.token, f"GET {url}")
        data = response.json()
        _log_external_call(self, f"GET {url}", data, query_params=params)
        return data

    @_retry_if_jwt_token_is_invalid
    def _authenticated_put(self, url: str, payload: str) -> None:
        """
        Make an authenticated PUT request on given URL
        """
        auth_headers = self._get_authentication_header()
        response = requests.put(url, headers=auth_headers, timeout=self.request_timeout, data=payload)
        _raise_for_status(response, self.cinema_details.token, f"PUT {url}")

    @_retry_if_jwt_token_is_invalid
    def _authenticated_post(self, url: str, payload: str | None = None) -> dict | list[dict] | list | None:
        """
        Make an authenticated POST request on given URL
        """
        auth_headers = self._get_authentication_header()
        response = requests.post(url, headers=auth_headers, timeout=self.request_timeout, data=payload)
        _raise_for_status(response, self.cinema_details.token, f"POST {url}")
        return response.json()

    # method used by BO to test pivot table is correctly set
    def test_jwt_token_generation(self) -> None:
        self._generate_jwt_token()

    def invalidate_jwt_token(self) -> None:
        """
        Invalidate active JWT token on Boost side and unset it in our DB
        """
        if not self.cinema_details.token:
            return
        self._authenticated_post(f"{self.cinema_details.cinemaUrl}api/vendors/logout")
        self._unset_cinema_details_token()

    def get_shows_remaining_places(self, shows_id: list[int]) -> dict[str, int]:
        raise NotImplementedError()

    @external_bookings_models.cache_external_call(
        key_template=constants.BOOST_SHOWTIMES_STOCKS_CACHE_KEY, expire=constants.BOOST_SHOWTIMES_STOCKS_CACHE_TIMEOUT
    )
    def get_film_showtimes_stocks(self, film_id: str) -> str:
        showtimes = self.get_showtimes(film=int(film_id))
        return json.dumps({showtime.id: showtime.numberSeatsRemaining for showtime in showtimes})

    def cancel_booking(self, barcodes: list[str]) -> None:
        barcodes = list(set(barcodes))
        sale_cancel_items = []
        for barcode in barcodes:
            sale_cancel_item = serializers.SaleCancelItem(
                code=barcode, refundType=constants.BOOST_PASS_CULTURE_REFUND_TYPE
            )
            sale_cancel_items.append(sale_cancel_item)

        sale_cancel = serializers.SaleCancel(sales=sale_cancel_items)
        self._authenticated_put(
            f"{self.cinema_details.cinemaUrl}api/sale/orderCancel",
            payload=sale_cancel.json(by_alias=True),
        )

    @catch_cinema_provider_request_timeout
    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[external_bookings_models.Ticket]:
        quantity = booking.quantity
        showtime = self.get_showtime(show_id)
        pcu_pricing = get_pcu_pricing_if_exists(showtime.showtimePricing)
        if not pcu_pricing:
            logger.warning(
                "[Boost] pass Culture pricing not found",
                extra={"show_id": show_id, "user_id": beneficiary.id},
            )
            # not a totally appropriate exception, we raise it to set the stock quantity to 0
            # as a beneficiary cannot book a show if there is no pass Culture pricing
            raise external_bookings_exceptions.ExternalBookingNotEnoughSeatsError(remainingQuantity=0)

        basket_items = [serializers.BasketItem(idShowtimePricing=pcu_pricing.id, quantity=quantity)]
        sale_body = serializers.SaleRequest(
            codePayment=constants.BOOST_PASS_CULTURE_CODE_PAYMENT, basketItems=basket_items, idsBeforeSale=None
        )

        # step 1: preparation
        sale_preparation_response = self._authenticated_post(
            f"{self.cinema_details.cinemaUrl}api/sale/complete",
            payload=sale_body.json(by_alias=True),
        )
        sale_preparation = parse_obj_as(serializers.SalePreparationResponse, sale_preparation_response)

        # step 2: confirmation
        sale_body.idsBeforeSale = str(sale_preparation.data[0].id)
        sale_response = self._authenticated_post(
            f"{self.cinema_details.cinemaUrl}api/sale/complete",
            payload=sale_body.json(by_alias=True),
        )
        sale_confirmation_response = parse_obj_as(serializers.SaleConfirmationResponse, sale_response)
        add_to_queue(
            bookings_constants.REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": sale_confirmation_response.data.code,
                "venue_id": booking.venueId,
                "timestamp": datetime.datetime.utcnow().timestamp(),
                "booking_type": bookings_constants.RedisExternalBookingType.CINEMA,
            },
        )

        tickets = []
        for ticket_response in sale_confirmation_response.data.tickets:
            # same barcode for each Ticket of the sale
            barcode = sale_confirmation_response.data.code
            seat_number = str(ticket_response.seat.id) if ticket_response.seat else None
            extra_data = {
                "barcode": barcode,
                "seat_number": seat_number,
                "ticketReference": ticket_response.ticketReference,
                "total_amount": sale_confirmation_response.data.amountTaxesIncluded,
            }
            # This will be useful for customer support
            logger.info("Booked Boost Ticket", extra=extra_data)
            ticket = external_bookings_models.Ticket(barcode=barcode, seat_number=seat_number)
            tickets.append(ticket)

        return tickets

    def get_showtimes(
        self,
        *,
        start_date: datetime.date = datetime.date.today(),
        interval_days: int = constants.BOOST_SHOWS_INTERVAL_DAYS,
        per_page: int = 30,  # `per_page` max value seems to be 200
        film: int | None = None,
    ) -> list:
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = (start_date + datetime.timedelta(days=interval_days)).strftime("%Y-%m-%d")
        url = f"{self.cinema_details.cinemaUrl}api/showtimes/between/{start_str}/{end_str}"
        params = {
            "paymentMethod": constants.BOOST_PASS_CULTURE_PAYMENT_METHOD,
            "hideFullReservation": constants.BOOST_HIDE_FULL_RESERVATION,
            "film": film,
            "per_page": per_page,
        }
        items = []
        current_page = next_page = 1

        while current_page <= next_page:
            params["page"] = current_page

            data = self._authenticated_get(url, params=params)

            collection = parse_obj_as(serializers.ShowTimeCollection, data)
            items.extend(collection.data)
            total_pages = collection.totalPages
            next_page = collection.nextPage
            current_page += 1
            if total_pages < current_page:
                break

        return items

    def get_showtime(self, showtime_id: int) -> serializers.ShowTime4:
        data = self._authenticated_get(f"{self.cinema_details.cinemaUrl}api/showtimes/{showtime_id}")
        showtime_details = parse_obj_as(serializers.ShowTimeDetails, data)
        return showtime_details.data

    def get_movie_poster(self, image_url: str) -> bytes:
        api_response = requests.get(image_url)

        if api_response.status_code != 200:
            logger.info("Could not fetch movie poster", extra={"provider": "boost", "url": image_url})
            return bytes()

        return api_response.content

    def get_cinemas_attributs(self) -> list[serializers.CinemaAttribut]:
        data = self._authenticated_get(f"{self.cinema_details.cinemaUrl}api/cinemas/attributs")
        attributs = parse_obj_as(serializers.CinemaAttributCollection, data)
        return attributs.data
