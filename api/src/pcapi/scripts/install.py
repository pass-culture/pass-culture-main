import importlib

import flask


def install_commands(app: flask.Flask) -> None:
    module_paths = (
        "pcapi.core.educational.commands",
        "pcapi.core.finance.commands",
        "pcapi.core.providers.commands",
        "pcapi.scheduled_tasks.search_commands",
        "pcapi.scheduled_tasks.commands",
        "pcapi.scheduled_tasks.titelive_commands",
        "pcapi.scripts.algolia_indexing.commands",
        "pcapi.scripts.beneficiary.import_test_users",
        "pcapi.scripts.clean_database",
        "pcapi.scripts.external_users.commands",
        "pcapi.scripts.full_index_offers",
        "pcapi.scripts.install_data",
        "pcapi.scripts.booking.commands",
        "pcapi.scripts.offerer.commands",
        "pcapi.scripts.provider.check_provider_api",
        "pcapi.scripts.sandbox",
        "pcapi.scripts.ubble_archive_past_identifications",
        "pcapi.scripts.backoffice_users.create_backoffice_users",
        "pcapi.utils.human_ids",
        "pcapi.utils.secrets",
        "pcapi.workers.worker",
    )

    for path in module_paths:
        module = importlib.import_module(path)
        app.register_blueprint(getattr(module, "blueprint"), cli_group=None)
