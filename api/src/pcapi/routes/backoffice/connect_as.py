import random

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.educational import models as educational_model
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import utils
from pcapi.utils import urls


class ConnectAsForm(FlaskForm):
    object_id = wtforms.HiddenField()
    object_type = wtforms.HiddenField()
    redirect = wtforms.HiddenField()


def generate_connect_as_link(
    offer: educational_model.CollectiveOffer | educational_model.CollectiveOfferTemplate | offers_models.Offer,
) -> dict | None:
    connect_as = None
    if utils.has_current_user_permission(perm_models.Permissions.CONNECT_AS_PRO):
        random_int = random.randint(10000, 99999)
        connect_as_form = ConnectAsForm(
            object_type=filters.get_offer_type(offer),
            object_id=offer.id,
            redirect=urls.build_pc_pro_offer_path(offer),
        )
        connect_as = {
            "form": connect_as_form,
            "form_name": f"connect-as-form-offer-{offer.id}-{random_int}",
            "href": urls.build_pc_pro_offer_link(offer),
        }

    return connect_as
