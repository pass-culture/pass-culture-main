import logging

from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle
from pcapi.validation.routes.users_authentifications import current_api_key


logger = logging.getLogger(__name__)


def check_is_allowed_to_perform_action(
    venue_provider: providers_models.VenueProvider,
    *,
    resource: providers_models.ApiResourceEnum,
    permission: providers_models.PermissionEnum,
) -> None:
    """
    Check the permissions defined in `venue_provider` allow provider
    to perform given action on given resource.

    Raise `ForbiddenError` if permissions are insufficient.
    """

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


def get_venue_provider_or_raise_404(venue_id: int) -> providers_models.VenueProvider:
    """
    Return active `VenueProvider` linking the venue to the current provider

    Raise `ResourceNotFoundError` if no active `VenueProvider` is found because it means
    provider should have access to the venue.
    """
    venue_provider = providers_repository.get_venue_provider_by_venue_and_provider_ids(
        venue_id=venue_id, provider_id=current_api_key.providerId
    )

    if not venue_provider or not venue_provider.isActive:
        raise api_errors.ResourceNotFoundError(errors={"global": "Venue cannot be found"})

    return venue_provider
