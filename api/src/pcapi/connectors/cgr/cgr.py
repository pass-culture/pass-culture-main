import json
import logging

from pydantic.v1 import parse_obj_as
from zeep import Client
from zeep.cache import InMemoryCache
from zeep.proxy import ServiceProxy

from pcapi import settings
from pcapi.connectors.serialization import cgr_serializers
from pcapi.core.external_bookings.cgr.exceptions import CGRAPIException
from pcapi.core.providers import models as providers_models
from pcapi.utils import requests
from pcapi.utils.crypto import decrypt


logger = logging.getLogger(__name__)

CGR_TIMEOUT = 10


def get_cgr_service_proxy(cinema_url: str) -> ServiceProxy:
    # https://docs.python-zeep.org/en/master/transport.html#caching
    cache = InMemoryCache()
    transport = requests.CustomZeepTransport(cache=cache, timeout=CGR_TIMEOUT, operation_timeout=CGR_TIMEOUT)
    client = Client(wsdl=f"{cinema_url}?wsdl", transport=transport)
    service = client.create_service(binding_name="{urn:GestionCinemaWS}GestionCinemaWSSOAPBinding", address=cinema_url)
    return service


def get_seances_pass_culture(
    cinema_details: providers_models.CGRCinemaDetails, allocine_film_id: int = 0
) -> cgr_serializers.GetSancesPassCultureResponse:
    """
    if allocine_film_id is 0 CGR API will return all future shows
    if allocine_film_id is not 0 CGR API will return only shows for concerned movie
    """
    user = settings.CGR_API_USER
    password = decrypt(cinema_details.password)
    cinema_url = cinema_details.cinemaUrl
    service = get_cgr_service_proxy(cinema_url)
    response = service.GetSeancesPassCulture(User=user, mdp=password, IDFilmAllocine=str(allocine_film_id))
    response = json.loads(response)
    _check_response_is_ok(response, "GetSeancesPassCulture")
    return parse_obj_as(cgr_serializers.GetSancesPassCultureResponse, response)


def reservation_pass_culture(
    cinema_details: providers_models.CGRCinemaDetails, body: cgr_serializers.ReservationPassCultureBody
) -> cgr_serializers.ReservationPassCultureResponse:
    user = settings.CGR_API_USER
    password = decrypt(cinema_details.password)
    cinema_url = cinema_details.cinemaUrl
    service = get_cgr_service_proxy(cinema_url)
    # We need to wait a little longer than the value we send them
    # Otherwise, for attempts very (very) close to the value of `CGR_TIMEOUT`
    # they might consider the booking as valid on their side
    # while on ours, the duration of the attempt + delay of the HTTP request + delay of HTTP response
    # could exceed the `CGR_TIMEOUT` value
    timeout = CGR_TIMEOUT - 2
    params = {
        "User": user,
        "mdp": password,
        "pIDSeances": body.pIDSeances,
        "pNumCinema": body.pNumCinema,
        "pPUTTC": body.pPUTTC,
        "pNBPlaces": body.pNBPlaces,
        "pNom": body.pNom,
        "pPrenom": body.pPrenom,
        "pEmail": body.pEmail,
        "pToken": body.pToken,
        "pDateLimiteAnnul": body.pDateLimiteAnnul,
        "pTimeoutReservation": timeout,
    }

    response = service.ReservationPassCulture(**params)
    response = json.loads(response)
    _check_response_is_ok(response, "ReservationPassCulture")
    return parse_obj_as(cgr_serializers.ReservationPassCultureResponse, response)


def annulation_pass_culture(cinema_details: providers_models.CGRCinemaDetails, qr_code: str) -> None:
    user = settings.CGR_API_USER
    password = decrypt(cinema_details.password)
    cinema_url = cinema_details.cinemaUrl
    service = get_cgr_service_proxy(cinema_url)
    response = service.AnnulationPassCulture(User=user, mdp=password, pQrCode=qr_code)
    response = json.loads(response)
    _check_response_is_ok(response, "AnnulationPassCulture")


def get_movie_poster_from_api(image_url: str) -> bytes:
    api_response = requests.get(image_url)

    if api_response.status_code != 200:
        raise CGRAPIException(
            f"Error getting CGR API movie poster {image_url}" f" with code {api_response.status_code}"
        )

    return api_response.content


def _check_response_is_ok(response: dict, resource: str) -> None:
    if response["CodeErreur"] != 0:
        error_message = response["IntituleErreur"]
        raise CGRAPIException(f"Error on CGR API on {resource} : {error_message}")
