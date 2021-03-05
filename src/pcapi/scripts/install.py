def install_scripts():
    # pylint: disable=unused-import
    import pcapi.scripts.algolia_indexing.commands
    import pcapi.scripts.clean_database
    import pcapi.scripts.install_data
    import pcapi.scripts.iris.commands
    import pcapi.scripts.payment.banishment_command
    import pcapi.scripts.payment.generate_payments
    import pcapi.scripts.provider.check_provider_api
    import pcapi.scripts.sandbox
    import pcapi.scripts.storage
    import pcapi.scripts.update_providables
