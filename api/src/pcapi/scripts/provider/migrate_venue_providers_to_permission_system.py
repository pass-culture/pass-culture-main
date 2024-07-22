import click
from sqlalchemy.exc import NoResultFound

from pcapi.core.providers import models as providers_models
from pcapi.core.providers import repository as providers_repository
from pcapi.repository import transaction
from pcapi.scripts.utils import PromptColors
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


def _migrate_venue_provider(venue_provider: providers_models.VenueProvider) -> None:
    if len(venue_provider.permissions) > 0:
        print(
            f"{PromptColors.YELLOW}`VenueProvider` id={venue_provider.id} has already been migrated!{PromptColors.END_COLOR}"
        )
        return

    with transaction():
        providers_repository.add_all_permissions_for_venue_provider(venue_provider=venue_provider)

    print(
        f"{PromptColors.GREEN}`VenueProvider` id={venue_provider.id} has been successfully migrated to the permission system! {PromptColors.END_COLOR}"
    )
    return


@blueprint.cli.command("migrate_venue_providers_to_permission_system")
@click.option("--venue_provider_id", type=int, required=False)
@click.option("--all-venue-providers", type=bool, required=False)
def migrate_venue_providers_to_permission_system(
    venue_provider_id: int | None,
    all_venue_providers: bool | None,
) -> None:
    """
    Migrate existing `VenueProvider` to the new permission system, meaning it creates
    all the `VenueProviderPermission` necessary to give full access to the existing
    integration and prevent any regression.

    If a `VenueProvider` already has at least one `VenueProviderPermission` we consider
    that it has already been migrated.

    :venue_provider_id: To migrate a specific `VenueProvider` using its id
    :all: When set to `true`, migrate all the `VenueProviders` that do not have a `VenueProviderPermission`
    """
    if venue_provider_id is None and not all_venue_providers:
        print(
            f"{PromptColors.RED}You should pass a `venue_provider_id` or set `all_venue_providers` to `true`{PromptColors.END_COLOR}"
        )
        return

    if venue_provider_id is not None and all_venue_providers:
        print(
            f"{PromptColors.RED}You cannot give a `venue_provider_id` and set `all_venue_providers` to `true`. Choose one of the two option.{PromptColors.END_COLOR}"
        )
        return

    if venue_provider_id:
        try:
            venue_provider = providers_repository.get_venue_provider_by_id(venue_provider_id)
            _migrate_venue_provider(venue_provider)
        except NoResultFound:
            print(f"{PromptColors.RED}`VenueProvider` id={venue_provider_id} does not exist!{PromptColors.END_COLOR}")

        return

    venue_providers = providers_repository.get_all_venue_providers_with_no_permission()

    for venue_provider in venue_providers:
        _migrate_venue_provider(venue_provider)
