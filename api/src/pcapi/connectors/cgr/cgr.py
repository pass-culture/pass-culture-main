import json
import logging

from zeep import Client
from zeep.cache import InMemoryCache
from zeep.proxy import ServiceProxy

from pcapi import settings
from pcapi.core.external_bookings.cgr.exceptions import CGRAPIException
from pcapi.core.providers import models as providers_models
from pcapi.utils import requests
from pcapi.utils.crypto import decrypt


logger = logging.getLogger(__name__)

CGR_TIMEOUT = 10


def get_cgr_service_proxy(cinema_url: str, request_timeout: int | None = None) -> ServiceProxy:
    # https://docs.python-zeep.org/en/master/transport.html#caching
    timeout = request_timeout or CGR_TIMEOUT
    cache = InMemoryCache()
    transport = requests.CustomZeepTransport(cache=cache, timeout=timeout, operation_timeout=timeout)
    client = Client(wsdl=f"{cinema_url}?wsdl", transport=transport)
    service = client.create_service(binding_name="{urn:GestionCinemaWS}GestionCinemaWSSOAPBinding", address=cinema_url)
    return service


def annulation_pass_culture(
    cinema_details: providers_models.CGRCinemaDetails,
    qr_code: str,
    request_timeout: int | None = None,
) -> None:
    user = settings.CGR_API_USER
    password = decrypt(cinema_details.password)
    cinema_url = cinema_details.cinemaUrl
    service = get_cgr_service_proxy(cinema_url, request_timeout=request_timeout)
    response = service.AnnulationPassCulture(User=user, mdp=password, pQrCode=qr_code)
    response = json.loads(response)

    if response["CodeErreur"] == 1:  # booking is already cancelled on their side
        return

    _check_response_is_ok(response, "AnnulationPassCulture")


def get_movie_poster_from_api(image_url: str) -> bytes:
    api_response = requests.get(image_url)

    if api_response.status_code != 200:
        raise CGRAPIException(f"Error getting CGR API movie poster {image_url} with code {api_response.status_code}")

    return api_response.content


def _check_response_is_ok(response: dict, resource: str) -> None:
    if response["CodeErreur"] != 0:
        error_message = response["IntituleErreur"]
        raise CGRAPIException(f"Error on CGR API on {resource} : {error_message}")
