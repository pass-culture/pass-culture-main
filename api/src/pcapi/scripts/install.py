import importlib

import flask


def install_commands(app: flask.Flask) -> None:
    module_paths = (
        "pcapi.scheduled_tasks.algolia_clock",
        "pcapi.scheduled_tasks.clock",
        "pcapi.scheduled_tasks.titelive_clock",
        "pcapi.scripts.algolia_indexing.commands",
        "pcapi.scripts.clean_database",
        "pcapi.scripts.external_users.commands",
        "pcapi.scripts.force_19yo_dms_import",
        "pcapi.scripts.full_extract_offers",
        "pcapi.scripts.full_index_offers",
        "pcapi.scripts.generate_invoices",
        "pcapi.scripts.install_data",
        "pcapi.scripts.offerer.commands",
        "pcapi.scripts.payment.add_custom_offer_reimbursement_rule",
        "pcapi.scripts.payment.banishment_command",
        "pcapi.scripts.payment.generate_payments",
        "pcapi.scripts.provider.check_provider_api",
        "pcapi.scripts.sandbox",
        "pcapi.scripts.update_providables",
        "pcapi.utils.human_ids",
        "pcapi.workers.worker",
    )

    for path in module_paths:
        module = importlib.import_module(path)
        app.register_blueprint(getattr(module, "blueprint"), cli_group=None)
