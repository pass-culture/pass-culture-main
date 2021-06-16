import base64
import logging

from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.offers import exceptions
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.repository as offers_repository
from pcapi.core.offers.validation import check_image
from pcapi.core.offers.validation import get_distant_image
from pcapi.flask_app import private_api
from pcapi.models import Offer
from pcapi.repository.offer_queries import get_offer_by_id
from pcapi.repository.offer_queries import get_offer_categories
from pcapi.repository.offer_queries import get_offer_sub_categories
from pcapi.routes.serialization.offers_recap_serialize import serialize_offers_recap_paginated
from pcapi.routes.serialization.offers_serialize import CategoriesResponseModel
from pcapi.routes.serialization.offers_serialize import CategoryResponseModel
from pcapi.routes.serialization.offers_serialize import GetOfferResponseModel
from pcapi.routes.serialization.offers_serialize import ImageBodyModel
from pcapi.routes.serialization.offers_serialize import ImageResponseModel
from pcapi.routes.serialization.offers_serialize import ListOffersQueryModel
from pcapi.routes.serialization.offers_serialize import ListOffersResponseModel
from pcapi.routes.serialization.offers_serialize import OfferResponseIdModel
from pcapi.routes.serialization.offers_serialize import PatchAllOffersActiveStatusBodyModel
from pcapi.routes.serialization.offers_serialize import PatchAllOffersActiveStatusResponseModel
from pcapi.routes.serialization.offers_serialize import PatchOfferActiveStatusBodyModel
from pcapi.routes.serialization.offers_serialize import PatchOfferBodyModel
from pcapi.routes.serialization.offers_serialize import PostOfferBodyModel
from pcapi.routes.serialization.offers_serialize import SubCategoryResponseModel
from pcapi.routes.serialization.thumbnails_serialize import CreateThumbnailBodyModel
from pcapi.routes.serialization.thumbnails_serialize import CreateThumbnailResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.workers.update_all_offers_active_status_job import update_all_offers_active_status_job


logger = logging.getLogger(__name__)
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.rest import load_or_404


@private_api.route("/offers", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListOffersResponseModel)  # type: ignore
def list_offers(query: ListOffersQueryModel) -> ListOffersResponseModel:
    paginated_offers = offers_api.list_offers_for_pro_user(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        type_id=query.type_id,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        name_keywords=query.name,
        status=query.status,
        creation_mode=query.creation_mode,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
    )

    return ListOffersResponseModel(__root__=serialize_offers_recap_paginated(paginated_offers))


@private_api.route("/offers/<offer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=GetOfferResponseModel)
def get_offer(offer_id: str) -> GetOfferResponseModel:
    offer = load_or_404(Offer, offer_id)
    return GetOfferResponseModel.from_orm(offer)


@private_api.route("/offers", methods=["POST"])
@login_required
@spectree_serialize(response_model=OfferResponseIdModel, on_success_status=201)  # type: ignore
def post_offer(body: PostOfferBodyModel) -> OfferResponseIdModel:
    offer = offers_api.create_offer(offer_data=body, user=current_user)
    return OfferResponseIdModel.from_orm(offer)


@private_api.route("/offers/active-status", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=204)  # type: ignore
def patch_offers_active_status(body: PatchOfferActiveStatusBodyModel) -> None:
    query = offers_repository.get_offers_by_ids(current_user, body.ids)
    offers_api.update_offers_active_status(query, body.is_active)


@private_api.route("/offers/all-active-status", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=None, on_success_status=202)
def patch_all_offers_active_status(
    body: PatchAllOffersActiveStatusBodyModel,
) -> PatchAllOffersActiveStatusResponseModel:
    filters = {
        "user_id": current_user.id,
        "is_user_admin": current_user.isAdmin,
        "offerer_id": body.offerer_id,
        "status": body.status,
        "venue_id": body.venue_id,
        "type_id": body.type_id,
        "name": body.name,
        "creation_mode": body.creation_mode,
        "period_beginning_date": body.period_beginning_date,
        "period_ending_date": body.period_ending_date,
    }
    update_all_offers_active_status_job.delay(filters, body.is_active)
    return PatchAllOffersActiveStatusResponseModel()


@private_api.route("/offers/<offer_id>", methods=["PATCH"])
@login_required
@spectree_serialize(response_model=OfferResponseIdModel)  # type: ignore
def patch_offer(offer_id: str, body: PatchOfferBodyModel) -> OfferResponseIdModel:
    offer = load_or_404(Offer, human_id=offer_id)
    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    offer = offers_api.update_offer(offer, **body.dict(exclude_unset=True))

    return OfferResponseIdModel.from_orm(offer)


@private_api.route("/offers/thumbnail-url-validation", methods=["POST"])
@login_required
@spectree_serialize(response_model=ImageResponseModel)
def validate_distant_image(body: ImageBodyModel) -> ImageResponseModel:
    errors = []

    try:
        image = get_distant_image(body.url)
        check_image(image)
        image_as_base64 = base64.b64encode(image)
        return ImageResponseModel(
            image=f'data:image/png;base64,{str(image_as_base64, encoding="utf-8")}', errors=errors
        )
    except (
        exceptions.FileSizeExceeded,
        exceptions.ImageTooSmall,
        exceptions.UnacceptedFileType,
        exceptions.FailureToRetrieve,
    ) as exc:
        logger.info("When validating image at: %s, this error was encountered: %s", body.url, exc.__class__.__name__)
        errors.append(exc.args[0])

    return ImageResponseModel(errors=errors)


@private_api.route("/offers/thumbnails/", methods=["POST"])
@login_required
@spectree_serialize(on_success_status=201, response_model=CreateThumbnailResponseModel)
def create_thumbnail(form: CreateThumbnailBodyModel) -> CreateThumbnailResponseModel:
    check_user_has_access_to_offerer(current_user, form.offerer_id)
    offer = get_offer_by_id(form.offer_id)

    image_as_bytes = form.get_image_as_bytes(request)
    thumbnail = offers_api.create_mediation(
        user=current_user,
        offer=offer,
        credit=form.credit,
        image_as_bytes=image_as_bytes,
        crop_params=form.crop_params,
    )

    return CreateThumbnailResponseModel(id=thumbnail.id)


@private_api.route("/offers/categories", methods=["GET"])
@login_required
@spectree_serialize(response_model=CategoriesResponseModel)
def get_categories() -> CategoriesResponseModel:
    return CategoriesResponseModel(
        categories=[CategoryResponseModel.from_orm(category) for category in get_offer_categories()],
        sub_categories=[SubCategoryResponseModel.from_orm(sub_category) for sub_category in get_offer_sub_categories()],
    )
