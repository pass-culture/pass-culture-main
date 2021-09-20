import importlib


def install_commands(app):
    module_paths = (
        "pcapi.scripts.algolia_indexing.commands",
        "pcapi.scripts.clean_database",
        "pcapi.scripts.install_data",
        "pcapi.scripts.offerer.commands",
        "pcapi.scripts.payment.banishment_command",
        "pcapi.scripts.payment.generate_payments",
        "pcapi.scripts.provider.check_provider_api",
        "pcapi.scripts.sandbox",
        "pcapi.scripts.update_providables",
    )

    for path in module_paths:
        module = importlib.import_module(path)
        app.register_blueprint(getattr(module, "blueprint"), cli_group=None)
