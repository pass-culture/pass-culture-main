import logging

from urllib3 import exceptions as urllib3_exceptions

from pcapi.core.providers import models as provider_models
from pcapi.core.providers.etls.boost_etl import BoostExtractTransformLoadProcess
from pcapi.core.providers.etls.cgr_etl import CGRExtractTransformLoadProcess
from pcapi.core.providers.etls.cine_office_etl import CineOfficeExtractTransformLoadProcess
from pcapi.core.providers.etls.ems_etl import EMSExtractTransformLoadProcess
from pcapi.local_providers.allocine.allocine_stocks import AllocineStocks
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.utils import logging as logging_utils
from pcapi.utils import requests
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)

_NAME_TO_LOCAL_PROVIDER_CLASS: dict[str, type[LocalProvider]] = {
    "AllocineStocks": AllocineStocks,
}

_LOCAL_CLASS_NAME_TO_ETL_CLASS: dict[
    str,
    type[BoostExtractTransformLoadProcess]
    | type[CineOfficeExtractTransformLoadProcess]
    | type[CGRExtractTransformLoadProcess]
    | type[EMSExtractTransformLoadProcess],
] = {
    "BoostStocks": BoostExtractTransformLoadProcess,
    "CDSStocks": CineOfficeExtractTransformLoadProcess,  # INFO: CDS is the old name of CineOffice
    "CGRStocks": CGRExtractTransformLoadProcess,
    "EMSStocks": EMSExtractTransformLoadProcess,
}


def synchronize_venue_providers(venue_providers: list[provider_models.VenueProvider], limit: int | None = None) -> None:
    for venue_provider in venue_providers:
        log_data = {
            "venue_provider_id": venue_provider.id,
            "venue_id": venue_provider.venueId,
            "provider_id": venue_provider.providerId,
        }
        try:
            with transaction():
                synchronize_venue_provider(venue_provider, limit)
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as exception:
            logger.error("Connexion error while synchronizing venue_provider", extra=log_data | {"exc": exception})
        except Exception:
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)


def synchronize_venue_provider(venue_provider: provider_models.VenueProvider, limit: int | None = None) -> None:
    assert venue_provider.provider.localClass in _NAME_TO_LOCAL_PROVIDER_CLASS, (
        f"Only {', '.join(_NAME_TO_LOCAL_PROVIDER_CLASS.keys())} should reach this code"
    )
    # new integration
    if venue_provider.provider.localClass in _LOCAL_CLASS_NAME_TO_ETL_CLASS:
        execute_cinema_etl_process(venue_provider)
        return

    # old integration
    # TODO (tcoudray-pass, 04/02/26): Remove once we get rid of local provider classes
    provider_class = _NAME_TO_LOCAL_PROVIDER_CLASS[venue_provider.provider.localClass]
    logger.info(
        "Starting synchronization of venue_provider=%s with provider=%s",
        venue_provider.id,
        venue_provider.provider.localClass,
    )
    provider = provider_class(venue_provider)
    provider.updateObjects(limit)
    logger.info(
        "Ended synchronization of venue_provider=%s with provider=%s",
        venue_provider.id,
        venue_provider.provider.localClass,
    )


def execute_cinema_etl_process(venue_provider: provider_models.VenueProvider, *, debug: bool = False) -> None:
    logging_level = logging.DEBUG if debug else logging.INFO
    pcapi_logger = logging.getLogger("pcapi")

    with logging_utils.logging_at_level(pcapi_logger, logging_level):
        assert venue_provider.provider.localClass  # to make mypy happy
        ETLProcess = _LOCAL_CLASS_NAME_TO_ETL_CLASS[venue_provider.provider.localClass]
        ETLProcess(venue_provider).execute()
