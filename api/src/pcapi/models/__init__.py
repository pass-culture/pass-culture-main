from pcapi.models.db import db


def install_models():
    # pylint: disable=unused-import
    import pcapi.core.bookings.models
    import pcapi.core.educational.models
    import pcapi.core.finance.models
    import pcapi.core.fraud.models
    import pcapi.core.mails.models
    import pcapi.core.offerers.models
    import pcapi.core.offers.models
    import pcapi.core.payments.models
    import pcapi.core.providers.models
    import pcapi.core.subscription.models
    import pcapi.core.users.models
    import pcapi.models.allocine_pivot
    import pcapi.models.bank_information
    import pcapi.models.beneficiary_import
    import pcapi.models.beneficiary_import_status
    import pcapi.models.criterion
    import pcapi.models.feature
    import pcapi.models.local_provider_event
    import pcapi.models.offer_criterion
    import pcapi.models.payment
    import pcapi.models.payment_message
    import pcapi.models.payment_status
    import pcapi.models.product
    import pcapi.models.user_offerer
    import pcapi.models.user_session
