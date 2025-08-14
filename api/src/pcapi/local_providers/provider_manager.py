import logging
from typing import Type

from urllib3 import exceptions as urllib3_exceptions

import pcapi.connectors.ems as ems_connectors
from pcapi.core.providers import models as provider_models
from pcapi.core.providers import repository as providers_repository
from pcapi.local_providers.allocine.allocine_stocks import AllocineStocks
from pcapi.local_providers.cinema_providers.boost.boost_stocks import BoostStocks
from pcapi.local_providers.cinema_providers.cds.cds_stocks import CDSStocks
from pcapi.local_providers.cinema_providers.cgr.cgr_stocks import CGRStocks
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.models import db
from pcapi.utils import cron
from pcapi.utils import requests
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)

_NAME_TO_LOCAL_PROVIDER_CLASS: dict[str, Type[LocalProvider]] = {
    "AllocineStocks": AllocineStocks,
    "BoostStocks": BoostStocks,
    "CDSStocks": CDSStocks,
    "CGRStocks": CGRStocks,
}


def synchronize_data_for_provider(provider_name: str, limit: int | None = None) -> None:
    provider_class = _NAME_TO_LOCAL_PROVIDER_CLASS[provider_name]
    try:
        provider = provider_class()
        provider.updateObjects(limit)
        provider.postTreatment()
    except Exception:
        logger.exception(cron.build_cron_log_message(name=provider_name, status=cron.CronStatus.FAILED))


def synchronize_venue_providers(venue_providers: list[provider_models.VenueProvider], limit: int | None = None) -> None:
    for venue_provider in venue_providers:
        log_data = {
            "venue_provider": venue_provider.id,
            "venue": venue_provider.venueId,
            "provider": venue_provider.providerId,
        }
        try:
            with transaction():
                synchronize_venue_provider(venue_provider, limit)
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as exception:
            logger.error("Connexion error while synchronizing venue_provider", extra=log_data | {"exc": exception})
        except Exception:
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)


def synchronize_venue_provider(venue_provider: provider_models.VenueProvider, limit: int | None = None) -> None:
    assert venue_provider.provider.localClass in _NAME_TO_LOCAL_PROVIDER_CLASS.keys(), (
        f"Only {', '.join(_NAME_TO_LOCAL_PROVIDER_CLASS.keys())} should reach this code"
    )
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


def synchronize_ems_venue_providers(from_last_version: bool = False) -> None:
    connector = ems_connectors.EMSScheduleConnector()
    last_version = providers_repository.get_ems_oldest_sync_version() if from_last_version else 0
    ems_provider_id = providers_repository.get_provider_by_local_class("EMSStocks").id
    venues_provider_to_sync: set[int] = set()
    venue_provider_by_site_id: dict[str, provider_models.VenueProvider] = {}

    logger.info("Starting EMS synchronization", extra={"version": last_version})

    cinemas_programs = connector.get_schedules(version=last_version)
    new_version = cinemas_programs.version
    active_venues_provider = providers_repository.get_active_venue_providers_by_provider(ems_provider_id)

    for active_venue_provider in active_venues_provider:
        venue_provider_by_site_id[active_venue_provider.venueIdAtOfferProvider] = active_venue_provider
        venues_provider_to_sync.add(active_venue_provider.id)

    for site in cinemas_programs.sites:
        venue_provider = venue_provider_by_site_id.get(site.id)
        if not venue_provider:
            logger.info("Venue provider for EMS site id %s not found", site.id)
            continue
        log_data = {
            "venue_provider": venue_provider.id,
            "venue": venue_provider.venueId,
            "provider": venue_provider.providerId,
        }
        try:
            with transaction():
                ems_stocks = EMSStocks(connector=connector, venue_provider=venue_provider, site=site)
                ems_stocks.synchronize()
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as exception:
            logger.error("Connexion error while synchronizing venue_provider", extra=log_data | {"exc": exception})
            venues_provider_to_sync.discard(venue_provider.id)
        except Exception:
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)
            venues_provider_to_sync.discard(venue_provider.id)

    with transaction():
        providers_repository.bump_ems_sync_version(new_version, venues_provider_to_sync)
        db.session.commit()


def synchronize_ems_venue_provider(
    venue_provider: provider_models.VenueProvider,
    target_version: int | None = None,
) -> None:
    connector = ems_connectors.EMSScheduleConnector()
    ems_cinema_details = providers_repository.get_ems_cinema_details(venue_provider.venueIdAtOfferProvider)
    target_version = target_version or ems_cinema_details.lastVersion
    schedules = connector.get_schedules(target_version)
    new_version = schedules.version
    for site in schedules.sites:
        if site.id != venue_provider.venueIdAtOfferProvider:
            continue
        ems_stocks = EMSStocks(connector=connector, venue_provider=venue_provider, site=site)
        ems_stocks.synchronize()
        providers_repository.bump_ems_sync_version(new_version, [venue_provider.id])
        db.session.commit()
