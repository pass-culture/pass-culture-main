import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import override_features
from pcapi.models import api_errors
from pcapi.routes.public.services import authorization


@pytest.mark.usefixtures("db_session")
class CheckIsAllowedToPerformActionTest:

    @override_features(WIP_ENABLE_PUBLIC_API_PERMISSION_SYSTEM=True)
    def should_raise_resource_not_found_error_when_no_venue_provider(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()

        with pytest.raises(api_errors.ResourceNotFoundError) as exc_info:
            authorization.check_is_allowed_to_perform_action(
                provider_id=provider.id,
                venue_id=venue.id,
                resource=providers_models.ApiResourceEnum.bookings,
                permission=providers_models.PermissionEnum.READ,
            )

        assert exc_info.value.errors == {"global": "Venue cannot be found"}

    @override_features(WIP_ENABLE_PUBLIC_API_PERMISSION_SYSTEM=True)
    def should_raise_resource_not_found_error_when_venue_provider_is_not_active(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()
        providers_factories.VenueProviderFactory(venue=venue, provider=provider, isActive=False)

        with pytest.raises(api_errors.ResourceNotFoundError) as exc_info:
            authorization.check_is_allowed_to_perform_action(
                provider_id=provider.id,
                venue_id=venue.id,
                resource=providers_models.ApiResourceEnum.bookings,
                permission=providers_models.PermissionEnum.READ,
            )

        assert exc_info.value.errors == {"global": "Venue cannot be found"}

    @override_features(WIP_ENABLE_PUBLIC_API_PERMISSION_SYSTEM=True)
    def should_raise_forbidden_error_when_no_permission(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()
        providers_factories.VenueProviderFactory(
            venue=venue,
            provider=provider,
        )

        with pytest.raises(api_errors.ForbiddenError) as exc_info:
            authorization.check_is_allowed_to_perform_action(
                provider_id=provider.id,
                venue_id=venue.id,
                resource=providers_models.ApiResourceEnum.bookings,
                permission=providers_models.PermissionEnum.READ,
            )

        assert exc_info.value.errors == {"global": "Not enough permission"}

    @override_features(WIP_ENABLE_PUBLIC_API_PERMISSION_SYSTEM=True)
    def should_raise_forbidden_error_when_wrong_permissions(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue,
            provider=provider,
        )

        providers_factories.VenueProviderPermissionFactory(
            venueProvider=venue_provider,
            resource=providers_models.ApiResourceEnum.bookings,
            permission=providers_models.PermissionEnum.WRITE,
        )
        providers_factories.VenueProviderPermissionFactory(
            venueProvider=venue_provider,
            resource=providers_models.ApiResourceEnum.events,
            permission=providers_models.PermissionEnum.READ,
        )

        with pytest.raises(api_errors.ForbiddenError) as exc_info:
            authorization.check_is_allowed_to_perform_action(
                provider_id=provider.id,
                venue_id=venue.id,
                resource=providers_models.ApiResourceEnum.bookings,
                permission=providers_models.PermissionEnum.READ,
            )

        assert exc_info.value.errors == {"global": "Not enough permission"}

    @override_features(WIP_ENABLE_PUBLIC_API_PERMISSION_SYSTEM=True)
    def should_not_raise(self):
        venue = offerers_factories.VenueFactory()
        provider = providers_factories.ProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(
            venue=venue,
            provider=provider,
        )
        providers_factories.VenueProviderPermissionFactory(
            venueProvider=venue_provider,
            resource=providers_models.ApiResourceEnum.bookings,
            permission=providers_models.PermissionEnum.READ,
        )

        authorization.check_is_allowed_to_perform_action(
            provider_id=provider.id,
            venue_id=venue.id,
            resource=providers_models.ApiResourceEnum.bookings,
            permission=providers_models.PermissionEnum.READ,
        )
