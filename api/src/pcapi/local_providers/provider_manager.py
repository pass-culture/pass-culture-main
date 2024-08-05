from csv import DictWriter
from datetime import datetime
import logging
from pathlib import Path
from typing import Callable
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
import pcapi.connectors.ems as ems_connectors
from pcapi.connectors.googledrive import get_backend
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers.models import Venue
from pcapi.core.providers import models as provider_models
from pcapi.core.providers import repository as providers_repository
from pcapi.core.providers.api import update_venue_synchronized_offers_active_status_job
from pcapi.core.providers.constants import CINEMA_PROVIDER_NAMES
from pcapi.infrastructure.repository.stock_provider import provider_api
import pcapi.local_providers
from pcapi.local_providers.cinema_providers.ems.ems_stocks import EMSStocks
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.scheduled_tasks.logger import CronStatus
from pcapi.scheduled_tasks.logger import build_cron_log_message
from pcapi.utils import requests


if TYPE_CHECKING:
    from pcapi.connectors.serialization.ems_serializers import Site
logger = logging.getLogger(__name__)


def synchronize_data_for_provider(provider_name: str, limit: int | None = None) -> None:
    provider_class = get_local_provider_class_by_name(provider_name)
    try:
        provider = provider_class()
        provider.updateObjects(limit)
        provider.postTreatment()
    except Exception:  # pylint: disable=broad-except
        logger.exception(build_cron_log_message(name=provider_name, status=CronStatus.FAILED))


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
        except provider_api.ProviderAPIException as exception:
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"ProviderAPIException with code {exception.status_code} while synchronizing venue_provider",
                extra=log_data | {"exc": exception},
            )
        except Exception as exception:  # pylint: disable=broad-except
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)


def get_local_provider_class_by_name(class_name: str) -> Callable:
    return getattr(pcapi.local_providers, class_name)


def synchronize_venue_provider(venue_provider: provider_models.VenueProvider, limit: int | None = None) -> None:
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
        except provider_api.ProviderAPIException as exception:
            logger.error(  # pylint: disable=logging-fstring-interpolation
                f"ProviderAPIException with code {exception.status_code} while synchronizing venue_provider",
                extra=log_data | {"exc": exception},
            )
            venues_provider_to_sync.discard(venue_provider.id)
        except Exception as exception:  # pylint: disable=broad-except
            logger.exception("Unexpected error while synchronizing venue provider", extra=log_data)
            venues_provider_to_sync.discard(venue_provider.id)

    with transaction():
        providers_repository.bump_ems_sync_version(new_version, venues_provider_to_sync)
        db.session.commit()


def synchronize_ems_venue_provider(venue_provider: provider_models.VenueProvider) -> None:
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


def collect_elligible_venues_and_activate_ems_sync() -> None:
    """
    Switch Allocine synchronization to EMS synchronization

    Also write into a file all cinemas available for synchronization
    that don't have one yet.
    """
    should_log_available_cinemas_for_sync = FeatureToggle.LOG_EMS_CINEMAS_AVAILABLE_FOR_SYNC.is_active()

    with transaction():
        connector = ems_connectors.EMSSitesConnector()

        venues_successfully_activated: set[str] = set()

        venue_providers_to_activate: list[dict] = []
        pivot_to_create: list[dict] = []
        venue_providers_to_deactivate: list[dict] = []
        allocine_pivot_to_delete: list[int] = []

        ems_provider_id = providers_repository.get_provider_by_local_class("EMSStocks").id
        available_sites_by_allocine_id: dict[str, Site] = {}
        available_sites_by_cinema_id: dict[str, Site] = {}

        for site in connector.get_available_sites():
            available_sites_by_allocine_id[site.allocine_id] = site
            available_sites_by_cinema_id[site.id] = site

        allocine_venue_provider_aliased = sa_orm.aliased(provider_models.AllocineVenueProvider, flat=True)

        venues_to_activate = (
            Venue.query.join(Venue.venueProviders)
            .join(
                allocine_venue_provider_aliased,
                sa.and_(
                    allocine_venue_provider_aliased.id == provider_models.VenueProvider.id,
                    allocine_venue_provider_aliased.internalId.in_(available_sites_by_allocine_id),
                ),
            )
            .outerjoin(Venue.allocinePivot)
            .options(sa_orm.joinedload(Venue.venueProviders.of_type(provider_models.AllocineVenueProvider)))
            .options(sa_orm.joinedload(Venue.allocinePivot))
            .all()
        )

        cinemas_aldready_activated = {
            cinema_id
            for cinema_id, in (
                provider_models.CinemaProviderPivot.query.join(
                    provider_models.EMSCinemaDetails,
                    provider_models.CinemaProviderPivot.id == provider_models.EMSCinemaDetails.cinemaProviderPivotId,
                )
                .with_entities(provider_models.CinemaProviderPivot.idAtProvider)
                .all()
            )
        }

        for venue_to_activate in venues_to_activate:
            allocine_venue_provider = venue_to_activate.venueProviders[0]
            available_venue = available_sites_by_allocine_id[allocine_venue_provider.internalId]
            venue_providers_to_deactivate.append(
                {
                    "id": allocine_venue_provider.id,
                    "venue_id": allocine_venue_provider.venueId,
                    "provider_id": allocine_venue_provider.providerId,
                    "is_active": False,
                }
            )
            logger.info(
                "Deactivating Allocine sync for a venue",
                extra={
                    "venue_id": venue_to_activate.id,
                    "venue_siret": venue_to_activate.siret,
                    "venue_name": venue_to_activate.name,
                    "venue_provider_id": allocine_venue_provider.id,
                },
            )
            history_api.add_action(
                action_type=history_models.ActionType.LINK_VENUE_PROVIDER_DELETED,
                author=None,
                venue=venue_to_activate,
                provider_id=allocine_venue_provider.providerId,
                provider_name="Allociné",
            )

            venue_providers_to_activate.append(
                {
                    "venueId": venue_to_activate.id,
                    "providerId": ems_provider_id,
                    "venueIdAtOfferProvider": available_venue.id,
                }
            )
            logger.info(
                "Creating EMS sync for a venue",
                extra={
                    "venue_id": venue_to_activate.id,
                    "venue_siret": venue_to_activate.siret,
                    "venue_name": venue_to_activate.name,
                },
            )

            pivot = {
                "venueId": venue_to_activate.id,
                "providerId": ems_provider_id,
                "idAtProvider": available_venue.id,
            }
            pivot_to_create.append(pivot)

            allocine_pivot_to_delete.extend([allocine_pivot.id for allocine_pivot in venue_to_activate.allocinePivot])

            venues_successfully_activated.add(allocine_venue_provider.internalId)

        # Removing no longer up to date allocine sync
        # As AllocineVenueProvider inherit from VenueProvider, we need to delete rows in both tables
        provider_models.AllocineVenueProvider.query.filter(
            provider_models.AllocineVenueProvider.id.in_(
                venue_provider["id"] for venue_provider in venue_providers_to_deactivate
            )
        ).delete()
        provider_models.VenueProvider.query.filter(
            provider_models.VenueProvider.id.in_(
                venue_provider["id"] for venue_provider in venue_providers_to_deactivate
            )
        ).delete()
        provider_models.AllocinePivot.query.filter(
            provider_models.AllocinePivot.id.in_(allocine_pivot_to_delete)
        ).delete()

        # Deactivate and deindex offers related to Allocine venue providers
        for venue_provider in venue_providers_to_deactivate:
            update_venue_synchronized_offers_active_status_job.delay(
                venue_provider["venue_id"], venue_provider["provider_id"], False
            )

        # Then creating EMS sync
        db.session.bulk_insert_mappings(provider_models.VenueProvider, venue_providers_to_activate)

        # And finally creating pivots and EMSCinemaDetails
        for mapping in pivot_to_create:
            pivot = provider_models.CinemaProviderPivot(**mapping)
            cinema_details = provider_models.EMSCinemaDetails(cinemaProviderPivot=pivot)
            repository.save(pivot, cinema_details, commit=False)

        if venues_left_to_be_activated := set(available_sites_by_allocine_id).difference(venues_successfully_activated):
            for allocine_id in venues_left_to_be_activated:
                venue = available_sites_by_allocine_id[allocine_id]
                logger.warning(
                    "Fail to find this venue available for EMS sync",
                    extra={
                        "venue_name": venue.name,
                        "venue_allocine_id": venue.allocine_id,
                        "venue_siret": venue.siret,
                    },
                )

        if should_log_available_cinemas_for_sync:
            if venues_left_to_be_activated := set(available_sites_by_cinema_id).difference(cinemas_aldready_activated):
                file_name = f"{datetime.today().date().isoformat()}.csv"
                path = Path(f"/tmp/{file_name}")
                with open(path, "w", encoding="utf-8") as f:
                    header = ["cinema", "siret", "ems_id", "allocine_id", "address", "zip_code", "city"]
                    writer = DictWriter(f, fieldnames=header)
                    writer.writeheader()

                    for cinema_id in venues_left_to_be_activated:
                        cinema = available_sites_by_cinema_id[cinema_id]
                        row = {
                            "cinema": cinema.name,
                            "siret": cinema.siret,
                            "ems_id": cinema.id,
                            "allocine_id": cinema.allocine_id,
                            "address": cinema.address,
                            "zip_code": cinema.zip_code,
                            "city": cinema.city,
                        }
                        writer.writerow(row)

                gdrive_backend = get_backend()
                file_id = gdrive_backend.create_file(settings.EMS_GOOGLE_DRIVE_FOLDER, file_name, path)
                logger.info("Successfully export cinemas available for sync under file %s", file_id)
