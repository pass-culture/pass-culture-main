import logging
from typing import Callable

from sqlalchemy import insert
import sqlalchemy.orm as sqla_orm
from urllib3 import exceptions as urllib3_exceptions

import pcapi.connectors.ems as ems_connectors
import pcapi.connectors.notion as notion_connector
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.constants import CINEMA_PROVIDER_NAMES
from pcapi.core.providers.models import CinemaProviderPivot
from pcapi.core.providers.models import EMSCinemaDetails
from pcapi.core.providers.models import VenueProvider
from pcapi.infrastructure.repository.stock_provider import provider_api
import pcapi.local_providers
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def synchronize_data_for_provider(provider_name: str, limit: int | None = None) -> None:
    provider_class = get_local_provider_class_by_name(provider_name)
    try:
        provider = provider_class()
        provider.updateObjects(limit)
        provider.postTreatment()
    except Exception:  # pylint: disable=broad-except
        logger.exception(build_cron_log_message(name=provider_name, status=CronStatus.FAILED))


def synchronize_venue_providers(venue_providers: list[VenueProvider], limit: int | None = None) -> None:
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
        except provider_api.ProviderAPIException as exception:
            notion_connector.add_venue_provider_error_to_notion_database(exception, venue_provider)
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"ProviderAPIException with code {exception.status_code} while synchronizing venue_provider",
                extra=log_data | {"exc": exception},
            )
        except Exception as exception:  # pylint: disable=broad-except
            notion_connector.add_venue_provider_error_to_notion_database(exception, venue_provider)
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)


def get_local_provider_class_by_name(class_name: str) -> Callable:
    return getattr(pcapi.local_providers, class_name)


def synchronize_venue_provider(venue_provider: VenueProvider, limit: int | None = None) -> None:
    if venue_provider.provider.implements_provider_api and not venue_provider.provider.isCinemaProvider:
        synchronize_provider_api.synchronize_venue_provider(venue_provider)

    else:
        assert (
            venue_provider.provider.localClass
            in [
                "AllocineStocks",
            ]
            + CINEMA_PROVIDER_NAMES
        ), f"Only {', '.join(CINEMA_PROVIDER_NAMES)} or AllocineStocks should reach this code"
        provider_class = get_local_provider_class_by_name(venue_provider.provider.localClass)

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
    venue_provider_by_site_id: dict[str, VenueProvider] = {}

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
        except provider_api.ProviderAPIException as exception:
            notion_connector.add_venue_provider_error_to_notion_database(exception, venue_provider)
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"ProviderAPIException with code {exception.status_code} while synchronizing venue_provider",
                extra=log_data | {"exc": exception},
            )
            venues_provider_to_sync.discard(venue_provider.id)
        except Exception as exception:  # pylint: disable=broad-except
            notion_connector.add_venue_provider_error_to_notion_database(exception, venue_provider)
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)
            venues_provider_to_sync.discard(venue_provider.id)

    with transaction():
        providers_repository.bump_ems_sync_version(new_version, venues_provider_to_sync)
        db.session.commit()


def synchronize_ems_venue_provider(venue_provider: VenueProvider) -> None:
    connector = ems_connectors.EMSScheduleConnector()
    ems_cinema_details = providers_repository.get_ems_cinema_details(venue_provider.venueIdAtOfferProvider)
    last_version = ems_cinema_details.lastVersion
    schedules = connector.get_schedules(last_version)
    new_version = schedules.version
    for site in schedules.sites:
        if site.id != venue_provider.venueIdAtOfferProvider:
            continue
        ems_stocks = EMSStocks(connector=connector, venue_provider=venue_provider, site=site)
        ems_stocks.synchronize()
        providers_repository.bump_ems_sync_version(new_version, [venue_provider.id])
        db.session.commit()


def activate_ems_sync() -> None:
    """What we are doing here:

    If a venue already exists:
        - If it’s already sync with EMS:
            - do nothing
        - If it’s sync we another provider:
            - remove the older sync and sync it with EMS
    If not:
        - Log the venue so we can fix it
    """
    with transaction():
        connector = ems_connectors.EMSSitesConnector()

        venues_siret_to_activate = set()
        venues_siret_activated = set()

        venue_providers_to_deactivate = []
        venue_providers_to_activate = []
        pivot_to_create = []
        pivot_to_update = []
        pivots_ids = []

        ems_provider_id = providers_repository.get_provider_by_local_class("EMSStocks").id
        venues_siret_already_activated = {
            venue.siret
            for venue in Venue.query.join(
                Venue.venueProviders.and_(VenueProvider.providerId == ems_provider_id),
            ).with_entities(Venue.siret)
        }
        available_venues_by_siret = {venue.siret: venue for venue in connector.get_available_venues()}

        for siret in available_venues_by_siret:
            if siret in venues_siret_already_activated:
                continue
            venues_siret_to_activate.add(siret)

        venues_to_activate = (
            Venue.query.filter(Venue.siret.in_(venues_siret_to_activate))
            .outerjoin(Venue.venueProviders)
            .outerjoin(
                Venue.cinemaProviderPivot,
            )
            .options(sqla_orm.joinedload(Venue.venueProviders))
            .options(sqla_orm.joinedload(Venue.cinemaProviderPivot))
            .all()
        )

        for venue_to_activate in venues_to_activate:
            logger.info(
                "Deactivating deprected sync for a venue",
                extra={
                    "venue_id": venue_to_activate.id,
                    "venue_siret": venue_to_activate.siret,
                    "venue_name": venue_to_activate.name,
                },
            )

            venue_providers_to_deactivate.extend(
                [venue_provider.id for venue_provider in venue_to_activate.venueProviders]
            )
            venue_providers_to_activate.append({"venueId": venue_to_activate.id, "providerId": ems_provider_id})

            logger.info(
                "Creating EMS sync for a venue",
                extra={
                    "venue_id": venue_to_activate.id,
                    "venue_siret": venue_to_activate.siret,
                    "venue_name": venue_to_activate.name,
                },
            )

            pivot_to_upsert = {
                "venueId": venue_to_activate.id,
                "providerId": ems_provider_id,
                "idAtProvider": available_venues_by_siret[venue_to_activate.siret].id,
            }
            if venue_to_activate.cinemaProviderPivot:
                pivot_to_upsert["id"] = venue_to_activate.cinemaProviderPivot[0].id
                pivot_to_update.append(pivot_to_upsert)
                pivots_ids.append({"cinemaProviderPivotId": pivot_to_upsert["id"]})
            else:
                pivot_to_create.append(pivot_to_upsert)

            venues_siret_activated.add(venue_to_activate.siret)

        # Remove no longer up to date sync and creating EMS ones
        VenueProvider.query.filter(VenueProvider.id.in_(venue_providers_to_deactivate)).delete()
        db.session.bulk_insert_mappings(VenueProvider, venue_providers_to_activate)

        # Updating or creating suitable pivots
        db.session.bulk_update_mappings(CinemaProviderPivot, pivot_to_update)
        if pivot_to_create:
            stmt = insert(CinemaProviderPivot).values(pivot_to_create).returning(CinemaProviderPivot.id)
            created_pivots_ids = db.session.execute(stmt)

            for _id in created_pivots_ids:
                pivots_ids.append({"cinemaProviderPivotId": _id[0]})

        # Finally creating EMS details
        db.session.bulk_insert_mappings(EMSCinemaDetails, pivots_ids)

        if venues_left_to_be_activated := venues_siret_to_activate.difference(venues_siret_activated):
            logger.warning("Fail to find venues available for EMS sync", extra={"sirets": venues_left_to_be_activated})
