import json

from pydantic import parse_obj_as
from zeep import Client
from zeep import Transport
from zeep.proxy import ServiceProxy

from pcapi import settings
from pcapi.connectors.cgr.exceptions import CGRAPIException
from pcapi.connectors.serialization import cgr_serializers
from pcapi.core.providers import models as providers_models


def get_cgr_service_proxy(cinema_url: str) -> ServiceProxy:
    transport = Transport(timeout=10, operation_timeout=10)
    client = Client(wsdl=f"{cinema_url}?wsdl", transport=transport)
    service = client.create_service(binding_name="{urn:GestionCinemaWS}GestionCinemaWSSOAPBinding", address=cinema_url)
    return service


def get_seances_pass_culture(
    cinema_details: providers_models.CGRCinemaDetails,
) -> cgr_serializers.GetSancesPassCultureResponse:
    user = settings.CGR_API_USER
    password = settings.CGR_API_PASSWORD
    # FIXME(fseguin, 2023-01-26): remove default from settings when FA page and pc pro pages are built
    cinema_url = cinema_details.cinemaUrl or settings.CGR_API_URL
    service = get_cgr_service_proxy(cinema_url)
    response = service.GetSeancesPassCulture(User=user, mdp=password)
    response = json.loads(response)
    _check_response_is_ok(response, "GetSeancesPassCulture")
    return parse_obj_as(cgr_serializers.GetSancesPassCultureResponse, response)


def _check_response_is_ok(response: dict, resource: str) -> None:
    if response["CodeErreur"] != 0:
        error_message = response["IntituleErreur"]
        raise CGRAPIException(f"Error on CGR API on {resource} : {error_message}")
