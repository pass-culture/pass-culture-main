from pcapi.core.providers import factories as providers_factories
from pcapi.routes.backoffice.dev import forms as dev_forms
from pcapi.routes.internal.auth import api_key_required
from pcapi.routes.internal.blueprint import testing_blueprint
from pcapi.utils import transaction_manager


@testing_blueprint.route("/e2e/provider", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def generate_provider() -> tuple[dict, int]:
    form = dev_forms.ProviderGeneratorForm()

    if not form.validate():
        transaction_manager.mark_transaction_as_invalid()
        return form.errors, 400

    provider = providers_factories.PublicApiProviderFactory(
        name=form.name.data,
        bookingExternalUrl=form.bookingExternalUrl.data,
        cancelExternalUrl=form.cancelExternalUrl.data,
        notificationExternalUrl=form.notificationExternalUrl.data,
    )

    return {
        "id": provider.id,
        "name": provider.name,
        "bookingExternalUrl": provider.bookingExternalUrl,
        "cancelExternalUrl": provider.cancelExternalUrl,
        "notificationExternalUrl": provider.notificationExternalUrl,
    }, 200
