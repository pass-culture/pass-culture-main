from pcapi.core.offers import generator as offers_generator
from pcapi.core.offers import models as offers_models
from pcapi.models.utils import get_or_404
from pcapi.routes.apis import private_api
from pcapi.routes.backoffice.dev import forms as dev_forms
from pcapi.routes.internal.auth import api_key_required
from pcapi.utils import transaction_manager


@private_api.route("/e2e/offer", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def generate_offer() -> tuple[dict, int]:
    form = dev_forms.OfferGeneratorForm()

    if not form.validate():
        transaction_manager.mark_transaction_as_invalid()
        return form.errors, 400

    offer = offers_generator.create_offer(
        offer_name=form.name.data,
        price=form.price.data,
        subcategory_id=form.subcategory_id.data,
        is_duo=form.is_duo.data,
    )

    if offer is None:
        return {"subcategoryId": ["Invalid subcategoryId"]}, 400

    return {
        "id": offer.id,
        "name": offer.name,
        "subcategoryId": offer.subcategoryId,
        "venueId": offer.venueId,
        "isDuo": offer.isDuo,
    }, 200


@private_api.route("/e2e/offer/<int:offer_id>/deactivate", methods=["POST"])
@transaction_manager.atomic()
@api_key_required
def deactivate_offer(offer_id: int) -> tuple[dict, int]:
    offer = get_or_404(offers_models.Offer, offer_id)
    offers_generator.deactivate_offer(offer)
    return {}, 200
