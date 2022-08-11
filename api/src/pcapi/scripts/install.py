import importlib

import flask


def install_commands(app: flask.Flask) -> None:
    module_paths = (
        "pcapi.scheduled_tasks.search_commands",
        "pcapi.scheduled_tasks.commands",
        "pcapi.scheduled_tasks.titelive_commands",
        "pcapi.scripts.algolia_indexing.commands",
        "pcapi.scripts.clean_database",
        "pcapi.scripts.external_users.commands",
        "pcapi.scripts.full_index_offers",
        "pcapi.scripts.generate_invoices",
        "pcapi.scripts.install_data",
        "pcapi.scripts.booking.commands",
        "pcapi.scripts.offerer.commands",
        "pcapi.scripts.payment.add_custom_offer_reimbursement_rule",
        "pcapi.scripts.provider.check_provider_api",
        "pcapi.scripts.sandbox",
        "pcapi.scripts.update_providables",
        "pcapi.utils.human_ids",
        "pcapi.utils.secrets",
        "pcapi.workers.worker",
    )

    for path in module_paths:
        module = importlib.import_module(path)
        app.register_blueprint(getattr(module, "blueprint"), cli_group=None)
