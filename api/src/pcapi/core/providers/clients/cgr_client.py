import json
import logging

import pydantic
import regex
from zeep import Client
from zeep.cache import InMemoryCache
from zeep.proxy import ServiceProxy

import pcapi.core.bookings.models as bookings_models
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.core.bookings.constants import REDIS_EXTERNAL_BOOKINGS_NAME
from pcapi.core.bookings.constants import RedisExternalBookingType
from pcapi.core.external_bookings.exceptions import ExternalBookingException
from pcapi.core.external_bookings.exceptions import ExternalBookingNotEnoughSeatsError
from pcapi.core.external_bookings.exceptions import ExternalBookingShowDoesNotExistError
from pcapi.core.providers.clients import cinema_client
from pcapi.core.providers.models import CGRCinemaDetails
from pcapi.core.providers.repository import get_cgr_cinema_details
from pcapi.utils import date as date_utils
from pcapi.utils import requests
from pcapi.utils.crypto import decrypt
from pcapi.utils.queue import add_to_queue

from . import cgr_serializers


logger = logging.getLogger(__name__)

CGR_TIMEOUT = 10
CGR_SHOWTIMES_STOCKS_CACHE_KEY = "api:cinema_provider:cgr:stocks:%s:%s"
CGR_SHOWTIMES_STOCKS_CACHE_TIMEOUT = 60
_CGR_NOT_ENOUGH_SEAT_ERROR_PATTERN = r"Impossible de délivrer \d places , il n'en reste que : (\d)"
_CGR_SHOW_DOES_NOT_EXISTS_PATTERN = r"PASS CULTURE IMPOSSIBLE erreur création résa \(site\) : IdSeance\(\d+\) inconnu"


class CGRAPIException(ExternalBookingException):
    pass


def _log_external_call(
    client: cinema_client.CinemaAPIClient,
    method: str,
    response: pydantic.BaseModel | dict,
) -> None:
    if isinstance(response, pydantic.BaseModel):
        response = response.model_dump(exclude_unset=True)

    logger.debug(
        "[CINEMA] Call to external API",
        extra={
            "api_client": client.__class__.__name__,
            "cinema_id": client.cinema_id,
            "method": method,
            "response": response,
        },
    )


def _check_response_is_ok(response: dict, resource: str) -> None:
    if response["CodeErreur"] != 0:
        error_message = response["IntituleErreur"]
        logger.warning(
            "[CGR] Error calling API",
            extra={"error_code": response["CodeErreur"], "error_message": error_message},
        )

        if regex.match(_CGR_NOT_ENOUGH_SEAT_ERROR_PATTERN, error_message):
            remaining_seats = int(regex.findall(_CGR_NOT_ENOUGH_SEAT_ERROR_PATTERN, error_message)[0])
            raise ExternalBookingNotEnoughSeatsError(remaining_seats)

        if "Séance inconnue" in error_message or regex.match(_CGR_SHOW_DOES_NOT_EXISTS_PATTERN, error_message):
            raise ExternalBookingShowDoesNotExistError()

        raise CGRAPIException(f"Error on CGR API on {resource} : {error_message}")


def _get_cgr_service_proxy(cinema_url: str, request_timeout: int | None = None) -> ServiceProxy:
    # https://docs.python-zeep.org/en/master/transport.html#caching
    timeout = request_timeout or CGR_TIMEOUT
    cache = InMemoryCache()
    transport = requests.CustomZeepTransport(cache=cache, timeout=timeout, operation_timeout=timeout)
    client = Client(wsdl=f"{cinema_url}?wsdl", transport=transport)
    service = client.create_service(binding_name="{urn:GestionCinemaWS}GestionCinemaWSSOAPBinding", address=cinema_url)
    return service


class CGRAPIClient(cinema_client.CinemaAPIClient):
    def __init__(
        self,
        cinema_id: str,
        request_timeout: None | int = None,
        cinema_details: None | CGRCinemaDetails = None,
    ):
        super().__init__(cinema_id=cinema_id, request_timeout=request_timeout)
        self.cinema_details = cinema_details or get_cgr_cinema_details(cinema_id)
        self.service_proxy = _get_cgr_service_proxy(self.cinema_details.cinemaUrl, request_timeout=self.request_timeout)
        self.user = settings.CGR_API_USER

    def _get_seances_pass_culture(
        self, allocine_film_id: str | None = None
    ) -> cgr_serializers.GetSancesPassCultureResponse:
        response = self.service_proxy.GetSeancesPassCulture(
            User=self.user,
            mdp=decrypt(self.cinema_details.password),
            IDFilmAllocine=allocine_film_id or "0",
        )
        data = json.loads(response)
        _check_response_is_ok(data, "GetSeancesPassCulture")
        _log_external_call(self, "GetSeancesPassCulture", data)
        data = cgr_serializers.GetSancesPassCultureResponse.model_validate(data)
        return data

    def get_num_cine(self) -> int:
        data = self._get_seances_pass_culture()
        return data.ObjetRetour.NumCine

    def get_films(self) -> list[cgr_serializers.Film]:
        logger.info("Fetching CGR movies", extra={"cinema_id": self.cinema_id})
        data = self._get_seances_pass_culture()
        return data.ObjetRetour.Films

    @cinema_client.cache_external_call(
        key_template=CGR_SHOWTIMES_STOCKS_CACHE_KEY, expire=CGR_SHOWTIMES_STOCKS_CACHE_TIMEOUT
    )
    def get_film_showtimes_stocks(self, film_id: str) -> str:
        logger.info("Fetching CGR showtimes", extra={"cinema_id": self.cinema_id})
        data = self._get_seances_pass_culture(film_id)
        films = data.ObjetRetour.Films

        if films:
            film = films[0]
            return json.dumps({show.IDSeance: show.NbPlacesRestantes for show in film.Seances})

        # Showtimes stocks are sold out, Stock.quantity will be updated to dnBookedQuantity
        # in `update_stock_quantity_to_match_cinema_venue_provider_remaining_places`
        return json.dumps({})

    def book_ticket(
        self, show_id: int, booking: bookings_models.Booking, beneficiary: users_models.User
    ) -> list[cinema_client.Ticket]:
        logger.info(
            "Booking CGR external ticket",
            extra={"show_id": show_id, "cinema_id": self.cinema_id, "booking_token": booking.token},
        )
        assert booking.cancellationLimitDate  # for typing; a movie screening is always an event
        timeout = self.request_timeout or CGR_TIMEOUT
        response = self.service_proxy.ReservationPassCulture(
            User=self.user,
            mdp=decrypt(self.cinema_details.password),
            pIDSeances=show_id,
            pNumCinema=self.cinema_details.numCinema,
            pPUTTC=booking.amount,
            pNBPlaces=booking.quantity,
            pNom=beneficiary.lastName if beneficiary.lastName else "",
            pPrenom=beneficiary.firstName if beneficiary.firstName else "",
            pEmail=beneficiary.email,
            pToken=booking.token,
            pDateLimiteAnnul=booking.cancellationLimitDate.isoformat(),
            pTimeoutReservation=timeout - 2,  # to be conservative on network latency
        )
        response = json.loads(response)
        _check_response_is_ok(response, "ReservationPassCulture")
        response = cgr_serializers.ReservationPassCultureResponse.model_validate(response)

        logger.info(
            "Booked CGR Ticket",
            extra={
                "barcode": response.QrCode,
                "seat_number": response.Placement,
                "booking_id": booking.id,
                "booking_token": booking.token,
            },
        )
        add_to_queue(
            REDIS_EXTERNAL_BOOKINGS_NAME,
            {
                "barcode": response.QrCode,
                "venue_id": booking.venueId,
                "timestamp": date_utils.get_naive_utc_now().timestamp(),
                "booking_type": RedisExternalBookingType.CINEMA,
            },
        )
        if booking.quantity == 2:
            tickets = [
                cinema_client.Ticket(
                    barcode=response.QrCode,
                    seat_number=response.Placement.split(",")[0] if "," in response.Placement else None,
                ),
                cinema_client.Ticket(
                    barcode=response.QrCode,
                    seat_number=response.Placement.split(",")[1] if "," in response.Placement else None,
                ),
            ]
        else:
            tickets = [
                cinema_client.Ticket(
                    barcode=response.QrCode, seat_number=response.Placement if response.Placement else None
                )
            ]
        return tickets

    def _annulation_pass_culture(self, barcode: str) -> None:
        response = self.service_proxy.AnnulationPassCulture(
            User=self.user,
            mdp=decrypt(self.cinema_details.password),
            pQrCode=barcode,
        )
        response = json.loads(response)

        if response["CodeErreur"] == 1:  # booking is already cancelled on their side
            return

        _check_response_is_ok(response, "AnnulationPassCulture")

    def cancel_booking(self, barcodes: list[str]) -> None:
        barcodes_set = set(barcodes)
        for barcode in barcodes_set:
            logger.info("Cancelling CGR external booking", extra={"barcode": barcode, "cinema_id": self.cinema_id})
            self._annulation_pass_culture(barcode)
            logger.info("CGR Booking Cancelled", extra={"barcode": barcode})

    def get_movie_poster_from_api(self, image_url: str) -> bytes:
        api_response = requests.get(image_url)

        if api_response.status_code != 200:
            raise CGRAPIException(
                f"Error getting CGR API movie poster {image_url} with code {api_response.status_code}"
            )

        return api_response.content
