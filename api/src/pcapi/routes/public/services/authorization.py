import logging

from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


def check_is_allowed_to_perform_action(
    provider_id: int,
    venue_id: int,
    resource: providers_models.ApiResourceEnum,
    permission: providers_models.PermissionEnum,
) -> None:
    """
    Check with 2 steps:
        1. Check that there is an active `VenueProvider` that links the venue to the provider.
        If not, raise a `ResourceNotFoundError` (HTTP 404)

        2. Check that the `VenueProvider` has given permission on given resource.
        If not, raise a `ForbiddenError` (HTTP 403)
    """
    # Check if provider is actively linked to the venue
    venue_provider = _get_venue_provider_or_raise_404(provider_id=provider_id, venue_id=venue_id)

    # Check if provider has permission to perform this action
    venue_provider_permission = providers_repository.get_venue_provider_permission_or_none(
        venue_provider.id,
        resource=resource,
        permission=permission,
    )

    if not venue_provider_permission:
        if FeatureToggle.WIP_ENABLE_PUBLIC_API_PERMISSION_SYSTEM.is_active():
            raise api_errors.ForbiddenError(errors={"global": "Not enough permission"})
        logger.warning(
            "%s has made a call in relation to %s that "
            "would raise an error if the permission system was on. Missing permission: `%s` on `%s`",
            venue_provider.provider,
            venue_provider.venue,
            permission.value,
            resource.value,
        )


def _get_venue_provider_or_raise_404(provider_id: int, venue_id: int) -> providers_models.VenueProvider:
    venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
        venue_id=venue_id, provider_id=provider_id
    )

    if not venue_provider or not venue_provider.isActive:
        raise api_errors.ResourceNotFoundError(errors={"global": "Venue cannot be found"})

    return venue_provider
