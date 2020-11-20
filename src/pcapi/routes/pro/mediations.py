from typing import List
from typing import Optional

from flask import request
from flask_login import current_user
from flask_login import login_required

import pcapi.core.offers.api as offers_api
from pcapi.core.offers.models import Mediation
from pcapi.flask_app import private_api
from pcapi.models.user_offerer import RightsType
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.routes.serialization.mediations_serialize import CreateMediationBodyModel
from pcapi.routes.serialization.mediations_serialize import MediationResponseIdModel
from pcapi.routes.serialization.mediations_serialize import UpdateMediationBodyModel
from pcapi.routes.serialization.mediations_serialize import UpdateMediationResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.rest import ensure_current_user_has_rights


@private_api.route("/mediations", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=MediationResponseIdModel)
def create_mediation(form: CreateMediationBodyModel) -> MediationResponseIdModel:
    ensure_current_user_has_rights(RightsType.editor, form.offerer_id)

    offer = get_offer_by_id(form.offer_id)
    image_as_bytes = form.get_image_as_bytes(request)

    mediation = offers_api.create_mediation(
        user=current_user,
        offer=offer,
        credit=form.credit,
        image_as_bytes=image_as_bytes,
        crop_params=form.crop_params,
    )

    return MediationResponseIdModel.from_orm(mediation)


@private_api.route("/mediations/<mediation_id>", methods=["PATCH"])
@login_required
@spectree_serialize(on_success_status=200, response_model=UpdateMediationResponseModel)
def update_mediation(mediation_id: str, body: UpdateMediationBodyModel) -> UpdateMediationResponseModel:

    mediation = Mediation.query.filter_by(id=dehumanize(mediation_id)).first_or_404()

    ensure_current_user_has_rights(RightsType.editor, mediation.offer.venue.managingOffererId)

    mediation = offers_api.update_mediation(mediation=mediation, is_active=body.isActive)

    return UpdateMediationResponseModel.from_orm(mediation)


def _get_crop(form: CreateMediationBodyModel) -> Optional[List[float]]:
    if form.cropping_rect_x is not None and form.cropping_rect_y is not None and form.cropping_rect_height is not None:
        return [form.cropping_rect_x, form.cropping_rect_y, form.cropping_rect_height]

    return None
