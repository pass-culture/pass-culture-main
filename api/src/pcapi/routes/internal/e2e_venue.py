from pcapi.core.offerers import generator as offerers_generator
from pcapi.core.offerers import models as offerers_models
from pcapi.routes.backoffice.dev import forms as dev_forms
from pcapi.routes.internal.auth import api_key_required
from pcapi.routes.internal.blueprint import testing_blueprint
from pcapi.utils import transaction_manager


@testing_blueprint.route("/e2e/venue", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def generate_venue() -> tuple[dict, int]:
    form = dev_forms.VenueGeneratorForm()

    if not form.validate():
        transaction_manager.mark_transaction_as_invalid()
        return form.errors, 400

    venue = offerers_generator.create_venue(
        name=form.name.data,
        activity=offerers_models.Activity[form.activity.data],
        timezone=form.timezone.data,
    )

    offerer_address = venue.offererAddress

    return {
        "id": venue.id,
        "name": venue.name,
        "activity": venue.activity.name,
        "timezone": offerer_address.address.timezone,
    }, 200
