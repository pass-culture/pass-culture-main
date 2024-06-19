import importlib

import flask

from pcapi import settings


def install_commands(app: flask.Flask) -> None:
    module_paths: tuple[str, ...] = (
        "pcapi.core.bookings.commands",
        "pcapi.core.educational.commands",
        "pcapi.core.external.commands",
        "pcapi.core.external_bookings.commands",
        "pcapi.core.finance.commands",
        "pcapi.core.geography.commands",
        "pcapi.core.offerers.commands",
        "pcapi.core.providers.commands",
        "pcapi.core.search.commands.indexation",
        "pcapi.core.search.commands.settings",
        "pcapi.core.subscription.commands",
        "pcapi.core.users.commands",
        "pcapi.scheduled_tasks.commands",
        "pcapi.scheduled_tasks.offerer_stats_commands",
        "pcapi.scheduled_tasks.titelive_commands",
        "pcapi.scripts.backoffice_users.add_permissions_to_staging_specific_roles",
        "pcapi.scripts.beneficiary.import_test_users",
        "pcapi.scripts.booking.commands",
        "pcapi.scripts.check_pre_migrations",
        "pcapi.scripts.external_users.commands",
        "pcapi.scripts.full_index_offers",
        "pcapi.scripts.install_data",
        "pcapi.scripts.generate_expected_openapi_json",
        "pcapi.scripts.provider.check_provider_api",
        "pcapi.scripts.sandbox",
        "pcapi.scripts.ubble_archive_past_identifications",
        "pcapi.scripts.offer.fix_offer_data_titelive",
        "pcapi.scripts.offer.fix_product_gtl_id_titelive",
        "pcapi.utils.db",
        "pcapi.utils.human_ids",
        "pcapi.utils.secrets",
        "pcapi.workers.worker",
    )

    if settings.ENABLE_COMMAND_CLEAN_DATABASE:
        module_paths += ("pcapi.scripts.clean_database",)

    for path in module_paths:
        module = importlib.import_module(path)
        app.register_blueprint(getattr(module, "blueprint"), cli_group=None)
