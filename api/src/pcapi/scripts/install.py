import importlib

import flask


def install_commands(app: flask.Flask) -> None:
    module_paths = (
        "pcapi.core.bookings.commands",
        "pcapi.core.educational.commands",
        "pcapi.core.external.commands",
        "pcapi.core.finance.commands",
        "pcapi.core.providers.commands",
        "pcapi.core.search.commands.indexation",
        "pcapi.core.search.commands.settings",
        "pcapi.core.subscription.commands",
        "pcapi.scheduled_tasks.commands",
        "pcapi.scheduled_tasks.titelive_commands",
        "pcapi.scripts.beneficiary.import_test_users",
        "pcapi.scripts.booking.commands",
        "pcapi.scripts.clean_database",
        "pcapi.scripts.external_users.commands",
        "pcapi.scripts.full_index_offers",
        "pcapi.scripts.offer.fill_product_and_offer_ean",
        "pcapi.scripts.full_index_collective_offers",
        "pcapi.scripts.install_data",
        "pcapi.scripts.offerer.commands",
        "pcapi.scripts.provider.check_provider_api",
        "pcapi.scripts.sandbox",
        "pcapi.scripts.ubble_archive_past_identifications",
        "pcapi.utils.db",
        "pcapi.utils.human_ids",
        "pcapi.utils.secrets",
        "pcapi.workers.worker",
    )

    for path in module_paths:
        module = importlib.import_module(path)
        app.register_blueprint(getattr(module, "blueprint"), cli_group=None)
